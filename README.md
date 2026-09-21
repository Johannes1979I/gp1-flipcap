# GP1 FlipCap V4.2

Tappo motorizzato mono-motore / mono-braccio per **Sky-Watcher Quattro 300P
f/4**, comandato da Ekos/INDI tramite emulazione del protocollo Alnitak
Remote Dust Cover.

> **Se arrivi dalla V4.1: leggi prima [CHANGELOG_V4.2.md](CHANGELOG_V4.2.md).**
> La V4.1 aveva tre difetti bloccanti (supporto motore staccato dalla scatola,
> braccio che compenetrava l'housing su tutta la corsa, tappo che sbatteva
> sulla scatola in apertura). Housing, coperchio e ingranaggi gia' stampati
> restano validi; braccio, contropiastra e supporti sensori vanno rifatti e
> serve un pezzo nuovo, la staffa motore.

---

## Architettura

- 1 x 28BYJ-48 5 V + ULN2003
- 1 solo braccio esterno, nessuna cerniera sul lato opposto
- riduzione stampata 15:1 interamente chiusa nella scatola, in aggiunta al
  riduttore interno del 28BYJ
- albero di uscita 6 mm su due cuscinetti 626ZZ
- due Hall A3144 su una piastra unica, magnete 6x3 su bandierina solidale
  all'albero
- scatola fissata al tubo con sella curva parametrica e due cinghie

### Riduzione (invariata dalla V4.1)

modulo 0,8 - motore 14T -> 42T (3:1) -> 14T -> 70T (5:1) = **15:1**
Interassi: 22,4 mm e 33,6 mm.

### Corsa

Da 0 a **-90 gradi** (la V4.1 diceva -105, ma a -105 il tappo toccava la
scatola: luce 0,65 mm). A -90 gradi la luce minima e' 7,86 mm e il bordo
vicino del tappo si trova 68 mm oltre il raggio del tubo, quindi
completamente fuori dal fascio.

### Tappo

Ø374 nominali. **Forex / PVC espanso 1,5 mm.** Non usare 2 mm e tanto meno un
disco PETG pieno: il margine di coppia e' 1,4x con il tubo allo zenit
(vedi CHANGELOG sezione 7).

---

## File

```
MANUALE_MONTAGGIO_V4.2.pdf     manuale illustrato passo-passo (18 pagine)
gp1_flipcap_V4_2.scad          modello parametrico, tutti i pezzi
CHANGELOG_V4.2.md              cosa e' cambiato dalla V4.1 e perche', con i numeri
MONTAGGIO.md                   cosa stampare, i 4 fori da fare, ordine di montaggio
LICENSE / NOTICE               CERN-OHL-S v2
firmware/
  GP1_Alnitak_DustCover_V4_2.ino
docs/
  BOM_meccanica.csv
  BOM_elettronica.csv
  COLLEGAMENTI.md
  verifica_collisioni.py       verifica geometrica automatica sugli STL
  VERIFICA_COLLISIONI.txt      output della verifica
  genera_dae.py                ricostruisce il .dae dell'assieme dagli STL
  genera_figure_manuale.py     render e disegni quotati del manuale
  genera_manuale_pdf.py        compone il PDF del manuale
  manuale/                     figure del manuale
  GP1_V4_2_assieme_SketchUp.dae   assieme completo, importabile in SketchUp
  SHA256SUMS.txt               checksum di tutti i file del progetto
  render/                      confronto visivo V4.1 -> V4.2
stl/
  housing.stl  cover.stl  motor_bracket.stl
  output_gear.stl  compound_gear.stl  motor_pinion.stl
  mono_arm.stl  lid_backplate.stl  hall_plate.stl  magnet_flag.stl
  accessori/
    GP1_electronics_box_MINI.stl   scatola per Nano+ULN2003+buck, non
                                   parametrica, non generata dallo SCAD.
                                   La mesh ha 8 isole a facce coincidenti:
                                   si stampa, ma non e' watertight.
```

