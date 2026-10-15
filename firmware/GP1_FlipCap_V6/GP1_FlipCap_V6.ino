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
  Seriale: 9600 8N1, comandi e risposte terminati da LF (solo LF: il driver
  indi_flipflat legge 8 byte, "*P98000\n", e un CR in piu' gli fa fallire il ping).

  COLLEGAMENTI
    D2 D3 D4 D5  -> IN1 IN2 IN3 IN4 della scheda ULN2003
    D6           <- uscita del sensore Hall CLOSED (tappo chiuso)
    D7           <- uscita del sensore Hall OPEN   (tappo parcheggiato)
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
static const uint8_t MOTOR_PINS[4] = {2, 3, 4, 5};   // D2..D5 -> IN1..IN4
// Ordine delle fasi: con 4 fili ci sono solo 3 ordini distinti e uno solo fa
// girare il 28BYJ pulito; gli altri lo fanno vibrare e perdere il verso.
// Si sceglie con >K0, >K1, >K2 (prove, fino al reset) e poi si fissa qui.
static const uint8_t PHASE_ORDERS[3][4] = {{0, 1, 2, 3}, {0, 2, 1, 3}, {0, 1, 3, 2}};
static const uint8_t PHASE_ORDER = 2;   // provato sul prototipo il 02/10/2026
static uint8_t phaseOrder = PHASE_ORDER;
static const uint8_t HALL_CLOSED_PIN = 6;
static const uint8_t HALL_OPEN_PIN   = 7;

// Mettere a true se dopo il montaggio OPEN/CLOSE risultano invertiti.
static const bool MOTOR_REVERSED = false;

// --- Budget di movimento -------------------------------------------------
// 28BYJ-48 con riduttore interno 1:64: 2038 full-step per giro d'uscita. Con
// il riduttore stampato 15:1 i 270 gradi di corsa sono
// MOTOR_STEPS_PER_REV x 15 x 0,75 = 22.928 passi, circa 46 s a 500 passi/s.
// Esiste anche il 28BYJ-48 1:16 (513 passi/giro): in quel caso mettere 513.
static const uint32_t MOTOR_STEPS_PER_REV = 2038;
static const uint32_t NOMINAL_STEPS     = MOTOR_STEPS_PER_REV * 15UL * 3UL / 4UL;  // 22.928
static const uint32_t STEP_INTERVAL_US  = 2000;  // regime: 500 full-step/s (provato: nessun passo perso)
static const uint32_t START_INTERVAL_US = 6000;  // partenza della rampa
static const uint32_t RAMP_STEPS        = 400;   // lunghezza rampa (~1,5 s)

// Il driver indi_flipflat rimanda il comando dopo 30 s:
//     IEAddTimer(30000, parkTimeoutHelper, this);
//     LOG_WARN("Parking cap timed out. Retrying..."); ParkCap();
// La corsa dura ~45 s, quindi succede. Non e' un problema: il comando ripetuto e' nella stessa direzione del
// movimento in corso e startMotion() lo ignora (vedi la guardia piu' sotto).
// Senza quella guardia azzererebbe moveSteps e raddoppierebbe il limite di
// extracorsa.
static const uint32_t MOVE_TIMEOUT_MS   = NOMINAL_STEPS / 400UL * 1000UL + 10000UL;

// Oltre il fine corsa il tappo non ha piu' niente da colpire: va semplicemente
// in appoggio sui supporti, quindi il limite serve solo a non far macinare il
// motore all'infinito se il sensore OPEN non scatta.
static const uint32_t MAX_MOVE_STEPS    = NOMINAL_STEPS + NOMINAL_STEPS / 20UL;  // +5%

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
static uint32_t runInterval = STEP_INTERVAL_US;   // regime, modificabile con >T (prove)

// Oltre-corsa: con il magnete 6x3 a 2,5 mm l'A3144 scatta ~17 gradi prima che
// il magnete gli sia sopra (misurato il 02/10/2026: ~19.950 passi fra i
// sensori invece di 22.928). Dopo lo scatto il motore fa ancora OVERRUN_*_STEPS
// passi, cosi' il tappo arriva davvero in chiusura e sugli appoggi.
// 1 grado = 30570 / 360 = ~85 passi. Separati per verso: tarati sul tappo
// montato il 14/10/2026 (in apertura il tappo restava alto: +10 gradi).
// Si regolano al volo con >Exxxx (apertura) e >Fxxxx (chiusura).
static const uint32_t OVERRUN_OPEN_STEPS  = 2250;
static const uint32_t OVERRUN_CLOSE_STEPS = 1400;
static uint32_t runOverrunOpen  = OVERRUN_OPEN_STEPS;
static uint32_t runOverrunClose = OVERRUN_CLOSE_STEPS;
static uint32_t overrunLeft = 0;
static uint8_t  overrunTarget = 0;                 // stato finale: 1 chiuso, 2 aperto
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
    digitalWrite(MOTOR_PINS[PHASE_ORDERS[phaseOrder][i]], FULLSTEP[p & 3][i] ? HIGH : LOW);
}

void motorOff()
{
  for (uint8_t i = 0; i < 4; ++i) digitalWrite(MOTOR_PINS[i], LOW);
}

// Filtro dei finecorsa: un sensore vale attivo solo se letto basso di continuo
// per HALL_FILTER campioni, uno ogni HALL_SAMPLE_US (20 ms in tutto). Il
// magnete resta davanti al sensore per secondi; i disturbi che il motore
// induce sui fili dei sensori durano microsecondi e vengono scartati. Con il
// vecchio antirimbalzo da 4 letture, a 500 passi/s il tappo si fermava dopo
// ~58 gradi credendo di essere arrivato.
static const uint32_t HALL_SAMPLE_US = 200;
static const uint8_t  HALL_FILTER    = 100;
static uint8_t hallCount[2] = {0, 0};          // 0 CLOSED, 1 OPEN
static uint32_t lastHallUs = 0;

