# Collegamenti elettrici - GP1 FlipCap V4.2

Invariati rispetto alla V4.1: il firmware V4.2 usa gli stessi pin.

## Arduino Nano -> ULN2003
- D2 -> IN1
- D3 -> IN2
- D4 -> IN3
- D5 -> IN4

## Finecorsa Hall
- D10 -> uscita sensore CLOSED (quello a ore 12 sulla piastra, angolo 0)
- D11 -> uscita sensore OPEN (quello a 90 gradi)
- VCC Hall -> 5 V
- GND Hall -> GND comune
- 100 nF fra VCC e GND di ciascun sensore, il piu' vicino possibile

Il firmware usa `INPUT_PULLUP`: il sensore deve portare il pin LOW quando il
magnete e' presente. L'A3144 e' un interruttore Hall UNIPOLARE: risponde a una
sola polarita'. Se non scatta, gira il magnete di 180 gradi nella sua tasca.

## Alimentazione
- 12 V astronomici -> fusibile 1-1.5 A -> LM2596
- Regolare LM2596 a 5.0 V PRIMA di collegare l'elettronica
- 5 V LM2596 -> ULN2003 + sensori
- GND LM2596 -> GND ULN2003 -> GND Arduino
- Arduino collegato ad AstroArch via USB

Non alimentare il 28BYJ-48 dalla porta USB / dal rail 5 V del Nano.

## INDI / Ekos
Driver `Alnitak Remote Dust Cover` / `Flip Flat` (`indi_flipflat`).
Il firmware emula il product ID 98 = Remote Dust Cover: **non c'e' pannello
flat**, solo il tappo. Park = chiuso, Unpark = aperto.

**Imposta la posizione di park con il tubo lontano dallo zenit.** Allo zenit la
coppia resistente al distacco e' ~0,22 N*m contro ~0,32 N*m disponibili
(margine 1,4x); con il tubo orizzontale scende a ~0,04 N*m (margine 8x).
