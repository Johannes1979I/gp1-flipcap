// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright (C) 2026 Johannes1979I
/*
  GP1 FlipCap V6 - firmware
  Tappo motorizzato a braccio singolo, ribaltamento di 270 gradi.

  Hardware: Arduino Nano (ATmega328P) + 28BYJ-48 5 V + scheda ULN2003
            + 2 sensori Hall A3144 (CLOSED e OPEN)
  Riduzione: riduttore interno del 28BYJ + treno stampato 15:1
  Protocollo: emula l'Alnitak Remote Dust Cover (product ID 98), quindi
              funziona con il driver INDI "Flip Flat" (indi_flipflat) e con
              qualunque software che parli il protocollo Alnitak.
  Seriale: 9600 8N1, comandi terminati da LF.

  COLLEGAMENTI
    D2 D3 D4 D5  -> IN1 IN2 IN3 IN4 della scheda ULN2003
    D10          <- uscita del sensore Hall CLOSED (tappo chiuso)
    D11          <- uscita del sensore Hall OPEN   (tappo parcheggiato)
    I sensori sono attivi bassi: il Nano usa le sue resistenze di pull-up.

  COME SI MUOVE
  - Full-step con due fasi sempre eccitate: e' il modo con piu' coppia.
  - Rampa di accelerazione in partenza, poi ~417 passi al secondo.
  - Ci si ferma sul sensore del lato verso cui si va. Il sensore vale solo
    se letto attivo quattro volte di fila (antirimbalzo).
  - Due protezioni se un sensore non scatta: un limite di passi (circa il
    5% oltre la corsa nominale) e un limite di tempo. In quel caso lo
    stato diventa 3 (errore) e il motore si spegne.
  - A motore fermo le bobine sono spente: non scaldano e non consumano.

  ALIMENTAZIONE
  - Il motore prende i 5 V dal convertitore, non dal Nano: sotto sforzo il
    28BYJ assorbe fino a ~250 mA e la porta USB del PC non va caricata.
  - Il GND del convertitore e quello del Nano devono essere in comune.
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
// un giro del braccio sono 30570 full-step, quindi i 270 gradi della corsa
// sono 22.928 passi: circa 55 secondi a regime.
static const uint32_t STEP_INTERVAL_US  = 2400;  // regime: ~417 full-step/s
static const uint32_t START_INTERVAL_US = 6000;  // partenza della rampa
static const uint32_t RAMP_STEPS        = 400;   // lunghezza rampa (~0,7 s)

// Con 270 gradi la corsa dura circa 55 s, cioe' PIU' dei 30 s dopo i quali il
// driver indi_flipflat rimanda il comando:
//     IEAddTimer(30000, parkTimeoutHelper, this);
//     LOG_WARN("Parking cap timed out. Retrying..."); ParkCap();
// Non e' un problema di per se': il comando ripetuto e' nella stessa direzione
// del movimento in corso e startMotion() lo ignora (vedi la guardia piu'
// sotto), quindi la corsa prosegue e finisce normalmente. Senza quella guardia
// il comando ripetuto azzererebbe moveSteps e raddoppierebbe di fatto il
// limite di extracorsa.
static const uint32_t MOVE_TIMEOUT_MS   = 70000; // deve stare sopra i 55 s di corsa

// Corsa nominale 270 gradi = 22.928 passi full-step (2038 x 15 x 0,75).
// Oltre il fine corsa il tappo non ha piu' niente da colpire: va semplicemente
// in appoggio sui supporti, quindi il limite serve solo a non far macinare il
// motore all'infinito se il sensore OPEN non scatta.
static const uint32_t MAX_MOVE_STEPS    = 24100;  // ~5% oltre i 22.928 nominali

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
  int8_t d = (direction > 0) ? 1 : -1;

  // Comando ripetuto nella stessa direzione mentre siamo gia' in movimento:
  // e' il retry del driver INDI dopo 30 s. Va ignorato, altrimenti azzera i
  // contatori di corsa e con loro il limite di extracorsa.
  if (moving && moveDirection == d) return;

  if (direction > 0 && openActive())   { stopMotion(2); return; }
  if (direction < 0 && closedActive()) { stopMotion(1); return; }

  moving = true;
  moveDirection = d;
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
  Serial.print(PRODUCT_ID); Serial.println("160");
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
