# GP1 FlipCap V4.2 - montaggio

Questo documento parte dal presupposto che **housing, cover e i tre ingranaggi
siano gia' stampati dalla V4.1**: quelle geometrie non sono cambiate.

---

## 0. Cosa stampare adesso

| pezzo | stato | volume | note |
|---|---|---|---|
| `housing.stl` | **gia' buono** | 251,5 cm3 | identico alla V4.1 a meno di 4 fori da trapanare (vedi sotto) |
| `cover.stl` | **gia' buono** | 33,7 cm3 | invariato |
| `output_gear.stl` | **gia' buono** | 15,8 cm3 | invariato |
| `compound_gear.stl` | **gia' buono** | 4,9 cm3 | invariato |
| `motor_pinion.stl` | **gia' buono** | 0,5 cm3 | invariato |
| `magnet_flag.stl` | gia' buono | 1,9 cm3 | il pezzo V4.1 funziona: incolla il magnete. Il nuovo ha solo la tasca aperta e il foro grano accorciato |
| `motor_bracket.stl` | **DA STAMPARE** | 33,8 cm3 | pezzo nuovo, senza di questo il motore non si monta |
| `mono_arm.stl` | **DA RISTAMPARE** | 54,6 cm3 | il vecchio compenetra la scatola |
| `lid_backplate.stl` | **DA RISTAMPARE** | 8,5 cm3 | nuovo schema a 4 fori |
| `hall_plate.stl` | **DA STAMPARE** | 3,5 cm3 | sostituisce i due `hall_holder` |

Materiale e parametri: PETG o ASA, layer 0,20 mm, 4-5 perimetri, 30-40% infill
per staffa/braccio/contropiastra. La `hall_plate` in piano, 3 perimetri.

Orientamento consigliato:
- `motor_bracket`: appoggiata sulla faccia grande della piastra motore, la
  flangia in verticale. Supporti solo sotto la flangia.
- `mono_arm`: mozzo sul piatto, piastra tappo in alto. Servono supporti sotto
  la piastra.
- `hall_plate`: faccia piatta sul piatto, nessun supporto.

---

## 1. Quattro fori da fare sull'housing gia' stampato

Sono tutti Ø3,4 mm. **I pezzi stampati fanno da dima**: appoggiali in
posizione e segna attraverso i loro fori. Le quote qui sotto servono solo come
controllo.

### 1a. Due fori sul TETTO della scatola (per la staffa motore)

Il tetto e' la faccia larga in alto, 72 x 74 mm.

