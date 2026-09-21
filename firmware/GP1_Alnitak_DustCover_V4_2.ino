// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright (C) 2026 Johannes1979I
/*
  GP1 FlipCap V4.2 - mono motore / mono braccio
  Hardware: Arduino Nano/Uno + 1x 28BYJ-48 5V + 1x ULN2003 + 2x Hall A3144
  Riduzione: riduttore interno 28BYJ + riduttore stampato 15:1
  Protocollo: emula Alnitak Remote Dust Cover per indi_flipflat (product ID 98)
  Seriale: 9600 8N1, comandi terminati da LF

  --------------------------------------------------------------------------
  DIFFERENZE RISPETTO ALLA V4.1  (motivazioni in CHANGELOG_V4.2.md)
  --------------------------------------------------------------------------
  1. FULL-STEP 2 FASI ATTIVE al posto dell'half-step.
     L'half-step alterna 1 e 2 fasi eccitate: la coppia media e' piu' bassa
     di quella disponibile. Con 2 fasi sempre attive si guadagna circa il
     40% di coppia, e a parita' di velocita' angolare la frequenza di passo
     si dimezza (piu' facile per il 28BYJ). La corsa dura uguale.
  2. RAMPA DI ACCELERAZIONE.
     La V4.1 partiva di colpo a 833 passi/s da fermo, e lo faceva proprio
     nell'istante di coppia resistente massima (tappo chiuso, tubo allo
     zenit: ~0,22 N*m). Uno stepper in quelle condizioni perde passi.
  3. CORSA RIDOTTA A 90 GRADI (era 105).
     A 105 gradi il disco del tappo passava a 0,65 mm dalla scatola.
  4. ANTIRIMBALZO sui finecorsa Hall.
  5. Budget tempi ricalcolato: corsa nominale ~19 s contro i 27 s di
     timeout, quindi con margine reale sotto i 30 s del driver INDI.

  --------------------------------------------------------------------------
  IMPORTANTE
  - Alimentare ULN2003 / motore da un 5 V esterno regolato (>= 1 A).
  - Collegare il GND del 5 V esterno al GND dell'Arduino.
  - Non alimentare il 28BYJ dalla USB / rail 5 V del Nano.
  - I sensori Hall sono attesi ATTIVI BASSI con INPUT_PULLUP.
  - Imposta la posizione di park di Ekos con il tubo NON allo zenit:
    la coppia resistente passa da ~0,22 N*m a ~0,04 N*m.
*/

#include <Arduino.h>

static const uint32_t BAUD_RATE = 9600;
static const uint8_t MOTOR_PINS[4] = {2, 3, 4, 5};
static const uint8_t HALL_CLOSED_PIN = 10;
static const uint8_t HALL_OPEN_PIN   = 11;

// Mettere a true se dopo il montaggio OPEN/CLOSE risultano invertiti.
static const bool MOTOR_REVERSED = false;

// --- Budget di movimento -------------------------------------------------
// 28BYJ-48: 2038 full-step per giro d'uscita. Con la riduzione stampata 15:1
// un giro del braccio sono 30570 full-step, quindi 90 gradi ~= 7642 step.
static const uint32_t STEP_INTERVAL_US  = 2400;  // regime: ~417 full-step/s
static const uint32_t START_INTERVAL_US = 6000;  // partenza della rampa
static const uint32_t RAMP_STEPS        = 400;   // lunghezza rampa (~0,7 s)
static const uint32_t MOVE_TIMEOUT_MS   = 27000; // sotto i 30 s di INDI FlipFlat

// LIMITE DI SICUREZZA MECCANICA, non una semplice tolleranza.
// Se il sensore OPEN non scatta, questo e' l'unico freno prima che il tappo
// vada a sbattere sulla scatola. Luce disco-scatola misurata sulle mesh:
//     -90 gradi (7642 passi) -> 8,47 mm    <- corsa nominale
//     -95 gradi (8067 passi) -> 5,38 mm
//    -100 gradi (8491 passi) -> 1,72 mm
//    -105 gradi (8916 passi) -> 0,77 mm    <- collisione
// 8100 passi = -95,4 gradi, cioe' ~5,2 mm di luce anche in avaria.
// NON alzarlo. La corsa reale resta 7642 passi qualunque sia la
// registrazione della piastra sensori: le asole ruotano CLOSED e OPEN
// insieme, e i due sensori sono a 90 gradi esatti per costruzione.
static const uint32_t MAX_MOVE_STEPS    = 8100;

static const uint8_t PRODUCT_ID = 98;

// Codifica stato INDI FlipFlat in *S98xyz:
//   x motore: 0 fermo / 1 in moto
//   y luce:   sempre 0 (product 98 = dust cover, niente pannello)
//   z tappo:  0 intermedio, 1 chiuso, 2 aperto, 3 timeout/errore
static uint8_t coverStatus = 0;
static bool moving = false;
static int8_t moveDirection = 0;   // +1 OPEN, -1 CLOSE
static uint32_t moveStartMs = 0;
static uint32_t moveSteps = 0;
static uint32_t lastStepUs = 0;
static uint32_t stepInterval = STEP_INTERVAL_US;
static uint8_t phase = 0;

