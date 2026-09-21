# Binario precompilato

`GP1_Alnitak_DustCover_V4_2.ino.hex` corrisponde al sorgente in
`firmware/GP1_Alnitak_DustCover_V4_2/`, compilato per **Arduino Nano
(ATmega328P)**.

```
arduino-cli 1.3.1 - core arduino:avr 1.8.6 - avr-gcc 7.3.0-atmel3.6.1-arduino7
fqbn: arduino:avr:nano
flash: 3594 byte su 30720 (11%)
RAM:    261 byte su  2048 (12%)
0 errori, 0 warning nello sketch
```

Serve solo a chi vuole flashare senza installare l'IDE Arduino, per esempio
con avrdude:

```
avrdude -c arduino -p m328p -P COM3 -b 115200 -U flash:w:GP1_Alnitak_DustCover_V4_2.ino.hex:i
```

Se il Nano ha il bootloader vecchio, usa `-b 57600`.

**Se modifichi il firmware, ricompila e rigenera questo file**, altrimenti
resta indietro rispetto al sorgente:

```
arduino-cli compile --fqbn arduino:avr:nano --output-dir firmware/build firmware/GP1_Alnitak_DustCover_V4_2
```
