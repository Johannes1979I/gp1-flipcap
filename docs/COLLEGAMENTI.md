# Collegamenti elettrici - GP1 FlipCap V6

Schema completo nella figura B1 del manuale (`docs/manuale/F12_cablaggio.png`).

## Alimentazione

- 12 V del setup -> fusibile ritardato 1 A (sul cavo) -> presa DC sul coperchio del vano
- presa DC -> IN+ / IN- del convertitore LM2596
- **Regolare l'LM2596 a 5,00 V a vuoto, prima di collegare qualunque altra cosa.**
- OUT+ dell'LM2596 -> morsetto **+5 V**
- OUT- dell'LM2596 -> morsetto **GND**

## Bus +5 V e GND (due WAGO 221-415)

| Morsetto | Cosa ci va |
|---|---|
| +5 V | OUT+ LM2596, + della ULN2003, VCC dei sensori, + del condensatore da 1000 uF |
| GND | OUT- LM2596, - della ULN2003, GND dei sensori, - del condensatore, **GND del Nano** |

Il Nano si alimenta **solo dalla USB**: niente sul suo pin 5V. Il GND in comune
fra Nano e resto del circuito e' obbligatorio.

## Arduino Nano -> ULN2003

- D2 -> IN1
- D3 -> IN2
- D4 -> IN3
- D5 -> IN4

Il 28BYJ-48 si innesta nel connettore bianco a 5 poli della ULN2003. Un
condensatore da 100 nF sul + e sul - della ULN2003 filtra i disturbi del
motore, che senza possono far staccare la USB del Nano durante la corsa.

Se il motore vibra o cambia verso cambiando velocita', l'ordine delle fasi e'
sbagliato: si corregge nel firmware (`PHASE_ORDER`, prove al volo con `>K0`,
`>K1`, `>K2`) senza spostare i fili.

## Sensori Hall

Visti dal lato della faccia marcata, piedini in basso: VCC, GND, uscita.

- D6 <- uscita del sensore **CLOSED** (sede rivolta verso il bordo anteriore della scatola, lato tappo)
- D7 <- uscita del sensore **OPEN** (sede rivolta verso il fondo della scatola, lato tubo)
- VCC -> +5 V (mai i 12 V), GND -> GND, 100 nF fra VCC e GND vicino a ogni sensore

I sensori si cablano gia' montati nella piastra (sedi marcate C e O). Tutto
resta incassato sotto il piano su cui passa la bandierina: accanto a ogni sede
c'e' l'incavo del condensatore da 100 nF, e il canale porta piedini, saldature
e fili fino al bordo, da cui i fili escono di lato. Canale e incavo si
riempiono di colla a caldo, rasa al piano.

I due VCC e i due GND si uniscono vicino alla piastra: al vano arrivano
quattro fili (VCC, GND, CLOSED, OPEN) attraverso il passaggio fra riduttore e
vano. Il firmware usa le resistenze di pull-up interne del Nano: il sensore
deve portare il pin a GND quando il magnete gli passa davanti. L'A3144 e'
unipolare: se non scatta, gira il magnete.

## INDI / Ekos

Driver **Flip Flat** (`indi_flipflat`, in Auxiliary / Optec), 9600 baud,
ricerca automatica delle porte disattivata. Il firmware emula il product ID 98
(Remote Dust Cover): nessun pannello luminoso, solo il tappo. Park = chiudi,
Unpark = apri. Risponde con un solo LF: il driver legge 8 byte esatti.

Porta fissa su Linux: il CH340 del Nano non ha numero di serie, quindi si lega
alla presa USB con una regola udev (senza `RUN+=stty`, che resetterebbe il Nano):

```
SUBSYSTEM=="tty", KERNELS=="1-1.3", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="flipcap", MODE="0666"
```

`KERNELS` si legge con `udevadm info -a -n /dev/ttyUSBx`. In Ekos la porta
diventa `/dev/flipcap`. Nei Treni ottici assegna Flip Flat alla voce Dust cap:
la scheda Cattura apre il tappo prima dei Light e lo chiude prima di Dark e Bias.

La corsa dura circa 45 secondi: dopo 30 secondi il driver ripete il comando e
scrive *Parking cap timed out. Retrying* nel log. E' normale: il firmware
ignora il comando ripetuto e la corsa finisce regolarmente. Fra un Park e un
Unpark aspetta circa un minuto, altrimenti il timer rimasto del comando
precedente puo' invertire per qualche secondo la corsa.