static void sampleHall()
{
  uint32_t now = micros();
  if ((uint32_t)(now - lastHallUs) < HALL_SAMPLE_US) return;
  lastHallUs = now;
  const uint8_t pins[2] = {HALL_CLOSED_PIN, HALL_OPEN_PIN};
  for (uint8_t i = 0; i < 2; ++i) {
    if (digitalRead(pins[i]) == LOW) { if (hallCount[i] < 255) ++hallCount[i]; }
    else hallCount[i] = 0;
  }
}

bool closedActive() { return hallCount[0] >= HALL_FILTER; }
bool openActive()   { return hallCount[1] >= HALL_FILTER; }

// Intervallo corrente: rampa lineare da START_INTERVAL_US a runInterval.
static uint32_t rampInterval(uint32_t n)
{
  if (n >= RAMP_STEPS) return runInterval;
  uint32_t span = START_INTERVAL_US - runInterval;
  return START_INTERVAL_US - (span * n) / RAMP_STEPS;
}

void determineInitialState()
{
  uint32_t t0 = millis();
  while (millis() - t0 < 30) sampleHall();      // riempie il filtro
  bool c = closedActive(), o = openActive();
  if (c && !o) coverStatus = 1;
  else if (o && !c) coverStatus = 2;
  else coverStatus = 0;
}

void stopMotion(uint8_t state)
{
  moving = false;
  overrunTarget = 0;
  overrunLeft = 0;
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
  overrunTarget = 0;
  overrunLeft = 0;
  stepInterval = START_INTERVAL_US;
  lastStepUs = micros();
}

void serviceMotion()
{
  if (!moving) return;

  if (overrunTarget == 0) {
    uint8_t hit = 0;
    if (moveDirection > 0 && openActive())   hit = 2;
    if (moveDirection < 0 && closedActive()) hit = 1;
    if (hit) {
      uint32_t ov = (hit == 2) ? runOverrunOpen : runOverrunClose;
      if (ov == 0) { stopMotion(hit); return; }
      overrunTarget = hit;                     // sensore trovato: ancora ov passi
      overrunLeft = ov;
    }
  } else if (overrunLeft == 0) {
    stopMotion(overrunTarget);
    return;
  }

  if ((millis() - moveStartMs) >= MOVE_TIMEOUT_MS + 5000UL ||
      moveSteps >= MAX_MOVE_STEPS + runOverrunOpen + runOverrunClose) {
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
  if (overrunLeft) --overrunLeft;
  stepInterval = rampInterval(moveSteps);
}

void replySimple(char op)
{
  Serial.print('*'); Serial.print(op);
  if (PRODUCT_ID < 10) Serial.print('0');
  Serial.print(PRODUCT_ID); Serial.print("000"); Serial.print('\n');
}

void replyStatus()
{
  Serial.print("*S");
  if (PRODUCT_ID < 10) Serial.print('0');
  Serial.print(PRODUCT_ID);
  Serial.print(moving ? '1' : '0');
  Serial.print('0');
  Serial.print((char)('0' + coverStatus)); Serial.print('\n');
}

void replyVersion()
{
  Serial.print("*V");
  if (PRODUCT_ID < 10) Serial.print('0');
  Serial.print(PRODUCT_ID); Serial.print("160"); Serial.print('\n');
}

void replyBrightness()
{
  Serial.print("*J");
  if (PRODUCT_ID < 10) Serial.print('0');
  Serial.print(PRODUCT_ID); Serial.print("000"); Serial.print('\n');
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
    // Diagnostica, fuori dal protocollo Alnitak (INDI non li manda mai):
    //   >N      passi fatti dall'ultima corsa      -> *N<passi>
    //   >Txxxx  intervallo a regime in us, fino al prossimo reset -> *T<us>
//   >Kn     ordine delle fasi 0..2, fino al prossimo reset     -> *K<n>
//   >Exxxx  oltre-corsa in apertura, fino al reset  -> *E<passi>  (>E? lo legge)
//   >Fxxxx  oltre-corsa in chiusura, fino al reset  -> *F<passi>  (>F? lo legge)
    case 'N': Serial.print("*N"); Serial.print(moveSteps); Serial.print('\n'); break;
    case 'T': {
      long us = atol(cmd + 2);
      if (!moving && us >= 1000 && us <= (long)START_INTERVAL_US) runInterval = (uint32_t)us;
      Serial.print("*T"); Serial.print(runInterval); Serial.print('\n');
      break;
    }
    case 'E':
    case 'F': {
      uint32_t *ov = (cmd[1] == 'E') ? &runOverrunOpen : &runOverrunClose;
      long n = atol(cmd + 2);
      if (!moving && n >= 0 && n <= 5000 && cmd[2] >= '0' && cmd[2] <= '9') *ov = (uint32_t)n;
      Serial.print('*'); Serial.print(cmd[1]); Serial.print(*ov); Serial.print('\n');
      break;
    }
    case 'K': {
      int k = cmd[2] - '0';
      if (!moving && k >= 0 && k <= 2) phaseOrder = (uint8_t)k;
      Serial.print("*K"); Serial.print(phaseOrder); Serial.print('\n');
      break;
    }
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
  sampleHall();
  serviceMotion();
}
