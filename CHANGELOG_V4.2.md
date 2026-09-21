# GP1 FlipCap - da V4.1 a V4.2

Tutti i numeri qui sotto sono misurati sulle mesh STL, non stimati.
Lo script che li produce e' `docs/verifica_collisioni.py`; il suo output e'
in `docs/VERIFICA_COLLISIONI.txt` e si rigenera con:

    python docs/verifica_collisioni.py

---

## 1. BLOCCANTE - la piastra di supporto motore era staccata dalla scatola

**V4.1.** `motor_mount_plate_raw()` era una `cube([3.2,48,58])` messa in
`union()` dentro `body_raw()`, ma non toccava nessuna parete della cavita':

```
housing.stl  isole = 2
  corpo principale  251,5 cm3
  ISOLA             6,6 cm3   X[132,4 .. 135,6]  Y[244 .. 292]  Z[-54 .. 4]
  distanza minima fra isola e corpo = 12,45 mm
```

Lo stesso log di OpenSCAD lo diceva: `docs/openscad_housing.log` riportava
`Volumes: 3` (= due solidi separati) mentre tutti gli altri pezzi riportavano
`Volumes: 2`. Risultato pratico: **nessun punto dove avvitare il 28BYJ-48**;
lo slicer ha stampato la lastrina per aria o l'ha scartata.

**V4.2.** La piastra esce dall'housing e diventa un pezzo a se':
`motor_bracket()`. Si posiziona da sola contro tre riferimenti della scatola
gia' stampata:

| riferimento | vincola |
|---|---|
| soffitto della cavita' (Y=306) | quota Y, cioe' l'interasse motore-composto |
| parete sinistra (X=88) | posizione assiale del pignone |
| i due boss superiori del coperchio (Z=-50,5 e +0,5) | rotazione |

Due viti M3 dall'esterno del tetto la bloccano. I fori del motore sono
**asolati di +/-2 mm in Y**, cosi' l'ingranamento 14/42 si registra a mano e
non dipende piu' dalle tolleranze di stampa.

Verifica: compenetrazione staffa-housing = 0 punti; luce dal composto 1,00 mm,
dall'ingranaggio di uscita 3,00 mm, dal pignone 8,07 mm.

---

## 2. Il monobraccio compenetrava l'housing su tutta la corsa