// Full-step, 2 fasi sempre eccitate.
static const uint8_t FULLSTEP[4][4] = {
  {1, 1, 0, 0},
  {0, 1, 1, 0},
  {0, 0, 1, 1},
  {1, 0, 0, 1}
};

static char rx[16];
static uint8_t rxLen = 0;

void setMotorPhase(uint8_t p)
{
  for (uint8_t i = 0; i < 4; ++i)
    digitalWrite(MOTOR_PINS[i], FULLSTEP[p & 3][i] ? HIGH : LOW);
}

void motorOff()
{
  for (uint8_t i = 0; i < 4; ++i) digitalWrite(MOTOR_PINS[i], LOW);
}

// Antirimbalzo: il finecorsa vale solo se letto basso 4 volte di fila.
static bool hallActive(uint8_t pin)
{
  for (uint8_t i = 0; i < 4; ++i) {
    if (digitalRead(pin) != LOW) return false;
    delayMicroseconds(60);
  }
  return true;
}

bool closedActive() { return hallActive(HALL_CLOSED_PIN); }
bool openActive()   { return hallActive(HALL_OPEN_PIN); }

// Intervallo corrente: rampa lineare da START_INTERVAL_US a STEP_INTERVAL_US.
static uint32_t rampInterval(uint32_t n)
{
  if (n >= RAMP_STEPS) return STEP_INTERVAL_US;
  uint32_t span = START_INTERVAL_US - STEP_INTERVAL_US;
  return START_INTERVAL_US - (span * n) / RAMP_STEPS;
}

void determineInitialState()
{
  delay(20);
  bool c = closedActive(), o = openActive();
  if (c && !o) coverStatus = 1;
  else if (o && !c) coverStatus = 2;
  else coverStatus = 0;
}

void stopMotion(uint8_t state)
{
  moving = false;
  moveDirection = 0;
  coverStatus = state;
  motorOff();
}

void startMotion(int8_t direction)
{
  if (direction > 0 && openActive())   { stopMotion(2); return; }
  if (direction < 0 && closedActive()) { stopMotion(1); return; }

  moving = true;
  moveDirection = (direction > 0) ? 1 : -1;
  coverStatus = 0;
  moveStartMs = millis();
  moveSteps = 0;
  stepInterval = START_INTERVAL_US;
  lastStepUs = micros();
}

void serviceMotion()
{
  if (!moving) return;

  if (moveDirection > 0 && openActive())   { stopMotion(2); return; }
  if (moveDirection < 0 && closedActive()) { stopMotion(1); return; }

  if ((millis() - moveStartMs) >= MOVE_TIMEOUT_MS || moveSteps >= MAX_MOVE_STEPS) {
    stopMotion(3);
    return;
  }

  uint32_t now = micros();
  if ((uint32_t)(now - lastStepUs) < stepInterval) return;
  lastStepUs += stepInterval;

  int8_t d = moveDirection;
  if (MOTOR_REVERSED) d = -d;
  phase = (uint8_t)((phase + d + 4) & 3);
  setMotorPhase(phase);

  ++moveSteps;
  stepInterval = rampInterval(moveSteps);
}

void replySimple(char op)
{
  Serial.print('*'); Serial.print(op);
  if (PRODUCT_ID < 10) Serial.print('0');
  Serial.print(PRODUCT_ID); Serial.println("000");
}

void replyStatus()
{
  Serial.print("*S");
  if (PRODUCT_ID < 10) Serial.print('0');
  Serial.print(PRODUCT_ID);
  Serial.print(moving ? '1' : '0');
  Serial.print('0');
  Serial.println((char)('0' + coverStatus));
}

void replyVersion()
{
  Serial.print("*V");
  if (PRODUCT_ID < 10) Serial.print('0');
  Serial.print(PRODUCT_ID); Serial.println("120");
}

void replyBrightness()
{
  Serial.print("*J");
  if (PRODUCT_ID < 10) Serial.print('0');
  Serial.print(PRODUCT_ID); Serial.println("000");
}

void handleCommand(const char *cmd)
{
  if (cmd[0] != '>' || strlen(cmd) < 2) return;
  switch (cmd[1]) {
    case 'P': replySimple('P'); break;
    case 'O': startMotion(+1); replySimple('O'); break;
    case 'C': startMotion(-1); replySimple('C'); break;
    case 'S': replyStatus(); break;
    case 'V': replyVersion(); break;
    case 'J': replyBrightness(); break;
    case 'B': replySimple('B'); break;
    case 'L': replySimple('L'); break;
    case 'D': replySimple('D'); break;
    default: break;
  }
}

void serviceSerial()
{
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      rx[rxLen] = '\0';
      if (rxLen) handleCommand(rx);
      rxLen = 0;
    } else if (rxLen < sizeof(rx) - 1) {
      rx[rxLen++] = c;
    } else {
      rxLen = 0;
    }
  }
}

void setup()
{
  for (uint8_t i = 0; i < 4; ++i) pinMode(MOTOR_PINS[i], OUTPUT);
  motorOff();
  pinMode(HALL_CLOSED_PIN, INPUT_PULLUP);
  pinMode(HALL_OPEN_PIN, INPUT_PULLUP);
  Serial.begin(BAUD_RATE);
  determineInitialState();
}

void loop()
{
  serviceSerial();
  serviceMotion();
}
