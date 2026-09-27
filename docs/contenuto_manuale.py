#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) 2026 Johannes1979I
"""
GP1 FlipCap V6 - testo del manuale di costruzione.

Separato da genera_manuale_pdf.py (che contiene solo l'impaginazione) per
poter lavorare sul testo senza toccare la grafica. I numeri che dipendono
dalla geometria (luci, volumi) arrivano da docs/VERIFICA_COLLISIONI.txt
tramite il dizionario `dati` costruito in genera_manuale_pdf.py.

Il manuale e' generico: chi lo legge costruisce tutto da zero.
"""


def build(ui, dati):
    banner, step, table, callout = ui.banner, ui.step, ui.table, ui.callout
    figure, figure_pair, h2, p, sp = ui.figure, ui.figure_pair, ui.h2, ui.p, ui.sp
    mm, CW, PageBreak, story = ui.mm, ui.CW, ui.PageBreak, ui.story
    Paragraph, S, Spacer = ui.Paragraph, ui.S, ui.Spacer
    code = ui.code

    # ---------------------------------------------------------- copertina
    story.append(Spacer(1, 16 * mm))
    story.append(Paragraph("GP1 FlipCap V6", S["cover1"]))
    sp(6)
    story.append(Paragraph("Manuale di costruzione", S["cover2"]))
    sp(2)
    story.append(Paragraph("Tappo motorizzato a ribaltamento per telescopi newtoniani,<br/>"
                           "comandato da INDI / Ekos", S["cover2"]))
    sp(8)
    figure("F01_assieme_chiuso.png", 150 * mm)
    sp(2)
    callout("Cosa stai per costruire.",
            "Un tappo antipolvere che si apre e si chiude da solo quando lo comanda il "
            "software di acquisizione. Un solo motore e un solo braccio: aprendosi, il "
            "tappo ruota di 270 gradi, scavalca la scatola e si <b>posa sul tubo</b>, "
            "cos&igrave; il vento non lo fa vibrare. Riduttore ed elettronica stanno in "
            "un'unica scatola stampata, fissata al tubo con due cinghie a strappo. Il "
            "progetto &egrave; parametrico: diametro del tubo, del tappo e posizioni si "
            "cambiano in un file di testo.", kind="info")
    story.append(PageBreak())

    # ------------------------------------------------------------- indice
    banner("Indice")
    table([
        ["Capitolo", "Contenuto"],
        ["<b>0. Il progetto in breve</b>",
         "come funziona, pezzi da stampare, viteria, elettronica, attrezzi, "
         "materiale del tappo, adattamento al proprio tubo"],
        ["<b>A. Preparazione</b>", "pulizia dei pezzi, prove a secco, inserti filettati"],
        ["<b>B. Elettronica</b>", "alimentazione, vassoio, cablaggio, firmware, prova a banco"],
        ["<b>C. Riduttore</b>",
         "cuscinetti, sensori, albero, motore, ingranaggi, taratura, chiusura"],
        ["<b>D. Sul telescopio</b>", "cinghie, braccio, tappo, appoggi, collaudo, Ekos"],
        ["<b>Appendici</b>",
         "comandi seriali, coppia e peso del tappo, diagnostica, limiti verificati, "
         "rigenerare i pezzi, chi ha gi&agrave; pezzi di versioni precedenti"],
    ], [42 * mm, CW - 42 * mm])
    callout("L'ordine dei passi conta.",
            "Alcune viti non si raggiungono pi&ugrave; dopo aver montato altri pezzi, e "
            "i sensori si tarano girando l'albero a mano, cosa possibile solo "
            "<b>prima</b> di montare il pignone del motore. Segui i passi nell'ordine in "
            "cui sono scritti: elettronica a banco, poi riduttore, poi telescopio.",
            kind="info")
    sp(3)
    callout("Questo progetto &egrave; open hardware.",
            "Licenza CERN-OHL-S v2: puoi usarlo, modificarlo e ridistribuirlo, anche "
            "commercialmente, a patto di pubblicare la sorgente delle tue modifiche con "
            "la stessa licenza. &Egrave; fornito cos&igrave; com'&egrave;, <b>senza alcuna "
            "garanzia</b>: chi lo monta sul proprio telescopio &egrave; responsabile delle "
            "proprie verifiche.", kind="ok")
    story.append(PageBreak())

    # ================================================ 0. IL PROGETTO IN BREVE
    banner("0. Il progetto in breve",
           "come funziona e cosa serve prima di cominciare")

    h2("0.1 &nbsp;Come funziona")
    figure("F03_corsa.png", CW, "FIG. 0.1 - vista di fianco, in scala. Il tappo ruota di 270 gradi "
           "attorno all'albero e si posa sul tubo; la linea tratteggiata &egrave; la traiettoria "
           "del suo bordo esterno")
    p("Il tappo &egrave; avvitato a un braccio che sta sull'<b>albero di uscita</b> di "
      "un piccolo riduttore. Un motore passo-passo 28BYJ-48 muove l'albero attraverso "
      "una riduzione stampata 15:1. A tappo chiuso il disco sta davanti alla bocca del "
      "tubo; aprendo, ruota di 270 gradi, passa sopra la scatola e si appoggia su due "
      "supporti fissati al tubo. Due sensori a effetto Hall leggono un magnete che gira "
      "con l'albero e dicono al firmware quando fermarsi.")
    sp(3)
    table([
        ["Voce", "Valore"],
        ["Motore", "28BYJ-48 da 5 V con scheda driver ULN2003"],
        ["Riduzione", "riduttore interno del 28BYJ + treno stampato 15:1 "
                      "(modulo 0,8: 14T-&gt;42T, 14T-&gt;70T)"],
        ["Corsa", "270 gradi in circa 55 secondi"],
        ["Albero di uscita", "acciaio 6 x 100 mm su due cuscinetti 626ZZ"],
        ["Finecorsa", "2 sensori Hall A3144 su una piastra, magnete 6 x 3 mm su una "
                      "bandierina solidale all'albero"],
        ["Elettronica", "Arduino Nano, ULN2003, convertitore LM2596, tutto nel vano "
                        "della scatola"],
        ["Alimentazione", "12 V (quelli del setup), circa 0,3 A durante il movimento, "
                          "zero a motore fermo"],
        ["Fissaggio", "due selle curve e due cinghie a strappo da 25 mm"],
        ["Software", "protocollo Alnitak (product ID 98), driver INDI "
                     "<i>indi_flipflat</i>; compatibile con qualunque programma che "
                     "comandi un Alnitak"],
        ["Misure di default", "tubo &Oslash;362 mm, tappo &Oslash;374 mm: entrambe "
                              "parametriche, vedi 0.8"],
    ], [34 * mm, CW - 34 * mm])
    callout("Non &egrave; un pannello per i flat.",
            "Il product ID 98 &egrave; un <i>dust cover</i>: copre e scopre, e basta. "
            "Non ha una luce. Il tappo inoltre resta a circa 12 mm dalla bocca del "
            "tubo: protegge dalla polvere e dalla rugiada ma non &egrave; a tenuta di "
            "luce. Per i dark copri il tubo come fai adesso, o vedi il consiglio del "
            "passo D4.", kind="info")

    h2("0.2 &nbsp;Pezzi da stampare")
    figure("F04_pezzi.png", CW, "FIG. 0.2 - i pezzi da stampare, in scala fra loro, come vanno sul piatto")
    p("Tutti i file sono in <font face='Courier'>stl/</font> e sono <b>gi&agrave; "
      "orientati per la stampa</b>: aprili nello slicer e non ruotarli. Materiale "
      "totale circa <b>%s cm3</b>, cio&egrave; intorno ai <b>%s g</b> di PETG con i "
      "parametri qui sotto." % (dati["vol_tot"], dati["peso_tot"]))
    sp(3)
    table([
        ["File", "Q.t&agrave;", "Cos'&egrave;", "Stampa"],
        ["housing", "1", "scatola: riduttore, vano elettronica, due selle",
         "sul piatto la parete sinistra. Senza supporti; se la stampante fatica sugli "
         "sbalzi, supporti solo sotto le due selle"],
        ["cover", "1", "coperchio del riduttore, con la sede del secondo 626ZZ",
         "faccia esterna sul piatto"],
        ["motor_bracket", "1", "staffa del motore", "gi&agrave; orientata, nessun supporto"],
        ["hall_plate", "1", "piastra dei due sensori", "sedi dei sensori sul piatto"],
        ["spacers", "1", "cinque distanziali (s1, s2, s3, c1, c2)",
         "in piedi; stampali al 100% di riempimento"],
        ["bay_lid", "1", "coperchio del vano, con presa 12 V e foro USB",
         "faccia esterna sul piatto"],
        ["bay_tray", "1", "vassoio delle schede", "colonnine verso l'alto"],
        ["output_gear", "1", "ingranaggio di uscita 70T", "sul lato senza mozzo"],
        ["compound_gear", "1", "ingranaggio composto 42T + 14T", "42T sul piatto"],
        ["motor_pinion", "1", "pignone del motore 14T", "sul lato senza mozzo"],
        ["magnet_flag", "1", "bandierina del magnete", "in piano"],
        ["mono_arm", "1", "braccio del tappo",
         "fianco del mozzo sul piatto; supporti sotto la piastra del tappo"],
        ["cap_backplate", "1", "contropiastra del tappo", "in piano"],
        ["cap_rest", "<b>2</b>", "appoggi del tappo sul tubo",
         "faccia d'appoggio sul piatto"],
    ], [27 * mm, 11 * mm, 58 * mm, CW - 96 * mm])
    callout("L'housing &egrave; grande.",
            "Occupa %s x %s mm sul piatto e %s mm di altezza: ci sta su un piatto da "
            "220 x 220 mm. Conviene lanciarlo per primo e stampare il resto mentre "
            "gira." % (dati["housing_x"], dati["housing_y"], dati["housing_z"]),
            kind="info")

    h2("0.3 &nbsp;Materiale e impostazioni")
    table([
        ["Gruppo", "Materiale", "Layer", "Perimetri", "Riempimento"],
        ["housing, coperchi, staffa, braccio, appoggi", "PETG o ASA", "0,20 mm", "4", "30-40%"],
        ["ingranaggi", "PETG, ASA o PA", "0,12-0,16 mm", "5 o pi&ugrave;", "50-100%"],
        ["piastra sensori, bandierina, contropiastra, vassoio", "PETG o ASA", "0,20 mm", "3", "30%"],
        ["distanziali", "PETG o ASA", "0,15 mm", "tutti", "100%"],
    ], [60 * mm, 28 * mm, 22 * mm, 20 * mm, CW - 130 * mm])
    callout("Il PLA non va bene.",
            "La scatola sta al sole del pomeriggio prima della sessione e il motore "
            "scalda: il PLA si deforma gi&agrave; a 55-60 gradi. Usa PETG o ASA.")

    h2("0.4 &nbsp;Viteria e minuteria")
    table([
        ["Q.t&agrave;", "Componente", "Dove va"],
        ["1", "Albero in acciaio &Oslash;6 x 100 mm (tondo rettificato)", "albero di uscita"],
        ["2", "Cuscinetto 626ZZ (6 x 19 x 6)", "parete della scatola e coperchio"],
        ["1", "Cuscinetto 625ZZ (5 x 16 x 5)", "dentro il 42T del composto"],
        ["1", "Vite M5 x 80 + 2 rondelle + dado autobloccante M5", "perno del composto"],
        ["1", "Rondella PTFE o nylon M5, spessore 1 mm", "fra distanziale c1 e composto"],
        ["10", "Inserti filettati a caldo M3 (lunghezza 4-6 mm)",
         "4 coperchio riduttore, 4 coperchio vano, 2 staffa motore"],
        ["4", "Viti M3 x 8 a testa svasata piana", "coperchio del vano"],
        ["8", "Viti M3 x 8 a testa cilindrica",
         "4 coperchio del riduttore, 2 staffa del motore (dal fondo della scatola), "
         "2 orecchie del motore (si filettano da sole nella plastica)"],
        ["2", "Viti M3 x 16 + rondelle + dadi", "piastra sensori, dalla parete sinistra"],
        ["1", "Vite M3 x 25 + dado", "morsetto del mozzo del braccio"],
        ["2", "Grani M3 x 5", "bandierina e ingranaggio di uscita"],
        ["4", "Viti M4 x 16 + rondelle larghe + dadi M4", "tappo sul braccio"],
        ["4", "Viti autofilettanti 1,7 x 6 (o M1,6)", "Arduino Nano sulle colonnine"],
        ["6-8", "Viti autofilettanti M3 x 6", "ULN2003 e LM2596 sulle colonnine"],
        ["1", "Magnete al neodimio 6 x 3 mm (N35 o pi&ugrave;)", "bandierina"],
        ["4", "Cinghie a strappo (velcro) 25 mm x 1,4 m",
         "2 per la scatola, 2 per gli appoggi"],
        ["1", "Gomma EVA (crepla) adesiva 2 mm, un foglio A4", "selle e appoggi"],
        ["1", "Lastra per il tappo, almeno 380 x 380 mm", "vedi 0.7"],
    ], [13 * mm, 78 * mm, CW - 91 * mm])

    h2("0.5 &nbsp;Elettronica")
    table([
        ["Q.t&agrave;", "Componente", "Nota"],
        ["1", "Arduino Nano (ATmega328P, 5 V)", "va bene un clone con CH340"],
        ["1", "Motore 28BYJ-48 <b>5 V</b> con scheda ULN2003", "di solito si vendono insieme"],
        ["1", "Convertitore LM2596 (modulo 43 x 21 mm)", "12 V -&gt; 5,0 V"],
        ["2", "Sensore Hall A3144 (o AH3144E)", "interruttore unipolare, contenitore TO-92"],
        ["2", "Condensatore ceramico 100 nF", "uno per sensore"],
        ["1", "Condensatore elettrolitico 1000 uF 10-16 V", "sul +5 V"],
        ["1", "Presa DC 5,5 x 2,1 da pannello, tipo DC-022B", "foro da 8 mm"],
        ["1", "Portafusibile volante con fusibile ritardato 1 A", "sul cavo dei 12 V"],
        ["2", "Morsetti a leva WAGO 221-415 (5 vie)", "bus +5 V e bus GND"],
        ["-", "Cavetti Dupont femmina-femmina, filo 0,25-0,5 mm2, guaina termorestringente", ""],
        ["1", "Cavo USB per il Nano", "fino al PC o al mini PC del setup"],
    ], [13 * mm, 88 * mm, CW - 101 * mm])

    h2("0.6 &nbsp;Attrezzi")
    p("Saldatore e stagno &middot; saldatore con punta per inserti (o la punta normale "
      "pulita) &middot; chiavi a brugola 1,5 / 2 / 2,5 / 3 mm &middot; chiave da 5,5, 7 "
      "e 8 mm &middot; piccola lima piatta e lima tonda &middot; cutter e riga "
      "&middot; multimetro &middot; metro da sarto &middot; trapano con punta da 4,5 mm "
      "(fori del tappo) &middot; un PC con l'IDE Arduino.")

    h2("0.7 &nbsp;Il tappo: che materiale usare")
    p("&Egrave; la scelta che pesa di pi&ugrave; su tutto il progetto. Durante la "
      "corsa il braccio deve sollevare il tappo tenendolo a circa 27 cm dall'albero, e "
      "il 28BYJ-48 con la riduzione stampata eroga circa <b>0,32 N&middot;m</b>. Il "
      "<b>margine</b> in tabella &egrave; il rapporto fra coppia disponibile e coppia "
      "richiesta nel punto peggiore della corsa, compresi braccio, contropiastra e "
      "viti: sotto 1 il tappo non si alza, sotto 1,3 funziona ma senza riserva.")
    sp(3)
    table([
        ["Disco &Oslash;374", "Massa del disco", "Coppia richiesta", "Margine", "Giudizio"],
        ["<b>Polipropilene alveolare 3 mm</b>", "53 g", "0,21 N&middot;m", "<b>1,6</b>",
         "<b>consigliato</b>: leggero, rigido, impermeabile, si taglia col cutter"],
        ["Depron / XPS 6 mm", "26 g", "0,14 N&middot;m", "2,4",
         "il pi&ugrave; leggero, ma si ammacca con un dito"],
        ["Forex 1,5 mm", "91 g", "0,30 N&middot;m", "1,1", "al limite; flette molto"],
        ["Forex 2 mm", "121 g", "0,38 N&middot;m",
         "<font color='#c0392b'><b>0,85</b></font>", "<font color='#c0392b'>non si alza</font>"],
        ["Forex 3 mm", "181 g", "0,54 N&middot;m",
         "<font color='#c0392b'><b>0,60</b></font>", "<font color='#c0392b'>non si alza</font>"],
    ], [44 * mm, 24 * mm, 26 * mm, 18 * mm, CW - 112 * mm],
        align={1: "CENTER", 2: "CENTER", 3: "CENTER"})
    callout("Usa il polipropilene alveolare da 3 mm.",
            "&Egrave; il materiale dei cartelli elettorali e delle scatole da trasloco "
            "in plastica (Polionda, Akylux): pesa circa 480 g al metro quadro, non teme "
            "l'umidit&agrave; e si taglia con il cutter. Orienta i canali interni lungo la "
            "linea che va dall'attacco del braccio al bordo opposto: &egrave; la "
            "direzione in cui il disco lavora a flessione. Il Forex, anche sottile, con "
            "questo motore non funziona: serve un motore pi&ugrave; forte (NEMA 14 o 17).",
            kind="ok")
    sp(2)
    p("Qualunque cosa aggiungi al tappo (guarnizioni, maniglie, adesivi) va contata: "
      "10 g sul bordo del disco tolgono circa 0,1 al margine.", "small")

    h2("0.8 &nbsp;Adattare il progetto al proprio tubo")
    p("Gli STL sono generati per un tubo da <b>362 mm</b> di diametro esterno (Sky-Watcher "
      "Quattro 300) e un tappo da <b>374 mm</b>. Misura il tuo tubo nel punto dove "
      "andr&agrave; la scatola: gira attorno al tubo un metro da sarto, leggi la "
      "circonferenza e dividi per 3,1416. Su un tubo grande &egrave; molto pi&ugrave; "
      "preciso del calibro.")
    sp(3)
    table([
        ["Differenza dal valore di default", "Cosa fare"],
        ["da -3 a +1 mm", "niente: l'EVA sotto le selle assorbe la differenza"],
        ["oltre", "rigenera <b>housing</b> e <b>cap_rest</b> con il tuo diametro "
                  "(appendice E). Il tappo va tagliato circa 12 mm pi&ugrave; grande del tubo"],
    ], [58 * mm, CW - 58 * mm])

    # =========================================================== PARTE A
    story.append(PageBreak())
    banner("Parte A - Preparazione dei pezzi", "pulizia, prove a secco, inserti filettati")

    callout("Tre regole da qui in avanti.",
            "<b>1.</b> Non alimentare il motore dal Nano o dalla USB: prende i 5 V dal "
            "convertitore. &nbsp; <b>2.</b> Non collegare niente al convertitore prima di "
            "averlo regolato a 5,0 V: un LM2596 nuovo esce spesso a 12 V e brucia Nano e "
            "sensori in un colpo solo. &nbsp; <b>3.</b> Quando il pignone &egrave; montato, "
            "non girare pi&ugrave; il braccio a mano: fra motore e albero c'&egrave; una "
            "riduzione di quasi 1000:1 e si rompono i denti.")

    step("A1", "Pulire i pezzi e fare le prove a secco", [
        "Togli supporti e sbavature. Passa una lima tonda nei fori dove entrano "
        "alberi e perni.",
        "<b>Cuscinetti</b>: il 626ZZ deve entrare nella sede della parete e in quella "
        "del coperchio spinto con il pollice, senza martello. Il 625ZZ deve entrare "
        "nella sede del lato 42T dell'ingranaggio composto. Se sono troppo stretti "
        "carteggia la sede, non forzare: la plastica si crepa.",
        "<b>Albero da 6 mm</b>: deve scorrere senza gioco nei distanziali s1, s2, s3, "
        "nella bandierina e nell'ingranaggio di uscita.",
        "<b>Perno M5</b>: deve scorrere nei distanziali c1 e c2 e nell'ingranaggio composto.",
        "<b>Pignone</b>: il foro &egrave; volutamente stretto e tondo. L'albero del "
        "28BYJ ha due piani: lima il foro a forma di D finch&eacute; il pignone entra a "
        "pressione sull'albero, senza gioco. Non montarlo ancora sul motore.",
    ])

    step("A2", "Inserti filettati a caldo", [
        "Sono dieci: <b>quattro</b> nei bossoli agli angoli del riduttore, "
        "<b>quattro</b> nei bossoli del vano elettronica (due dentro in alto, due sotto "
        "il fondo) e <b>due</b> sotto il piede della staffa del motore.",
        "Saldatore a circa 220 gradi. Appoggia l'inserto sul foro, scaldalo e lascialo "
        "scendere <b>col suo peso</b>, tenendo il saldatore dritto. Fermati quando "
        "&egrave; a filo, poi appoggia subito una superficie piana fredda per "
        "allinearlo.",
        "Se un inserto va storto, riscaldalo e raddrizzalo subito: a freddo non si "
        "recupera pi&ugrave;.",
    ])

    step("A3", "Il magnete nella bandierina", [
        "Il magnete va nella tasca sulla faccia della bandierina. <b>Non incollarlo "
        "ancora</b>: il sensore A3144 risponde a una sola faccia del magnete, e quale "
        "sia lo scopri al passo C5. Per ora tienilo a pressione con un velo di nastro.",
        "Segna con un pennarello una faccia del magnete: ti servir&agrave; per capire "
        "come girarlo.",
    ])

    # =========================================================== PARTE B
    story.append(PageBreak())
    banner("Parte B - Elettronica", "si prepara e si prova a banco, prima della meccanica")
    figure("F12_cablaggio.png", CW, "FIG. B1 - schema elettrico completo")

    step("B1", "Regolare il convertitore LM2596, prima di tutto", [
        "Collega <b>solo</b> il convertitore ai 12 V, con il fusibile sul cavo. Niente "
        "altro a valle.",
        "Con il multimetro sull'uscita gira la vite del trimmer finch&eacute; leggi "
        "<b>5,00 V</b> (va bene fra 4,95 e 5,10). Il trimmer &egrave; multigiro: servono "
        "anche venti giri prima di vedere cambiare la tensione.",
        "Stacca i 12 V. Da qui in poi l'uscita del convertitore &egrave; il "
        "<b>+5 V</b> di tutto il sistema.",
    ])

    step("B2", "Il coperchio del vano", [
        "Monta la presa DC nel foro da 8 mm, con il dado dal lato interno.",
        "Salda due fili di circa 12 cm alla presa (centrale = +12 V, esterno = GND) e "
        "portali all'ingresso del convertitore, <b>IN+</b> e <b>IN-</b>.",
        "Il foro rettangolare &egrave; per la spina USB del Nano: resta libero.",
    ])

    figure_pair("F11b_vassoio.png", "FIG. B2 - disposizione delle schede sul vassoio (in scala)",
                "F11_vano.png", "FIG. B3 - il vassoio montato dentro il vano", width=84 * mm)

    step("B3", "Montare le schede sul vassoio", [
        "<b>LM2596</b> sulle quattro colonnine basse vicino al coperchio: ha due soli "
        "fori, in diagonale. Usa quelli; le altre due colonnine fanno da appoggio. Il "
        "lato IN verso il coperchio, dove arriva la presa.",
        "<b>ULN2003</b> sulle quattro colonnine basse dal lato del riduttore, con il "
        "connettore bianco del motore rivolto verso il passaggio dei cavi.",
        "<b>Arduino Nano</b> sulle quattro colonnine alte (10 mm), con la presa USB "
        "verso il coperchio. Se i pin del tuo Nano sono gi&agrave; saldati verso il "
        "basso, montalo <b>capovolto</b>, componenti verso il vassoio: cos&igrave; i pin "
        "puntano in alto e ci innesti i cavetti Dupont. Se i pin sono sciolti, saldali "
        "verso l'alto e monta il Nano dritto. In tutti e due i casi la USB resta davanti "
        "al foro del coperchio.",
        "Le misure dei fori delle schede cambiano da un produttore all'altro. Prima di "
        "stampare il vassoio misurale con il calibro: se sono diverse correggile nel file "
        "SCAD (appendice E). Il vassoio si ristampa in mezz'ora; in alternativa fissa le "
        "schede con biadesivo spesso.",
    ])

    step("B4", "Bus +5 V e GND", [
        "Usa due morsetti WAGO a 5 vie: uno per il <b>+5 V</b>, uno per il <b>GND</b>.",
        "Al <b>+5 V</b>: OUT+ del convertitore, + della ULN2003, VCC dei sensori, + del "
        "condensatore da 1000 uF.",
        "Al <b>GND</b>: OUT- del convertitore, - della ULN2003, GND dei sensori, - del "
        "condensatore, <b>GND del Nano</b>. Senza il GND in comune i segnali dei sensori "
        "non hanno riferimento e il motore si comporta in modo casuale.",
        "Il condensatore ha la striscia bianca sul polo negativo. Montato al "
        "contrario si gonfia o scoppia.",
        "Il Nano si alimenta <b>solo</b> dalla USB: niente fili sul suo pin 5V.",
    ])

    step("B5", "Nano verso la ULN2003", [
        "Quattro cavetti Dupont: <b>D2 -&gt; IN1, D3 -&gt; IN2, D4 -&gt; IN3, D5 -&gt; IN4</b>.",
        "Il motore si innesta nel connettore bianco a 5 poli della ULN2003: non c'&egrave; "
        "niente da cablare. Il connettore entra in un solo verso.",
    ])

    step("B6", "Preparare i sensori", [
        "Guardando l'A3144 dal lato della <b>faccia marcata</b> (quella con le scritte), "
        "con i piedini in basso: a sinistra VCC, al centro GND, a destra l'uscita.",
        "Salda ai piedini fili lunghi circa <b>50 cm</b>: devono arrivare dalla piastra "
        "dei sensori, dentro il riduttore, fino al vano. Accorcia i piedini a 5 mm e "
        "isola ogni saldatura con la guaina.",
        "Salda un condensatore da 100 nF fra VCC e GND di ogni sensore, il pi&ugrave; "
        "vicino possibile al corpo.",
        "Unisci i due VCC e i due GND vicino alla piastra: al vano arrivano quattro fili, "
        "<b>VCC, GND, CLOSED, OPEN</b>. Segna con un pezzo di nastro quale sensore "
        "&egrave; quale.",
        "Uscita CLOSED -&gt; <b>D10</b>, uscita OPEN -&gt; <b>D11</b>. Non servono "
        "resistenze: il firmware usa quelle interne del Nano.",
    ])

    step("B7", "Caricare il firmware", [
        "Apri <font face='Courier'>firmware/GP1_FlipCap_V6/GP1_FlipCap_V6.ino</font> con "
        "l'IDE Arduino.",
        "Scheda <b>Arduino Nano</b>, processore <b>ATmega328P</b>. Se il caricamento "
        "fallisce, scegli <b>ATmega328P (Old Bootloader)</b>: &egrave; il caso di quasi "
        "tutti i cloni.",
        "In alternativa carica il file gi&agrave; compilato "
        "<font face='Courier'>firmware/build/GP1_FlipCap_V6.ino.hex</font> con avrdude "
        "(istruzioni nel README della cartella).",
        "Non cambiare niente al primo caricamento.",
    ])

    step("B8", "Prova a banco", [
        "Collega i 12 V, il motore alla ULN2003 e il Nano al PC. Motore <b>libero</b>, "
        "non montato.",
        "Apri il monitor seriale a <b>9600 baud</b> con terminatore <b>Nuova riga (LF)</b> "
        "e prova i comandi della tabella.",
        "Con <font face='Courier'>&gt;O000</font> l'albero del motore deve girare in modo "
        "regolare. Nessun sensore scatta, quindi dopo circa un minuto il motore si ferma "
        "da solo e lo stato diventa 3: &egrave; giusto.",
        "Durante il movimento avvicina il magnete al sensore OPEN: il motore si deve "
        "fermare subito e lo stato diventa 2. Se non succede, gira il magnete dall'altra "
        "faccia. Stessa prova con <font face='Courier'>&gt;C000</font> e il sensore CLOSED "
        "(stato 1).",
        "Se il motore vibra senza girare, controlla l'ordine D2-D5 verso IN1-IN4.",
    ])
    table([
        ["Mandi", "Risposta", "Significato"],
        ["&gt;P000", "*P98000", "ping: risponde il product ID 98"],
        ["&gt;V000", "*V98160", "versione del firmware"],
        ["&gt;S000", "*S98xyz", "stato: x motore, y luce (sempre 0), z tappo"],
        ["&gt;O000", "*O98000", "apri"],
        ["&gt;C000", "*C98000", "chiudi"],
    ], [24 * mm, 30 * mm, CW - 54 * mm])
    table([
        ["Cifra", "Valori"],
        ["x (motore)", "0 = fermo, 1 = in movimento"],
        ["z (tappo)", "0 = in mezzo, 1 = chiuso, 2 = aperto, 3 = fermo per errore (sensore non trovato)"],
    ], [30 * mm, CW - 30 * mm])

    # =========================================================== PARTE C
    story.append(PageBreak())
    banner("Parte C - Il riduttore", "dall'housing vuoto al meccanismo tarato e chiuso")
    figure("F05_housing.png", 132 * mm, "FIG. C1 - l'housing visto dal lato aperto")

    step("C1", "Cuscinetti 626ZZ", [
        "Spingi un 626ZZ nella sede della parete sinistra <b>dall'interno</b> della "
        "scatola, finch&eacute; batte sul labbro esterno.",
        "Spingi il secondo 626ZZ nella sede del coperchio, anche questo dal lato "
        "interno.",
        "Se entrano troppo morbidi, una goccia di frenafiletti medio sul diametro "
        "esterno.",
    ])

    step("C2", "Piastra dei sensori - va montata prima dell'albero", [
        "Infila i due A3144 nelle loro sedi con la <b>faccia marcata verso l'alto</b>, "
        "cio&egrave; verso l'interno della scatola, dove passer&agrave; il magnete. I "
        "fili escono dalla fessura verso il centro e girano sotto la piastra.",
        "La sede rivolta verso il <b>bordo anteriore</b> della scatola (lato tappo) "
        "&egrave; quella del sensore <b>CLOSED</b>; la sede rivolta verso il "
        "<b>fondo</b> della scatola (lato tubo) &egrave; quella del sensore "
        "<b>OPEN</b>. Guarda la figura C2.",
        "Fissa la piastra con due viti M3 x 16 infilate <b>dall'esterno</b> della parete "
        "sinistra, rondella e dado dentro. Stringi appena: le asole servono alla "
        "taratura del passo C5.",
        "Porta i quattro fili lungo la parete fino al passaggio in basso verso il vano, e "
        "fermali con una goccia di colla a caldo lontano dagli ingranaggi.",
    ], fig="F07_piastra_sensori.png", figw=110 * mm,
        figcap="FIG. C2 - piastra dei sensori sulla parete sinistra, vista dall'interno")

    figure("F06_assi.png", CW, "FIG. C3 - l'ordine dei pezzi sui due assi")

    step("C3", "Albero di uscita, distanziali, bandierina, ingranaggio 70T", [
        "Con una lima fai due piccoli piani sull'albero dove appoggeranno i grani: a "
        "<b>41 mm</b> e a <b>73 mm</b> da un'estremit&agrave;. Quell'estremit&agrave; "
        "&egrave; il lato del braccio.",
        "Infila l'albero dall'esterno attraverso il 626ZZ della parete, lato braccio verso "
        "l'esterno, finch&eacute; ne sporgono 24 mm fuori dalla parete.",
        "Dall'interno infila in quest'ordine: <b>s1</b> (il corto da 6 mm), la "
        "<b>bandierina</b> con il magnete verso i sensori, <b>s3</b> (21 mm), "
        "l'<b>ingranaggio 70T</b> con il mozzo verso il coperchio, <b>s2</b> (13 mm).",
        "Spingi tutto verso la parete: s1 appoggia sul cuscinetto, e bandierina e "
        "ingranaggio si trovano da soli al posto giusto. Stringi i due grani sui piani "
        "dell'albero.",
        "Gira l'albero a mano: la bandierina non deve toccare la piastra dei sensori in "
        "nessun punto.",
    ], fig="F08_albero.png", figw=112 * mm,
        figcap="FIG. C4 - albero con distanziali, bandierina e ingranaggio di uscita")

    figure("F09b_28byj.png", 82 * mm, "FIG. C5 - il 28BYJ-48 visto dal lato dell'albero")

    step("C4", "Motore e staffa", [
        "<b>Il 28BYJ-48 ha l'albero fuori centro di 8 mm</b> (figura C5): la staffa ha "
        "gi&agrave; il foro nella posizione giusta, ma devi infilare il motore con il "
        "cappuccio azzurro dei fili verso l'intaglio della staffa.",
        "Il corpo del motore passa nel foro della staffa e le orecchie appoggiano sulla "
        "faccia rivolta verso il coperchio. Avvitale con due M3 x 8: le viti si "
        "filettano da sole nella plastica. Stringi appena.",
        "Porta il cavo del motore verso il passaggio per il vano.",
        "Metti la staffa sul fondo del riduttore e avvitala <b>da sotto la scatola</b> "
        "con due M3 x 8 negli inserti del piede.",
        "Il pignone <b>non</b> si monta ancora.",
    ], fig="F09_staffa_motore.png", figw=108 * mm,
        figcap="FIG. C6 - staffa e motore montati sul fondo del riduttore")

    step("C5", "Ingranaggio composto", [
        "Pianta il 625ZZ nella sede del lato 42T del composto.",
        "Infila la vite M5 x 80 <b>dall'esterno</b> della parete sinistra, con una "
        "rondella sotto la testa.",
        "Dall'interno infila sulla vite, in quest'ordine: il distanziale <b>c1</b> (il "
        "lungo), la <b>rondella in PTFE</b>, il <b>composto</b> (lato 14T verso la parete), "
        "il distanziale <b>c2</b>. Facendolo scorrere, ruotalo un poco finch&eacute; i "
        "denti entrano fra quelli del 70T.",
        "Il composto deve girare libero e avere un filo di gioco assiale. La vite "
        "arriver&agrave; al coperchio al passo C9.",
    ], fig="F10_riduttore.png", figw=96 * mm,
        figcap="FIG. C7 - il riduttore completo, visto dal lato del coperchio")

    step("C6", "Taratura dei sensori, a mano", [
        "Collega l'elettronica preparata nella parte B e apri il monitor seriale. Il "
        "pignone non c'&egrave;: l'albero di uscita gira liberamente a mano.",
        "Ruota l'albero finch&eacute; il magnete &egrave; davanti al sensore CLOSED e "
        "manda <font face='Courier'>&gt;S000</font>: l'ultima cifra deve essere "
        "<b>1</b>.",
        "Se resta 0, prima di tutto <b>gira il magnete</b> nella sua tasca: l'A3144 "
        "&egrave; unipolare e risponde a una sola faccia. Quando funziona, incolla il "
        "magnete con una goccia di cianoacrilica.",
        "Ruota l'albero di 270 gradi nel verso di apertura (il magnete si porta davanti "
        "al sensore OPEN): l'ultima cifra deve diventare <b>2</b>.",
        "Per regolare il punto di scatto allenta le due viti della piastra e ruotala "
        "nelle asole, poi stringi. Le asole muovono insieme i due sensori, che restano "
        "sempre a 270 gradi l'uno dall'altro.",
    ])

    step("C7", "Pignone e ingranamento del motore", [
        "Infila il pignone sull'albero del motore fino al collarino: i denti devono "
        "allinearsi con quelli del 42T. Ruota il composto di un pelo per farli entrare.",
        "Allenta le due viti delle orecchie. I fori delle orecchie sono pi&ugrave; "
        "larghi delle viti: spingi il motore verso il composto finch&eacute; il pignone "
        "ingrana senza forzare, poi tornalo indietro di un soffio, cos&igrave; resta un "
        "minimo gioco percepibile. Stringi.",
        "Troppo stretto: il motore fatica e salta dei passi. Troppo lasco: i denti "
        "scavalcano sotto sforzo.",
        "<b>Da adesso il braccio non si gira pi&ugrave; a mano.</b>",
    ])

    step("C8", "Verso di rotazione e prova a vuoto", [
        "Manda <font face='Courier'>&gt;C000</font>: il meccanismo si porta sul sensore "
        "CLOSED e si ferma (stato 1).",
        "Manda <font face='Courier'>&gt;O000</font>: la bandierina deve muoversi verso il "
        "sensore OPEN. Se va nel verso sbagliato, fermala con "
        "<font face='Courier'>&gt;C000</font>, metti <font face='Courier'>MOTOR_REVERSED = "
        "true</font> nel firmware e ricaricalo.",
        "La corsa completa deve durare <b>circa 55 secondi</b> e finire con lo stato 2. "
        "Molto di pi&ugrave;, o uno stato 3, significa passi persi o sensore non "
        "raggiunto.",
    ])

    step("C9", "Chiudere il riduttore", [
        "Ultimo controllo: nessun filo vicino agli ingranaggi, tutti fermati con colla a "
        "caldo o una fascetta.",
        "Appoggia il coperchio: l'albero di uscita entra nel suo 626ZZ e la vite M5 nel "
        "foro. Avvitalo con quattro M3 x 8.",
        "Sulla vite M5, fuori dal coperchio: rondella e dado autobloccante, "
        "<b>senza stringere</b>. Il composto deve continuare a girare libero.",
    ])

    # =========================================================== PARTE D
    story.append(PageBreak())
    banner("Parte D - Sul telescopio", "fissaggio, braccio, tappo, appoggi, collaudo")

    step("D1", "Chiudere il vano elettronica", [
        "Infila il vassoio nel vano di taglio: il bordo interno va sotto il listello "
        "della parete sinistra.",
        "Collega il cavo del motore alla ULN2003 e i quattro fili dei sensori, che "
        "arrivano dal passaggio.",
        "Chiudi con il coperchio del vano: il suo listello interno tiene fermo "
        "l'altro bordo del vassoio. Quattro viti M3 x 8 svasate.",
    ])

    step("D2", "Montare la scatola sul tubo", [
        "Incolla l'EVA da 2 mm sulla faccia interna delle due selle.",
        "Posiziona la scatola con il suo bordo anteriore <b>10 mm oltre la bocca del "
        "tubo</b>: l'albero del braccio cade cos&igrave; 25 mm dietro la bocca, come nel "
        "progetto. Puoi ruotare tutto attorno al tubo per evitare cercatori o "
        "focheggiatori: basta che il tappo parcheggiato trovi il tubo sotto di "
        "s&eacute; e che gli appoggi possano stare sulla parte alta del tubo.",
        "Passa una cinghia attorno al tubo sopra ognuna delle due selle, fra le due "
        "costole, e stringi bene.",
        "Aggiungi circa 700 g in testa al tubo: <b>ribilancia la montatura</b>.",
    ], fig="F13_cinghie.png", figw=118 * mm,
        figcap="FIG. D1 - le due cinghie passano sopra le selle, fra le costole")

    step("D3", "Braccio", [
        "Manda <font face='Courier'>&gt;C000</font>: l'albero si porta in posizione "
        "CLOSED.",
        "Infila il mozzo del braccio sull'albero, a filo dell'estremit&agrave;. Il mozzo "
        "&egrave; a morsetto: entra libero.",
        "Orienta il braccio in modo che la sua piastra sia davanti alla bocca del tubo e "
        "<b>parallela</b> alla bocca, e stringi la vite M3 x 25 con il dado nella sua sede. "
        "Stringi deciso: &egrave; questo morsetto che trasmette tutta la coppia.",
    ], fig="F14_braccio.png", figw=104 * mm,
        figcap="FIG. D2 - braccio e contropiastra")

    step("D4", "Tappo", [
        "Traccia il cerchio con uno spago e una puntina e taglia il disco con il cutter "
        "(374 mm con le misure di default). Canali del polipropilene orientati come "
        "spiegato al capitolo 0.7.",
        "Appoggia il disco sulla piastra del braccio, centrato sulla bocca del tubo, e "
        "<b>usa la contropiastra come dima</b> per i quattro fori da 4,5 mm.",
        "I dadi M4 vanno nelle sedi esagonali sotto la piastra del braccio. Viti M4 x 16 "
        "dal lato cielo con rondelle larghe, attraverso la contropiastra e il disco. "
        "Stringi senza schiacciare il polipropilene.",
        "Facoltativo, per i dark: un anello di gomma crepla sul lato interno del tappo, "
        "alto quanto basta a sfiorare l'anello del tubo. Pesa: rileggi il margine al "
        "capitolo 0.7.",
    ])

    step("D5", "Appoggi del tappo", [
        "Incolla 2 mm di EVA sulla faccia superiore di ogni appoggio e sotto, dove tocca "
        "il tubo.",
        "Fissali sulla generatrice pi&ugrave; alta del tubo, dalla parte della scatola, "
        "con una cinghia ciascuno: il primo a <b>%d mm</b> dalla bocca del tubo, il "
        "secondo a <b>%d mm</b>." % (dati["rest1"], dati["rest2"]),
        "Manda <font face='Courier'>&gt;O000</font> e guarda l'ultimo tratto della corsa: "
        "il tappo si deve posare sui due appoggi proprio quando il motore si ferma. Se "
        "si ferma prima, sollevato di qualche millimetro, aggiungi EVA; se si posa e il "
        "motore continua a girare, toglila.",
    ], fig="F15_appoggi.png", figw=CW,
        figcap="FIG. D3 - posizioni lungo il tubo, misurate dalla bocca")

    step("D6", "Collaudo", [
        "Apri e chiudi almeno dieci volte di seguito: lo stato finale deve essere "
        "sempre 1 o 2, mai 3.",
        "Ripeti con il telescopio nelle posizioni in cui lo parcheggi davvero.",
        "Controlla che il tappo chiuso copra tutta la bocca e che, aperto, stia fermo "
        "sugli appoggi anche dando un colpetto al tubo.",
    ])
    figure("F02_assieme_parcheggiato.png", 138 * mm,
           "FIG. D4 - tappo parcheggiato, appoggiato sul tubo")

    step("D7", "Ekos / INDI", [
        "Driver <b>Flip Flat</b> (<font face='Courier'>indi_flipflat</font>), porta "
        "seriale del Nano, 9600 baud.",
        "<b>Park</b> = chiudi, <b>Unpark</b> = apri.",
        "La corsa dura circa 55 secondi, pi&ugrave; dei 30 dopo i quali il driver INDI "
        "ripete il comando e scrive nel log <i>Parking cap timed out. Retrying</i>. "
        "&Egrave; normale: il firmware riconosce il comando ripetuto e lo ignora, e la "
        "corsa finisce regolarmente.",
        "Usa il tappo a telescopio fermo: aprilo prima di sparcheggiare e chiudilo dopo "
        "aver parcheggiato.",
    ])

    # =========================================================== APPENDICI
    story.append(PageBreak())
    banner("Appendici")

    h2("A. &nbsp;Comandi seriali (protocollo Alnitak)")
    p("9600 baud, 8N1, ogni comando termina con un a capo (LF). Il firmware emula "
      "l'Alnitak Remote Dust Cover, product ID 98.")
    sp(3)
    table([
        ["Comando", "Risposta", "Effetto"],
        ["&gt;P000", "*P98000", "ping"],
        ["&gt;O000", "*O98000", "apri il tappo"],
        ["&gt;C000", "*C98000", "chiudi il tappo"],
        ["&gt;S000", "*S98xyz", "stato: x motore, y luce, z tappo"],
        ["&gt;V000", "*V98160", "versione del firmware"],
        ["&gt;J000", "*J98000", "luminosit&agrave; (non usata)"],
        ["&gt;B, &gt;L, &gt;D", "*B98000 ...", "comandi del pannello luminoso: rispondono ma non fanno niente"],
    ], [26 * mm, 30 * mm, CW - 56 * mm])

    h2("B. &nbsp;Coppia, velocit&agrave; e peso del tappo")
    p("Coppia disponibile stimata: circa 30 mN&middot;m del 28BYJ-48 a 12 giri al "
      "minuto, moltiplicati per la riduzione 15:1 e per un rendimento di 0,72 sui due "
      "stadi: <b>circa 0,32 N&middot;m</b> sull'albero di uscita. Il valore reale "
      "cambia da motore a motore.")
    sp(3)
    p("Coppia richiesta: il caso peggiore &egrave; il braccio orizzontale, con il "
      "centro del tappo a 267 mm dall'albero. Il braccio (circa 57 g) pesa come se "
      "stesse a 67 mm, contropiastra e viti (circa 27 g) a 108 mm.")
    sp(3)
    p("<b>Se il tappo non si alza</b> e hai gi&agrave; il materiale pi&ugrave; leggero, "
      "rallenta il motore: il 28BYJ ha pi&ugrave; coppia a bassa velocit&agrave;. Nel "
      "firmware porta <font face='Courier'>STEP_INTERVAL_US</font> da 2400 a 3000 e "
      "<font face='Courier'>MOVE_TIMEOUT_MS</font> da 70000 a 90000 (la corsa passa a "
      "circa 70 secondi). Se non basta ancora serve un motore pi&ugrave; forte.")

    h2("C. &nbsp;Diagnostica")
    table([
        ["Sintomo", "Causa probabile", "Cosa fare"],
        ["Il motore vibra ma non gira", "ordine delle fasi", "controlla D2-D5 verso IN1-IN4"],
        ["Gira nel verso sbagliato", "-", "MOTOR_REVERSED = true nel firmware"],
        ["Lo stato resta sempre 0", "nessun sensore scatta",
         "gira il magnete; controlla VCC, GND e il GND in comune col Nano"],
        ["Stato 3 a fine corsa", "il sensore di arrivo non scatta",
         "gira il magnete o registra la piastra (passo C6)"],
        ["Stato 3 dopo pochi secondi", "il motore stalla",
         "controlla l'ingranamento (C7); tappo pi&ugrave; leggero; motore pi&ugrave; "
         "lento (appendice B)"],
        ["Il tappo si ferma sopra gli appoggi", "EVA troppo sottile", "aggiungi EVA sugli appoggi"],
        ["A fine apertura il motore insiste", "EVA troppo spessa", "togli EVA"],
        ["Rumore ciclico dagli ingranaggi", "pignone troppo spinto contro il 42T", "rifai il passo C7"],
        ["Il Nano si resetta quando parte il motore", "motore alimentato dal Nano",
         "il motore va sul +5 V del convertitore (B4)"],
        ["La scatola ruota attorno al tubo", "cinghie lente o EVA mancante",
         "stringi le cinghie; l'EVA sotto le selle &egrave; necessaria"],
    ], [42 * mm, 42 * mm, CW - 84 * mm])

    h2("D. &nbsp;Limiti verificati")
    p("Le luci qui sotto sono misurate sulle mesh dei pezzi, montate in posizione, "
      "lungo tutta la corsa (passi di 3 gradi). Lo script &egrave; "
      "<font face='Courier'>docs/verifica_collisioni.py</font>; il risultato "
      "completo &egrave; in <font face='Courier'>docs/VERIFICA_COLLISIONI.txt</font>.")
    sp(3)
    table(dati["tabella_luci"], [CW - 40 * mm, 40 * mm])
    callout("Extracorsa.",
            "Se il sensore OPEN non scatta, oltre i 270 gradi il tappo &egrave; gi&agrave; "
            "sugli appoggi: il motore si ferma contro di loro, cosa che il 28BYJ "
            "sopporta, e il firmware lo spegne al pi&ugrave; tardi dopo "
            "MAX_MOVE_STEPS = 24.100 passi (circa 284 gradi) o 70 secondi, segnalando "
            "lo stato 3. In chiusura, oltre lo zero il tappo va in appoggio sull'anello "
            "del tubo.", kind="info")

    h2("E. &nbsp;Rigenerare i pezzi con misure diverse")
    p("Serve OpenSCAD (la libreria MCAD &egrave; gi&agrave; inclusa). Tutti i "
      "parametri sono in testa a <font face='Courier'>gp1_flipcap_V6.scad</font>, "
      "commentati. Aprendo il file e premendo F5 si vede l'assieme; "
      "<font face='Courier'>cap_angle</font> muove il tappo.")
    sp(3)
    table([
        ["Cosa cambi", "Parametro", "Pezzi da rigenerare"],
        ["diametro del tubo", "ota_d", "housing, cap_rest"],
        ["spessore del tappo", "cap_thickness", "mono_arm, cap_rest"],
        ["diametro del tappo", "cap_d", "nessuno: &egrave; solo la misura a cui tagli il disco"],
        ["fori delle schede", "nano_holes, uln_holes, buck_holes", "bay_tray"],
        ["distanza degli appoggi", "rest_z", "nessuno"],
    ], [38 * mm, 58 * mm, CW - 96 * mm])
    p("Da riga di comando, un pezzo alla volta:")
    code("openscad -o stl/housing.stl -D 'part=\"housing\"' -D ota_d=355 gp1_flipcap_V6.scad")
    p("<b>Dopo ogni modifica rilancia la verifica</b>, che rifa' da sola tutti i "
      "controlli di questo manuale sulle mesh nuove (servono Python con numpy e scipy):")
    code("python docs/verifica_collisioni.py")
    p("Impiega una ventina di minuti: esporta tutti i pezzi da OpenSCAD e prova la corsa "
      "ogni 3 gradi.", "small")

    h2("F. &nbsp;Se hai gi&agrave; stampato pezzi di versioni precedenti")
    p("Il <b>composto</b> e il <b>pignone</b> hanno la stessa geometria dalla V4.1 in poi "
      "e si riusano; l'<b>ingranaggio di uscita</b> si riusa dopo averlo forato (qui "
      "sotto). La <b>bandierina</b> della V4.1 ha la tasca del magnete chiusa dentro il "
      "pezzo e va ristampata. Tutto il resto &egrave; nuovo e va stampato.")
    sp(2)
    callout("Attenzione all'ingranaggio di uscita delle V4.x.",
            "Nelle versioni precedenti il foro del grano cadeva sulla faccia dell'ingranaggio "
            "invece che nel mozzo, e il grano non poteva stringere l'albero. Se riusi quel "
            "pezzo, fora il mozzo a met&agrave; della sua parte sporgente, in radiale, con una "
            "punta da 2,5 mm, e usa una vite M3 che si filetta da sola. Il file "
            "<font face='Courier'>output_gear.stl</font> della V6 ha gi&agrave; il foro "
            "giusto.")
    sp(8)
    p("<i>Documento generato automaticamente: docs/genera_figure_manuale.py crea le "
      "figure dal modello, docs/genera_manuale_pdf.py impagina, "
      "docs/contenuto_manuale.py contiene il testo.</i>", "small")