**V4.1.** Con `arm_x = 76` (cioe' `box_x-box_depth_x/2-8`), campionando la
mesh `mono_arm.stl` in 17.795 punti e ruotandola contro `housing.stl`:

| angolo | punti in compenetrazione | dove |
|---|---|---|
| 0 gradi (chiuso) | 733 | mozzo dentro il boss del 626ZZ; flangia dentro lo spigolo scatola (fino a X=91) |
| -52 gradi | 382 | mozzo + nervature dentro la parete sinistra |
| -105 gradi (aperto) | 822 | mozzo + nervature + flangia |

Tre cause distinte:

- il mozzo `x_cyl(13,14)` occupava X 69..83, il boss del cuscinetto X 80..90:
  **3 mm di interferenza coassiale permanente**, il braccio non si infilava;
- le nervature arrivavano a X 87,5 contro una parete che sta a X 84..88;
- la flangia del tappo, larga 30 mm e centrata sul mozzo, arrivava a X 91.

**V4.2.** Braccio ridisegnato:

- `arm_x` 76 -> **70**, `arm_w` 18 -> **16**: mozzo a X 62..78, cioe' 2 mm di
  luce dal boss. Serve un albero **6 x 100 mm** (la BOM V4.1 diceva 95).
- Vincolo di progetto esplicito: nessun punto del braccio oltre X globale 82
  sotto quota Z 3. Il corpo del braccio non entra mai nel volume X>=84 dove
  vive la scatola.
- Il braccio sale in verticale restando a Y~212 (dove il raggio dall'asse
  ottico e' 223 mm, quindi sempre fuori dal tubo) e solo dopo si sposta verso
  il centro del tappo. Cosi' scavalca l'anello frontale dell'OTA.

Verifica: 0 punti in compenetrazione su tutta la corsa, luce minima 2,00 mm.

---

## 3. Il disco del tappo sbatteva contro la scatola in apertura

**V4.1**, luce minima fra il disco Ø374 e l'housing, misurata sulla mesh:

| angolo | luce |
|---|---|
| 0 gradi | 8,68 mm |
| -90 gradi | 8,59 mm |
| -95 gradi | 5,67 mm |
| -100 gradi | 3,18 mm |
| **-105 gradi (apertura nominale)** | **0,65 mm** |

Il contatto avviene sul bordo del disco a raggio ~184 mm contro lo spigolo
anteriore-sinistro della scatola. Con 0,65 mm teorici, su un pannello Forex da
374 mm che flette di parecchi millimetri, sbatte.

`docs/VERIFICA_GEOMETRICA.txt` della V4.1 dichiarava "nessun punto campionato
del disco entra nel volume del box": formalmente vero, ma senza margine.

**V4.2.** Due modifiche:

- `open_angle` -105 -> **-90 gradi**;
- piano del tappo da Z=+12 a **Z=+17** (`arm_dz=42`), che allontana il disco
  dalla faccia anteriore della scatola e lascia spazio sotto la piastra del
  braccio.

Luce minima su tutta la corsa: **7,86 mm** (a -90 gradi), minimo 10,10 mm da
chiuso. A -90 gradi il bordo vicino del tappo e' 68 mm oltre il raggio del
tubo: completamente fuori dal fascio, non si perde nulla rispetto ai 105.

Le asole della nuova piastra sensori ruotano CLOSED e OPEN **insieme**, di
+/-7 gradi: servono a registrare esattamente l'istante di scatto del CLOSED.
La corsa fra i due sensori resta 90 gradi esatti, perche' le due sedi sono a
90 gradi per costruzione.

---

## 4. Attacco del tappo

**V4.1.** 2 viti M4 a 20 mm di interasse su una flangia 30 x 52 mm, per
reggere un disco di 374 mm. In torsione attorno all'asse del braccio il tappo
era libero di ballare.

**V4.2.** 4 viti M4 ai vertici di un quadrilatero di **61 x 33 mm**, su una
piastra da 10 mm di spessore. Dadi M4 in sedi esagonali sotto le piazzole,
viti dal lato cielo attraverso la contropiastra. `lid_backplate` rifatta con
lo stesso schema fori.

Le viti stanno a raggio 158 e 176 mm dall'asse ottico: il bordo del diaframma
utile e' a 152,5 mm, quindi le rondelle M4 restano appena fuori dall'apertura.

Mozzo del braccio: **morsetto a pinza** (taglio + vite M3 passante con dado)
invece del solo grano. Un grano M3 su un albero da 6 mm che porta tutto il
carico del tappo e' il punto debole classico di questi meccanismi.

---

## 5. Sensori Hall - l'asse magnetico era ruotato di 90 gradi

**V4.1.** Nella `magnet_flag()` la tasca del magnete era `x_cyl(...)`, quindi
poli lungo X. Nel `hall_holder()` la tasca del sensore era
`cube([9,2.4,5.2])`, cioe' con lo spessore 2,4 mm lungo **Y**: la faccia
sensibile dell'A3144 guardava in Y e leggeva la componente sbagliata del campo.
In piu' il supporto (X 88..95) e la bandierina (X 90,5..95,5) si
compenetravano di 5 mm.

**V4.2.** I due supporti separati diventano una **piastra unica**
`hall_plate()`:

- i due A3144 sono alloggiati nello spessore della piastra, con la faccia
  sensibile ortogonale a X, affacciata al polo del magnete;
- le posizioni a 0 e 90 gradi sono ricavate per costruzione, non da regolare;
- due asole ad arco centrate sull'asse albero permettono di ruotare tutto il
  gruppo di +/-7 gradi per registrare l'istante di scatto;
- la piastra e' distanziata di 2,6 mm dalla parete per scavalcare il boss del
  626ZZ, che sporge in cavita' fino a X=90;
- bandierina spostata a X=99, tasca del magnete aperta verso i sensori.

Traferro magnete-sensore risultante: **~2,9 mm**. Un 6x3 N35 a 2,9 mm rende
circa 1300 G contro i ~250 G di soglia dell'A3144: margine ampio.
Verifica: compenetrazione 0, luce meccanica piastra-bandierina 2,90 mm.

L'A3144 resta un interruttore Hall **unipolare**: se non scatta, gira il
magnete di 180 gradi.

---

## 6. Firmware

| | V4.1 | V4.2 |
|---|---|---|
| pilotaggio | half-step (8 fasi) | **full-step 2 fasi attive** (4 fasi) |
| coppia relativa | riferimento | **~+40%** |
| passi per 1 giro uscita | 4076 x 15 = 61.140 | 2038 x 15 = 30.570 |
| passi per la corsa | 17.832 (105 gradi) | 7.642 (90 gradi) |
| intervallo di passo | 1200 us (833 passi/s) | 2400 us (417 passi/s) |
| rampa | assente | **da 6000 a 2400 us in 400 passi** |
| durata corsa | ~21,4 s | **~19 s** |
| timeout | 27 s (margine 5,6 s) | 27 s (**margine 8 s**) |
| antirimbalzo Hall | no | si', 4 letture concordi |

La rampa non e' un dettaglio: la coppia resistente e' massima **nell'istante
in cui parte l'apertura**, e li' la V4.1 chiedeva al 28BYJ di passare da fermo
a 833 passi/s.

### 6b. `MAX_MOVE_STEPS` e' un limite meccanico, non una tolleranza

Se il sensore OPEN non scatta, il conteggio passi e' l'unica cosa che impedisce
al tappo di andare a sbattere. Luce disco-scatola misurata oltre la corsa
nominale:

| angolo | passi | luce disco | luce braccio |
|---|---|---|---|
| -90 (nominale) | 7.642 | 7,86 mm | 2,00 mm |
| -95 | 8.067 | 4,76 mm | 2,00 mm |
| -100 | 8.492 | **2,06 mm** | 1,31 mm |
| -105 | 8.916 | **0,82 mm** | 0,47 mm |

Percio' `MAX_MOVE_STEPS = 8100` (= -95,4 gradi, ~5 mm di luce anche in
avaria). **Non va alzato.** La corsa reale resta 7.642 passi qualunque sia la
registrazione della piastra sensori: le asole ruotano CLOSED e OPEN insieme e
i due sensori sono a 90 gradi esatti per costruzione.

Nell'altro verso non serve protezione: chiudendo oltre lo zero il tappo va in
appoggio sull'anello frontale del tubo, che fa da fermo meccanico.

---

## 7. Margine di coppia - da tenere d'occhio

Non e' un difetto introdotto dalla V4.1, ma un vincolo del progetto che vale
la pena scrivere nero su bianco.

- Tappo Forex 1,5 mm Ø374 ~ 91 g, piu' contropiastra e viti ~ **105 g**,
  baricentro a **212 mm** dalla cerniera.
- Coppia resistente = m x g x braccio, e il braccio e' l'**offset in Y** del
  baricentro rispetto alla cerniera. Quindi:

| condizione | coppia resistente |
|---|---|
| tubo allo zenit, tappo chiuso | **~0,23 N*m** |
| tubo allo zenit, tappo a -90 gradi | ~0,04 N*m |
| tubo orizzontale, tappo chiuso | **~0,04 N*m** |

- Coppia disponibile: 28BYJ-48 a ~12 rpm di uscita ~30 mN*m, x15, con
  rendimento 0,72 su due stadi stampati = **~0,32 N*m**.

Margine 1,4x allo zenit, 8x all'orizzonte. Da -78 gradi in poi la gravita'
aiuta l'apertura, quindi il tappo resta appoggiato aperto senza caricare il
finecorsa.

**Conseguenza operativa: imposta il park di Ekos con il tubo lontano dallo
zenit.** E usa Forex da 1,5 mm, non 2 mm.

---

## 8. Igiene del progetto

Sistemato anche:

- `gp1_flipcap_V4.scad` e `gp1_flipcap_V4_1.scad` erano **identici byte per
  byte**: due nomi per lo stesso file. Ora ce n'e' uno solo.
- I commenti `// 19.2` e `// 28.8` su `stage1_center`/`stage2_center` erano i
  valori della V4 (12/36/60); i calcoli davano 22,4 e 33,6.
- `README_V4_IT.md` descriveva ancora la trasmissione 12/36/60 e STL
  chiamati `12T`/`60T`.
- `START_HERE.txt` e `FILE_MANIFEST.txt` rimandavano a tre PNG
  (`assembly_closed.png`, `assembly_open.png`, `gearbox_internal.png`) che
  **non esistevano**. Ora ci sono i render in `docs/render/`.
- `SHA256SUMS.txt` aveva 9 checksum su 10 non corrispondenti (era il manifest
  della V4 con gli STL della V4.1): inutilizzabile per verificare cosa si e'
  stampato. Rigenerato.
- Nella `magnet_flag()` il foro del grano Ø2,7 arrivava a z=14 e **sfondava
  nella tasca del magnete**: accorciato a 20 mm.
- BOM: albero da 95 -> 100 mm; aggiunta la viteria che mancava (viti motore,
  viti staffa, morsetto braccio, 4 viti tappo invece di 2).
- `stl/GP1_electronics_box_MINI.stl` non era documentato da nessuna parte:
  spostato in `stl/accessori/` e citato nel README. Attenzione: quella mesh ha
  8 isole a facce coincidenti (colonnine appoggiate esattamente sul fondo).
  Si stampa, ma non e' watertight.
