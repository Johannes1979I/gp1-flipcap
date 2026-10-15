# Binario precompilato

`GP1_FlipCap_V6.ino.hex` corrisponde al sorgente in
`firmware/GP1_FlipCap_V6/`, compilato per **Arduino Nano (ATmega328P)**.

```
arduino-cli 1.3.1 - core arduino:avr 1.8.6 - avr-gcc 7.3.0-atmel3.6.1-arduino7
fqbn: arduino:avr:nano:cpu=atmega328
flash: 4384 byte su 30720 (14%)
RAM:    304 byte su  2048 (14%)
0 errori, 0 warning nello sketch
```

Serve a chi vuole caricare il firmware senza installare l'IDE Arduino, per
esempio con avrdude:

```
avrdude -c arduino -p m328p -P COM3 -b 115200 -U flash:w:GP1_FlipCap_V6.ino.hex:i
```

Dove avrdude non c'e' (per esempio sul Raspberry dell'osservatorio) basta
Python 3: `tools/stk500.py` parla direttamente con il bootloader del Nano,
scrive e rilegge pagina per pagina. Prima scollega il driver INDI dalla porta.

```
python3 tools/stk500.py /dev/flipcap firmware/build/GP1_FlipCap_V6.ino.hex
```

Se il Nano ha il bootloader vecchio (quasi tutti i cloni con CH340), usa
`-b 57600`. Al posto di `COM3` metti la porta del tuo Nano
(`/dev/ttyUSB0` su Linux).

**Se modifichi il firmware, ricompila e rigenera questo file**, altrimenti
resta indietro rispetto al sorgente:

```
arduino-cli compile --fqbn arduino:avr:nano --output-dir firmware/build firmware/GP1_FlipCap_V6
```