## Manuale

[MANUALE_MONTAGGIO_V4.2.pdf](MANUALE_MONTAGGIO_V4.2.pdf) - 18 pagine, con
elenco pezzi, disegni quotati delle forature, schema di cablaggio, montaggio
meccanico ed elettrico passo-passo, taratura, diagnostica.

Si rigenera con:

```
python docs/genera_figure_manuale.py
python docs/genera_manuale_pdf.py
```

## Render di confronto

In `docs/render/`, a coppie PRIMA (V4.1) / DOPO (V4.2):

| file | cosa mostra |
|---|---|
| `1_chiuso_*` | assieme completo a tappo chiuso |
| `2_aperto_*` | assieme in apertura (-105 vs -90 gradi) |
| `3_braccio_*` | il braccio da vicino, senza tubo e tappo: nel PRIMA la flangia entra nello spigolo della scatola |
| `4_interno_*` | interno della scatola senza coperchio: nel PRIMA si vede la piastra motore sospesa in aria |

---

## Rigenerare gli STL

OpenSCAD 2021.01 o piu' recente, con la libreria MCAD (inclusa
nell'installazione):

```
openscad -o stl/housing.stl -D 'part="housing"' gp1_flipcap_V4_2.scad
```

Parti disponibili: `housing`, `cover`, `motor_bracket`, `motor_pinion`,
`compound_gear`, `output_gear`, `mono_arm`, `lid_backplate`, `hall_plate`,
`magnet_flag`.

Per i render dell'assieme ci sono tre interruttori: `show_ota`, `show_lid`,
`show_cover`.

## Riverificare la geometria

```
python docs/verifica_collisioni.py
```

Campiona le mesh STL reali e controlla, su tutta la corsa: integrita' dei
solidi, braccio vs housing, staffa vs housing e ingranaggi, disco tappo vs
housing, braccio vs tubo, piastra sensori vs housing e bandierina.
Richiede numpy e scipy.

---

## Prima di uscire in cielo

1. **Misura il tubo.** `ota_d=362` e' un valore di progetto. Circonferenza
   diviso pi greco, nel punto di fissaggio.
2. **Orienta il gruppo** dove non da' fastidio a focheggiatore e cercatore:
   la sella copre solo 43 gradi di arco e puoi ruotarla liberamente.
3. **Prova il treno a mano** a scatola aperta, prima di alimentare.
4. **Prova i due Hall a scatola aperta.** L'A3144 e' unipolare: se non scatta,
   gira il magnete.
5. **Park di Ekos lontano dallo zenit.** Allo zenit la coppia resistente al
   distacco e' ~0,23 N*m contro ~0,32 N*m disponibili; con il tubo orizzontale
   scende a ~0,04 N*m.
6. **Ribilancia la montatura**: 400-500 g in punta al tubo.

---

## Licenza

**CERN Open Hardware Licence Version 2 - Strongly Reciprocal** (CERN-OHL-S v2).
Testo completo in [LICENSE](LICENSE), sintesi in [NOTICE](NOTICE).

Puoi usare, modificare e ridistribuire il progetto, anche commercialmente. Se
distribuisci un prodotto basato su questi file o una versione modificata dei
file stessi, devi rendere disponibile la sorgente completa corrispondente sotto
la stessa licenza.

## Avvertenza

Progetto amatoriale fornito **cos&igrave; com'&egrave;, senza garanzia**. Le
verifiche geometriche in `docs/VERIFICA_COLLISIONI.txt` valgono per il modello
parametrico con i valori di default: se cambi parametri, rilancia la verifica.
Il margine di coppia del 28BYJ-48 &egrave; stretto (1,4x con il tubo allo
zenit): leggi la sezione 7 del CHANGELOG prima di costruire.

Chi monta questo meccanismo su un telescopio &egrave; responsabile della
propria verifica meccanica ed elettrica.