- Traccia una linea a **37 mm dal bordo anteriore** (quello rivolto al tappo).
- Su quella linea, due punti a **16 mm** e **48 mm** dal bordo sinistro
  (il lato dove esce l'albero del braccio).
- Fora Ø3,4 passante attraverso i 4 mm di parete.

### 1b. Due fori sulla PARETE SINISTRA (per la piastra sensori)

Prendi come riferimento il **centro del boss del cuscinetto 626ZZ**, il
tondo sporgente da cui esce l'albero.

- Foro 1: **8,7 mm verso il bordo inferiore** e **26,6 mm verso il bordo
  anteriore** rispetto al centro del boss.
- Foro 2: **26,6 mm verso il bordo superiore** e **8,7 mm verso il bordo
  posteriore** rispetto al centro del boss.
- Fora Ø3,4 passante.

I quattro fori della V4.1 per i vecchi `hall_holder` restano inutilizzati:
tappali con un pezzetto di nastro nero o una goccia di colla, cosi' non entra
luce/polvere.

Dopo aver forato la piastra motore staccata che ti e' uscita dalla stampa
della V4.1: e' scarto, buttala.

---

## 2. Ordine di montaggio

L'ordine conta: alcune cose non sono piu' raggiungibili dopo.

1. **Piastra sensori Hall.** Va per prima, perche' i dadi delle sue viti
   stanno dentro la scatola e dopo il montaggio degli ingranaggi non ci arrivi
   piu'. Infila gli A3144 nelle due tasche (faccia marcata verso l'esterno,
   cioe' verso il centro della scatola), salda i fili, passali lungo il bordo
   inferiore. Fissa con due M3x16 + rondella dall'esterno e dado interno,
   lasciando le asole al centro della corsa.
2. **Cuscinetti.** 626ZZ nella sede della parete sinistra (si inserisce
   dall'esterno) e 626ZZ nel boss del coperchio.
3. **Albero 6 x 100 mm** attraverso i due cuscinetti. Deve sporgere ~19 mm dal
   lato sinistro (per il braccio) e ~3 mm dal lato coperchio.
4. **Bandierina magnete** sull'albero, a X=99 cioe' **11 mm dalla faccia
   interna della parete sinistra**. Magnete rivolto verso i sensori.
   Controlla a mano che sfiori senza toccare: sono 2,9 mm di traferro.
5. **Ingranaggio di uscita 70T** sull'albero, grano M3 stretto.
6. **625ZZ** nell'ingranaggio composto (lato 42T) e composto sul perno M5,
   con rondella PTFE contro la parete sinistra.
7. **Staffa motore.** Inseriscila spingendola contro soffitto, parete sinistra
   e fra i due boss superiori del coperchio. Si posiziona da sola. Inserti M3
   a caldo nella flangia, poi due M3x10 dall'esterno del tetto.
8. **28BYJ-48** sulla staffa: corpo attraverso il foro grande, orecchie
   appoggiate alla faccia destra, due M3x12 nelle asole. **Non stringere
   ancora.**
9. **Pignone 14T** sull'albero del motore. Foro leggermente stretto: allargalo
   con una lima a D finche' entra a pressione. Deve arrivare a filo della
   faccia della staffa.
10. **Registra l'ingranamento**: spingi il motore nelle asole finche' il
    14/42 ingrana senza gioco eccessivo e senza forzare, poi stringi le due
    M3x12. Fai girare tutto a mano: il treno deve ruotare libero.
11. **Prova elettrica a scatola aperta.** Alimenta, manda `>O000` e `>C000` da
    un terminale seriale a 9600 baud e guarda che i due Hall scattino. Se non
    scattano, gira il magnete di 180 gradi nella sua tasca. Registra le asole
    della piastra sensori finche' CLOSED scatta esattamente a tappo chiuso.
12. **Chiudi il coperchio** con le 4 M3.
13. **Monobraccio** sull'estremita' sinistra dell'albero. Il mozzo e' a
    morsetto: infila fino a lasciare **2 mm di luce dal boss del cuscinetto**,
    poi stringi la M3 del morsetto.
14. **Tappo.** Fora il disco Forex sui 4 punti usando la piastra del braccio
    come dima, metti i dadi M4 nelle sedi esagonali sotto le piazzole e serra
    con le M4x16 dal lato cielo, con la `lid_backplate` sopra e rondelle
    larghe. Non strizzare: il Forex si schiaccia.
15. **Fissaggio all'OTA** con le due cinghie e 3-4 mm di EVA fra sella e tubo.

---

## 3. Prima di fissare all'OTA: misura il tubo

Il modello assume `ota_d = 362 mm`. **Misura la circonferenza con un metro
flessibile nel punto di fissaggio e dividi per pi greco.**

- tubo reale **< 362**: la sella balla. Riempi con EVA piu' spessa (3-4 mm).
  Non e' un problema.
- tubo reale **> 363,2**: la sella non si appoggia. Vai di carta abrasiva
  all'interno, oppure rigenera l'housing con il valore giusto
  (`openscad -o stl/housing.stl -D 'part="housing"' -D 'ota_d=XXX'
  gp1_flipcap_V4_2.scad`) e ristampa.

**Posizione angolare.** La sella copre un arco di soli ~43 gradi, centrato a
34 gradi dalla verticale. Puoi ruotare liberamente tutto il gruppo attorno al
tubo: la cinematica e' invariante. Sul Quattro 300P focheggiatore e cercatore
stanno vicino alla bocca del tubo, esattamente dove va la sella: scegli il
lato libero prima di stringere.

**Bilanciamento.** Il gruppo pesa 400-500 g in punta a un tubo da 1200 mm.
Rifai il bilanciamento e verifica che le fascette non slittino.

---

## 4. Ekos

Driver `Alnitak Remote Dust Cover` / `Flip Flat` (`indi_flipflat`).
Product ID 98 = dust cover: **niente pannello flat**, il tappo e' solo un
tappo. Park = chiuso, Unpark = aperto.

**Imposta la posizione di park con il tubo lontano dallo zenit.** Vedi la
sezione 7 del CHANGELOG: allo zenit il margine di coppia e' 1,4x, con il tubo
orizzontale e' 8x.

---

## 5. Riverificare la geometria dopo una modifica

Se cambi un parametro nello SCAD, rigenera gli STL e rilancia:

    python docs/verifica_collisioni.py

Controlla braccio-housing, staffa-housing, disco-housing e braccio-tubo su
tutta la corsa, direttamente sulle mesh che vanno in stampa. Richiede numpy e
scipy.
