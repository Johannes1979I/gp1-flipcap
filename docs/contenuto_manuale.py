#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) 2026 Johannes1979I
"""
GP1 FlipCap V4.2 - contenuto del manuale di montaggio.

Separato da genera_manuale_pdf.py (che contiene solo gli elementi grafici)
per poter lavorare sul testo senza toccare l'impaginazione.

Il manuale e' GENERICO: parte dal presupposto che chi lo legge costruisca
tutto da zero. Le note per chi viene dalla V4.1 stanno nell'appendice F.
"""


def build(ui):
    """`ui` espone gli elementi di impaginazione: banner, step, table, ecc."""
    banner, step, table, callout = ui.banner, ui.step, ui.table, ui.callout
    figure, figure_pair, h2, p, sp = ui.figure, ui.figure_pair, ui.h2, ui.p, ui.sp
    mm, CW, PageBreak, story = ui.mm, ui.CW, ui.PageBreak, ui.story
    Paragraph, S, Spacer = ui.Paragraph, ui.S, ui.Spacer

    # ---------------------------------------------------------- copertina
    story.append(Spacer(1, 24 * mm))
    story.append(Paragraph("GP1 FlipCap V4.2", S["cover1"]))
    sp(6)
    story.append(Paragraph("Manuale di costruzione e montaggio", S["cover2"]))
    sp(2)
    story.append(Paragraph(
        "Tappo motorizzato per telescopi newtoniani<br/>"
        "comandato da INDI / Ekos", S["cover2"]))
    sp(8)
    figure("F01_assieme.png", 138 * mm)
    sp(2)
    callout("Cosa stai per costruire.",
            "Un tappo antipolvere motorizzato che si apre e si chiude da solo "
            "su comando del software di acquisizione. Un solo motore, un solo "
            "braccio, tutta la meccanica chiusa in una scatola stampata che si "
            "fissa al tubo con due cinghie. Il progetto &egrave; parametrico: "
            "il diametro del tubo e quello del tappo sono variabili, "
            "quindi si adatta a newtoniani diversi.", kind="info")
    story.append(PageBreak())

    # ------------------------------------------------------------- indice
    banner("Indice")
    table([
        ["Capitolo", "Contenuto"],
        ["<b>0. Il progetto in breve</b>",
         "cosa fa, cosa serve, elenco completo dei pezzi da stampare, "
         "minuteria, scelta del materiale del tappo, adattamento al proprio tubo"],
        ["<b>A. Meccanica</b>",
         "dalla scatola stampata al gruppo motore-ingranaggi funzionante"],
        ["<b>B. Elettronica</b>",
         "alimentazione, sensori, cablaggio, firmware, prova a banco"],
        ["<b>C. Integrazione</b>",
         "taratura, chiusura, braccio, tappo, montaggio sul telescopio, Ekos"],
        ["<b>Appendici</b>",
         "comandi seriali, coppia e posizione di park, diagnostica, limiti "
         "verificati, come rigenerare i pezzi, note per chi viene dalla V4.1"],
    ], [42 * mm, CW - 42 * mm])
    callout("Come leggere i passi.",
            "Ogni passo &egrave; numerato dentro la sua parte (A1, A2... B1... "
            "C1...). <b>L'ordine conta</b>: alcuni componenti non sono "
            "pi&ugrave; raggiungibili dopo che ne sono stati montati altri. In "
            "particolare la piastra dei sensori va montata per prima e il tappo "
            "per ultimo.", kind="info")
    sp(4)
    callout("Questo progetto &egrave; open hardware.",
            "Licenza CERN-OHL-S v2. Puoi usarlo, modificarlo e ridistribuirlo, "
            "anche commercialmente, a patto di pubblicare la sorgente delle tue "
            "modifiche sotto la stessa licenza. Fornito cos&igrave; com'&egrave;, "
            "<b>senza alcuna garanzia</b>: chi lo monta su un telescopio "
            "&egrave; responsabile della propria verifica.", kind="ok")
    story.append(PageBreak())

    # ================================================ 0. IL PROGETTO IN BREVE
    banner("0. Il progetto in breve",
           "cosa serve, cosa stampare, quali scelte fare prima di cominciare")

    h2("0.1 &nbsp;Architettura")
    table([
        ["Voce", "Valore"],
        ["Motore", "1 x 28BYJ-48 5 V con driver ULN2003"],
        ["Riduzione", "riduttore interno del 28BYJ + riduzione stampata 15:1 "
                      "(modulo 0,8: 14T-&gt;42T, 14T-&gt;70T)"],
        ["Corsa del tappo", "90 gradi, circa 19 secondi"],
        ["Albero di uscita", "acciaio 6 mm su due cuscinetti 626ZZ"],
        ["Finecorsa", "2 sensori Hall A3144 su piastra unica, magnete 6x3 su "
                      "bandierina solidale all'albero"],
        ["Fissaggio al tubo", "sella curva parametrica + due cinghie"],
        ["Interfaccia", "USB seriale, protocollo Alnitak Remote Dust Cover "
                        "(product ID 98), driver INDI <i>indi_flipflat</i>"],
        ["Valori di default", "tubo Ø362 mm, tappo Ø374 mm. Entrambi "
                              "parametrici: vedi 0.7"],
    ], [38 * mm, CW - 38 * mm])
    callout("Non &egrave; un pannello per i flat.",
            "Il product ID 98 &egrave; un <i>dust cover</i>: copre e scopre, "
            "punto. Non ha luce integrata. Per i flat servono cielo "
            "crepuscolare o un pannello separato.", kind="info")

    h2("0.2 &nbsp;Pezzi da stampare")
    p("Dieci pezzi, circa <b>410 cm3</b> di materiale, intorno ai <b>320 g</b> "
      "di filamento. L'housing da solo vale i tre quarti del totale ed &egrave; "
      "la stampa lunga: conviene farla per prima e proseguire con il resto "
      "mentre gira.")
    sp(4)
    table([
        ["Pezzo", "Volume", "Filam.*", "Orientamento e supporti"],
        ["housing.stl", "251,5 cm3", "~190 g",
         "parete sinistra piena sul piatto, scatola aperta verso l'alto. "
         "Supporti sotto il raccordo con la sella"],
        ["cover.stl", "33,7 cm3", "~26 g", "faccia piana sul piatto, nessun supporto"],
        ["motor_bracket.stl", "33,8 cm3", "~26 g",
         "appoggiata sulla piastra motore, flangia in verticale. Supporti solo "
         "sotto la flangia"],
        ["mono_arm.stl", "54,3 cm3", "~41 g",
         "mozzo sul piatto, piastra del tappo in alto. Supporti sotto la piastra"],
        ["lid_backplate.stl", "8,5 cm3", "~6 g", "piatta, nessun supporto"],
        ["hall_plate.stl", "3,5 cm3", "~3 g", "piatta, nessun supporto"],
        ["magnet_flag.stl", "1,9 cm3", "~2 g", "faccia piana sul piatto"],
        ["output_gear.stl (70T)", "15,8 cm3", "~18 g",
         "piatto sul lato senza mozzo"],
        ["compound_gear.stl (42T/14T)", "4,9 cm3", "~6 g",
         "in piedi sull'asse, supporti minimi"],
        ["motor_pinion.stl (14T)", "0,5 cm3", "~1 g", "in piedi sull'asse"],
    ], [42 * mm, 18 * mm, 16 * mm, CW - 76 * mm])
    p("* stima indicativa a 35% di riempimento in PETG; dipende dal profilo di "
      "stampa.", "small")
    sp(4)
    table([
        ["Gruppo", "Materiale", "Layer", "Perimetri", "Riempimento"],
        ["Scatola, coperchio, staffa, braccio, sella",
         "PETG o ASA", "0,20 mm", "4-5", "30-40%"],
        ["Ingranaggi", "PETG, ASA o PA", "0,12-0,16 mm", "5+", "50-100%"],
        ["Piastra sensori, contropiastra, bandierina",
         "PETG o ASA", "0,20 mm", "3", "30%"],
    ], [58 * mm, 30 * mm, 22 * mm, 20 * mm, CW - 130 * mm])
    callout("Il PLA non va bene.",
            "La scatola sta sul tubo, al sole del pomeriggio prima della "
            "sessione, e il motore scalda. Il PLA si deforma. PETG o ASA.")

    h2("0.3 &nbsp;Viteria e minuteria")
    table([
        ["Q.t&agrave;", "Componente", "Dove va"],
        ["1", "Albero acciaio 6 mm x 100 mm", "albero di uscita"],
        ["2", "Cuscinetto 626ZZ (6x19x6)", "parete della scatola e boss del coperchio"],
        ["1", "Cuscinetto 625ZZ (5x16x5)", "lato 42T dell'ingranaggio composto"],
        ["1", "Perno M5 x 80 + rondelle + dado autobloccante", "ingranaggio composto"],
        ["1", "Rondella PTFE o nylon M5", "fra composto e parete"],
        ["4", "Inserti M3 + 4 viti M3x10", "coperchio della scatola"],
        ["2", "Inserti M3 + 2 viti M3x10", "staffa motore, avvitata al tetto dall'esterno"],
        ["2", "Viti M3x12 + rondelle", "28BYJ-48 sulla staffa (asole di registrazione)"],
        ["2", "Viti M3x16 + rondelle + dadi", "piastra sensori sulla parete"],
        ["1", "Vite M3x25 + dado", "morsetto del mozzo del braccio"],
        ["2", "Viti M3 (grani o a testa cilindrica)", "bandierina e mozzo ingranaggio di uscita"],
        ["4", "Viti M4x16 + rondelle larghe + 4 dadi M4", "tappo sul braccio"],
        ["2", "Cinghie 25 mm x 1200 mm", "fissaggio al tubo (velcro o fibbia)"],
        ["1", "Nastro EVA o gomma 3-4 mm", "fra sella e tubo"],
        ["1", "Disco per il tappo", "vedi 0.6"],
    ], [12 * mm, 62 * mm, CW - 74 * mm])

    h2("0.4 &nbsp;Elettronica")
    table([
        ["Q.t&agrave;", "Componente", "Nota"],
        ["1", "Arduino Nano (ATmega328P 5 V)", "CH340 o USB-C vanno bene"],
        ["1", "28BYJ-48", "versione 5 V"],
        ["1", "Scheda driver ULN2003", "il motore ci si innesta col connettore a 5 poli"],
        ["1", "Convertitore buck LM2596", "12 V -&gt; 5,0 V, almeno 2 A"],
        ["2", "Sensore Hall A3144 o AH3144",
         "interruttore unipolare: risponde a una sola polarit&agrave; del magnete"],
        ["1", "Magnete al neodimio 6x3 mm", "N35 o superiore"],
        ["1", "Condensatore elettrolitico 1000 uF 10-16 V", "sul bus 5 V"],
        ["2", "Condensatore ceramico 100 nF", "uno per sensore Hall"],
        ["1", "Fusibile 1-1,5 A + portafusibile", "lato 12 V"],
        ["1", "Connettore DC 5,5x2,1 oppure GX12-2", "ingresso alimentazione"],
        ["-", "Cavo 0,25-0,5 mm2, termorestringente, morsettiera o WAGO", ""],
    ], [12 * mm, 68 * mm, CW - 80 * mm])
    p("In <i>stl/accessori/</i> c'&egrave; anche una scatola per Nano, "
      "ULN2003 e buck. Non &egrave; generata dal modello parametrico e la sua "
      "mesh non &egrave; watertight: si stampa lo stesso, se lo slicer protesta "
      "usa la riparazione automatica.", "small")

    h2("0.5 &nbsp;Attrezzi")
    p("Saldatore e stagno &middot; saldatore con punta per inserti filettati "
      "&middot; chiavi a brugola 2 / 2,5 / 3 mm &middot; chiave o bussola da "
      "5,5 mm &middot; cutter e riga &middot; lima piatta piccola o lima a D "
      "&middot; multimetro &middot; metro flessibile da sarto &middot; un "
      "terminale seriale (IDE Arduino, PuTTY, minicom). Un trapano con punta "
      "da 3,4 mm serve <b>solo</b> a chi parte da un housing V4.1: vedi "
      "appendice F.")

    story.append(PageBreak())
    h2("0.6 &nbsp;Scegliere il materiale del tappo")
    p("&Egrave; la scelta che pesa di pi&ugrave; su tutto il progetto, e va "
      "fatta <b>prima</b> di stampare il braccio: lo spessore del disco "
      "determina la quota delle piazzole di `mono_arm`.")
    sp(4)
    p("Il 28BYJ-48 con la riduzione 15:1 eroga circa <b>0,32 N&middot;m</b>. "
      "La coppia che serve per staccare il tappo dipende dalla massa del disco "
      "e da quanto &egrave; alto il tubo quando il tappo si muove. Nella "
      "tabella il <b>margine</b> &egrave; il rapporto fra coppia disponibile e "
      "coppia richiesta: sotto 1,00 il tappo non si apre.")
    sp(4)
    table([
        ["Materiale del disco Ø374", "Massa*", "Freccia**",
         "Margine<br/>tubo a 0 deg", "Margine<br/>a 45 deg", "Margine<br/>allo zenit"],
        ["Forex / PVC espanso 1,5 mm", "109 g", "31 mm",
         "4,6x", "1,48x", "1,28x"],
        ["Forex 2 mm", "137 g", "15 mm", "4,0x", "1,21x", "1,04x"],
        ["Forex 3 mm", "192 g", "4 mm",
         "3,1x", "<font color='#c0392b'><b>0,88x</b></font>",
         "<font color='#c0392b'><b>0,76x</b></font>"],
        ["<b>Polipropilene alveolare 3 mm</b>", "<b>76 g</b>", "<b>5 mm</b>",
         "<b>5,8x</b>", "<b>2,03x</b>", "<b>1,76x</b>"],
        ["Depron / XPS 6 mm", "50 g", "9 mm", "7,2x", "2,85x", "2,50x"],
    ], [46 * mm, 15 * mm, 17 * mm, 22 * mm, 20 * mm, CW - 120 * mm])
    p("* massa del disco pi&ugrave; contropiastra, viti e dadi. ** freccia "
      "sotto peso proprio con il tubo allo zenit, sbalzo di 350 mm.", "small")
    sp(4)
    callout("Come si legge.",
            "Il <b>polipropilene alveolare da 3 mm</b> &egrave; la scelta "
            "migliore: pi&ugrave; leggero del Forex 1,5 mm, pi&ugrave; rigido "
            "del Forex 2 mm, impermeabile e si taglia col cutter. Orienta le "
            "nervature interne in direzione radiale, dall'attacco del braccio "
            "verso il bordo opposto. Il <b>Forex 3 mm</b> &egrave; molto "
            "rigido ma pesa il doppio: funziona solo se il tappo viene "
            "azionato con il tubo basso (vedi appendice B). Il <b>Depron</b> "
            "&egrave; il pi&ugrave; leggero in assoluto ma &egrave; fragile: "
            "una ditata lo ammacca.", kind="info")
    sp(2)
    callout("Un anello stampato con la tela tesa non conviene.",
            "&Egrave; la prima idea che viene, ma non funziona: un anello da "
            "20 x 2,5 mm di Ø374 mm pesa gi&agrave; 71 g di sola plastica, "
            "quindi non guadagni peso, e caricato da un punto solo si affloscia "
            "(freccia oltre 200 mm senza un labbro di irrigidimento, che a sua "
            "volta porta il peso a 110 g). In pi&ugrave; la tela tesa mette "
            "l'anello in compressione circonferenziale e lo fa imbozzare.")
    sp(2)
    p("<b>Se scegli uno spessore diverso da 3 mm</b>, rigenera il braccio "
      "prima di stamparlo. Vedi appendice E.")

    h2("0.7 &nbsp;Adattare il progetto al proprio tubo")
    p("I file STL nel repository sono generati per un tubo da <b>362 mm</b> di "
      "diametro esterno e un tappo da <b>374 mm</b>. Se il tuo tubo &egrave; "
      "diverso:")
    sp(3)
    table([
        ["Differenza", "Cosa fare"],
        ["fino a -7 mm (tubo pi&ugrave; piccolo)",
         "niente: la sella balla un po', riempi con EVA pi&ugrave; spessa"],
        ["oltre -7 mm, oppure tubo pi&ugrave; grande",
         "rigenera housing e tappo con il tuo valore. Vedi appendice E"],
    ], [50 * mm, CW - 50 * mm])
    sp(3)
    p("<b>Misura la circonferenza</b> con un metro flessibile da sarto nel "
      "punto di fissaggio e dividi per pi greco: su un tubo grande &egrave; "
      "molto pi&ugrave; preciso che usare un calibro. Il tappo deve essere "
      "circa 12 mm pi&ugrave; grande del tubo.")

    # =========================================================== PARTE A
    story.append(PageBreak())
    banner("Parte A - Meccanica",
           "dalla scatola stampata al gruppo motore-ingranaggi funzionante")

    callout("Tre cose da non fare, da qui in avanti.",
            "<b>1.</b> Non alimentare il 28BYJ-48 dal 5 V del Nano o dalla "
            "USB: assorbe pi&ugrave; di quanto il regolatore del Nano possa "
            "erogare, serve il buck con il GND in comune. &nbsp; "
            "<b>2.</b> Non collegare niente al buck prima di averlo regolato a "
            "5,00 V: un LM2596 nuovo esce spesso a 12 V e brucia Nano e "
            "sensori in un colpo solo. &nbsp; "
            "<b>3.</b> Non forzare mai il meccanismo a mano con il motore "
            "alimentato: con 960:1 di riduzione totale si spanano i denti "
            "stampati o si rompe il riduttore interno del 28BYJ.")

    step("A1", "Preparare i pezzi stampati", [
        "Togli i supporti e sbavatura i fori. I tre fori che contano sono: la "
        "sede dei cuscinetti 626ZZ nella parete e nel coperchio, e il foro "
        "dell'albero negli ingranaggi.",
        "Prova a secco i cuscinetti nelle loro sedi. Devono entrare decisi ma "
        "non a martellate: se serve, carteggia leggermente o scalda il pezzo "
        "con un phon.",
        "Prova a secco l'albero da 6 mm nei cuscinetti e nei mozzi.",
        "<b>Se hai stampato l'housing dai file V4.2 i fori ci sono gi&agrave; "
        "tutti</b>: non devi trapanare niente. Chi parte da un housing V4.1 "
        "deve invece fare quattro fori: vedi appendice F.",
    ])

    step("A2", "Montare la piastra dei sensori Hall - VA PER PRIMA", [
        "I dadi delle sue viti stanno <b>dentro</b> la scatola: dopo aver "
        "montato albero e ingranaggi non ci arrivi pi&ugrave;.",
        "Infila i due A3144 nelle tasche ricavate nello spessore della piastra. "
        "La <b>faccia marcata</b> del sensore deve guardare verso l'interno "
        "della scatola, cio&egrave; verso il magnete.",
        "Salda i fili prima di infilare i sensori: dentro la scatola non hai "
        "spazio. Salda anche i due condensatori da 100 nF fra VCC e GND, il "
        "pi&ugrave; vicino possibile al corpo del sensore.",
        "Lascia i cavi lunghi almeno 40 cm: devono uscire dalla scatola e "
        "arrivare all'elettronica.",
        "Fissa con due M3x16 e rondella dall'esterno, dado all'interno. "
        "<b>Lascia le asole a met&agrave; corsa</b>: servono per la taratura "
        "del passo C1.",
        "La piastra resta staccata di 2,6 mm dalla parete: &egrave; voluto, "
        "deve scavalcare il boss del cuscinetto.",
    ], fig="F04_piastra_hall.png", figw=98 * mm,
        figcap="FIG. 2 - piastra dei sensori in posizione, vista dall'interno "
               "della scatola")

    step("A3", "Cuscinetti", [
        "Inserisci un 626ZZ nella sede della parete, spingendolo "
        "<b>dall'esterno</b>: uno spallamento interno lo trattiene.",
        "Inserisci il secondo 626ZZ nel boss del coperchio, anch'esso "
        "dall'esterno.",
        "Se ballano, una goccia di frenafiletti sul diametro esterno.",
    ])

    step("A4", "Albero di uscita", [
        "Infila l'albero da 6 x 100 mm attraverso il cuscinetto della parete, "
        "da fuori verso dentro.",
        "Deve sporgere <b>circa 19 mm dal lato esterno</b> (ci va il braccio) e "
        "arrivare a filo del secondo cuscinetto dal lato del coperchio.",
        "Controlla che ruoti libero, senza gioco assiale apprezzabile.",
    ], fig="F05_albero.png", figw=98 * mm,
        figcap="FIG. 3 - albero e bandierina del magnete montati")

    step("A5", "Bandierina del magnete", [
        "Incolla il magnete 6x3 nella sua tasca. Se temi di sbagliare "
        "polarit&agrave;, <b>non incollarlo ancora</b>: tienilo a pressione e "
        "decidi dopo la prova del passo C1.",
        "Infila la bandierina sull'albero, magnete rivolto verso i sensori, a "
        "<b>11 mm dalla faccia interna della parete</b>.",
        "Ruotala a mano su tutta la corsa: deve passare davanti ai sensori "
        "senza toccarli. La luce di progetto &egrave; 2,9 mm.",
        "Stringi il grano M3.",
    ])

    step("A6", "Ingranaggio di uscita 70T", [
        "Infila l'ingranaggio da 70 denti sull'albero, mozzo rivolto verso il "
        "coperchio.",
        "Allinea la dentatura con quella del pignone piccolo del composto, che "
        "monterai al passo successivo.",
        "Stringi la vite M3 radiale sul mozzo.",
    ], fig="F06_ruote.png", figw=98 * mm,
        figcap="FIG. 4 - ingranaggio di uscita in posizione")

    step("A7", "Ingranaggio composto 42T/14T", [
        "Pianta il 625ZZ nella sede ricavata nel lato 42T: entra dal lato "
        "esterno e appoggia su uno spallamento sottile.",
        "Infila il composto sul perno M5, con una <b>rondella PTFE o nylon</b> "
        "fra il composto e la parete.",
        "Il perno M5 attraversa la parete e il coperchio: blocca con rondelle e "
        "dado autobloccante, <b>senza stringere</b>. Il composto deve girare "
        "libero sul perno.",
        "Controlla a mano l'ingranamento 14/70: il composto deve trascinare "
        "l'ingranaggio di uscita senza punti duri.",
    ])

    step("A8", "Staffa del motore", [
        "Si posiziona da sola: spingila contemporaneamente <b>contro il "
        "soffitto</b> della cavit&agrave;, <b>contro la parete dei cuscinetti</b> "
        "e <b>fra i due boss superiori</b> del coperchio. In quella posizione i "
        "fori della flangia cadono sui due fori del tetto.",
        "Inserisci a caldo i due inserti filettati M3 nelle sedi sulla faccia "
        "superiore della flangia, tenendoli in verticale, senza affondare.",
        "Fissa con due M3x10 avvitate <b>dall'esterno del tetto</b>, stringendo "
        "gradualmente e alternando.",
        "Il foro grande in basso sulla piastra &egrave; la luce per il mozzo "
        "dell'ingranaggio composto: deve restare libero.",
    ], fig="F07_staffa.png", figw=98 * mm,
        figcap="FIG. 5 - staffa del motore montata (in verde)")

    figure("F13_staffa_pezzo.png", 104 * mm,
           "FIG. 6 - la staffa da sola. La flangia in alto va a contatto col "
           "soffitto della scatola; i due fori asolati sulla piastra verticale "
           "servono a registrare l'interasse del motore")

    step("A9", "Motore e pignone", [
        "Il corpo del 28BYJ-48 passa <b>attraverso il foro grande</b> della "
        "piastra; le due orecchie si appoggiano sulla faccia opposta.",
        "Fissa con due M3x12 e rondelle nelle asole. <b>Non stringere "
        "ancora</b>.",
        "Infila il pignone 14T sull'albero del motore. Il foro &egrave; "
        "volutamente stretto: allargalo con una lima a D finch&eacute; entra a "
        "pressione, senza gioco.",
        "Il pignone deve arrivare quasi a filo della faccia della staffa, "
        "cos&igrave; da impegnare tutta la lunghezza utile dell'albero motore.",
    ], fig="F08_motore.png", figw=98 * mm,
        figcap="FIG. 7 - motore e pignone montati sulla staffa")

    step("A10", "Registrare l'ingranamento 14/42", [
        "&Egrave; il motivo per cui i fori del motore sono asolati: "
        "l'interasse si regola a mano e non dipende dalle tolleranze di stampa.",
        "Spingi il motore nelle asole finch&eacute; il pignone ingrana col 42T "
        "<b>senza gioco eccessivo e senza forzare</b>. Deve restare un filo di "
        "gioco percepibile.",
        "Stringi le due M3x12.",
        "Troppo stretto: il motore fatica e stalla. Troppo lasco: i denti "
        "saltano sotto carico.",
    ])

    step("A11", "Verifica a mano - non saltare questo passo", [
        "Ruota l'albero di uscita a mano su tutta la corsa, lentamente.",
        "Tutto il treno deve girare <b>libero, senza punti duri e senza rumore "
        "di raschiamento</b>.",
        "Un punto duro periodico significa interasse troppo stretto su quella "
        "coppia; gioco e scatti significano interasse troppo largo.",
        "Controlla anche che la bandierina non tocchi la piastra dei sensori in "
        "nessuna posizione.",
        "<b>Solo quando il meccanismo gira bene a mano</b> ha senso collegare "
        "l'elettronica.",
    ])

    # =========================================================== PARTE B
    story.append(PageBreak())
    banner("Parte B - Elettronica",
           "alimentazione, cablaggio, sensori, firmware, prova a banco")

    figure("F10_cablaggio.png", CW, "FIG. 8 - schema di cablaggio completo")

    step("B1", "Regolare il buck LM2596 - prima di tutto il resto", [
        "Collega <b>solo</b> il buck all'alimentazione 12 V, attraverso il "
        "fusibile. Nient'altro a valle.",
        "Con il multimetro sull'uscita, gira il trimmer finch&eacute; leggi "
        "<b>5,00 V</b> (accettabile fra 4,95 e 5,10).",
        "Il trimmer &egrave; multigiro: servono parecchi giri, non forzarlo a "
        "fondo corsa.",
        "Solo a questo punto stacca l'alimentazione e collega il resto.",
    ])

    step("B2", "Bus 5 V e GND", [
        "Realizza due nodi di distribuzione (morsettiera o WAGO): uno per il "
        "<b>+5 V</b>, uno per il <b>GND</b>. Dal buck partono entrambi.",
        "Al bus 5 V si attaccano la scheda ULN2003 e i sensori Hall. Al bus GND "
        "gli stessi <b>pi&ugrave; il GND dell'Arduino</b>.",
        "Monta il condensatore da 1000 uF fra i due bus, il pi&ugrave; vicino "
        "possibile alla ULN2003, rispettando la polarit&agrave;.",
        "Il Nano resta alimentato dalla sua USB. Il GND in comune &egrave; "
        "obbligatorio: senza, i segnali dei sensori non hanno riferimento.",
    ])

    step("B3", "Nano verso ULN2003", [
        "D2 -&gt; IN1, D3 -&gt; IN2, D4 -&gt; IN3, D5 -&gt; IN4.",
        "Il 28BYJ-48 si innesta sulla ULN2003 con il suo connettore a 5 poli "
        "(4 fasi pi&ugrave; comune): non c'&egrave; niente da cablare.",
        "Alimenta la ULN2003 dal bus 5 V, non dal Nano.",
    ])

    step("B4", "Sensori Hall", [
        "Guardando l'A3144 dal lato della <b>faccia marcata</b>, con i reofori "
        "in basso: pin 1 = VCC, pin 2 = GND, pin 3 = uscita.",
        "VCC e GND ai rispettivi bus, 100 nF fra i due vicinissimo al corpo del "
        "sensore.",
        "Uscita del sensore <b>CLOSED</b> (sede a 0 gradi) -&gt; <b>D10</b>. "
        "Uscita del sensore <b>OPEN</b> (sede a 90 gradi) -&gt; <b>D11</b>.",
        "Il firmware usa INPUT_PULLUP: non servono resistenze esterne. Il "
        "sensore deve <b>portare il pin a GND</b> quando il magnete gli passa "
        "davanti.",
    ])

    step("B5", "Caricare il firmware", [
        "Apri <i>firmware/GP1_Alnitak_DustCover_V4_2/</i> nell'IDE Arduino.",
        "Scheda: Arduino Nano. Processore: ATmega328P, oppure <i>ATmega328P "
        "(Old Bootloader)</i> se il caricamento fallisce.",
        "Lo sketch occupa circa 3,6 kB di flash e 261 byte di RAM: ci sta "
        "comodamente su un Nano.",
        "Non modificare nulla al primo caricamento. In particolare <b>non "
        "alzare MAX_MOVE_STEPS</b>: &egrave; un limite meccanico, vedi "
        "appendice D.",
        "Apri il monitor seriale a <b>9600 baud</b>, terminatore <b>Nuova riga "
        "(LF)</b>.",
    ])

    step("B6", "Prova a banco, motore scollegato dalla meccanica", [
        "Prima di accoppiare il motore agli ingranaggi, verifica che "
        "l'elettronica risponda ai comandi della tabella qui sotto.",
        "Con il motore innestato sulla ULN2003 ma <b>non</b> accoppiato al "
        "treno, mandando <font face='Courier'>&gt;O000</font> l'albero deve "
        "girare per una ventina di secondi e poi fermarsi in timeout (stato 3), "
        "perch&eacute; nessun sensore scatta.",
        "Avvicinando il magnete a mano al sensore OPEN durante il movimento, il "
        "motore si deve fermare subito e lo stato deve diventare 2.",
        "Se il motore vibra ma non gira, hai invertito due fili: controlla "
        "l'ordine IN1-IN4.",
    ])
    table([
        ["Comando", "Risposta attesa", "Significato"],
        ["&gt;P000", "*P98000", "ping: risponde il product ID 98"],
        ["&gt;V000", "*V98120", "versione del firmware"],
        ["&gt;S000", "*S98xyz", "stato (vedi sotto)"],
        ["&gt;O000", "*O98000", "apri"],
        ["&gt;C000", "*C98000", "chiudi"],
    ], [26 * mm, 34 * mm, CW - 60 * mm])
    table([
        ["Cifra", "Posizione", "Valori"],
        ["x", "motore", "0 = fermo, 1 = in movimento"],
        ["y", "luce", "sempre 0 (il product 98 non ha pannello flat)"],
        ["z", "tappo", "0 = intermedio, 1 = chiuso, 2 = aperto, 3 = timeout o errore"],
    ], [16 * mm, 26 * mm, CW - 42 * mm])

    # =========================================================== PARTE C
    story.append(PageBreak())
    banner("Parte C - Integrazione",
           "taratura, chiusura, braccio, tappo, montaggio sul telescopio")

    step("C1", "Taratura dei sensori, a scatola aperta", [
        "Scatola aperta, coperchio non montato, meccanica completa, elettronica "
        "collegata.",
        "Ruota a mano l'albero fino alla posizione di <b>tappo chiuso</b>. "
        "Manda <font face='Courier'>&gt;S000</font>: l'ultima cifra deve essere "
        "<b>1</b>.",
        "Se resta 0, il sensore CLOSED non scatta: <b>prima prova a girare il "
        "magnete di 180 gradi</b> nella sua tasca. L'A3144 &egrave; unipolare e "
        "risponde a una sola faccia.",
        "Se ancora non scatta, allenta le due viti della piastra e ruotala "
        "leggermente nelle asole, poi ristringi.",
        "Ripeti per la posizione aperta: ruota di 90 gradi, l'ultima cifra deve "
        "diventare <b>2</b>.",
        "Le asole ruotano <b>entrambi</b> i sensori insieme. Regola sul CLOSED, "
        "che &egrave; quello che deve essere preciso: l'OPEN segue a 90 gradi "
        "esatti per costruzione.",
        "Quando sei soddisfatto, incolla definitivamente il magnete.",
    ])

    step("C2", "Verso di rotazione", [
        "Manda <font face='Courier'>&gt;O000</font> partendo da chiuso: il "
        "braccio deve muoversi <b>in apertura</b>, allontanandosi dal tubo.",
        "Se va al contrario, nel firmware metti <font face='Courier'>"
        "MOTOR_REVERSED = true</font> e ricarica.",
        "Cronometra la corsa completa: deve durare <b>circa 19 secondi</b>. "
        "Molto di pi&ugrave; significa passi persi.",
    ])

    step("C3", "Chiusura del coperchio", [
        "Inserisci i 4 inserti M3 a caldo nei boss della scatola.",
        "Controlla un'ultima volta che il treno giri libero e che i cavi non "
        "finiscano fra gli ingranaggi. Fermali con una fascetta.",
        "Chiudi con le 4 viti M3x10, serrando a croce.",
    ])

    step("C4", "Monobraccio", [
        "Infila il mozzo del braccio sull'estremit&agrave; esterna dell'albero. "
        "Il mozzo &egrave; a morsetto: entra libero.",
        "Posizionalo lasciando <b>2 mm di luce fra il mozzo e il boss del "
        "cuscinetto</b>.",
        "Orienta il braccio: a tappo chiuso la piastra deve essere parallela al "
        "piano del tappo, rivolta in avanti.",
        "Stringi la vite M3 del morsetto, con il dado nella sua sede esagonale. "
        "Serra deciso: &egrave; questo morsetto che trasmette tutta la coppia.",
    ], fig="F09_braccio.png", figw=104 * mm,
        figcap="FIG. 9 - monobraccio e contropiastra montati sull'albero")

    step("C5", "Preparare e fissare il tappo", [
        "Taglia il disco del diametro giusto (374 mm con i valori di default) "
        "nel materiale scelto al capitolo 0.6. Un compasso improvvisato con uno "
        "spago e una puntina &egrave; pi&ugrave; preciso di quanto sembri.",
        "Se usi polipropilene alveolare, orienta le nervature interne in "
        "direzione <b>radiale</b>, lungo la linea che va dall'attacco del "
        "braccio al bordo opposto.",
        "Appoggia la piastra del braccio sul disco e <b>usala come dima</b> per "
        "i 4 fori Ø4,5.",
        "Inserisci i 4 dadi M4 nelle sedi esagonali sotto le piazzole del "
        "braccio.",
        "Serra le 4 viti M4x16 dal lato cielo, con la contropiastra e rondelle "
        "larghe. <b>Non strizzare</b>: il materiale del tappo si schiaccia e "
        "perdi il serraggio.",
    ])

    step("C6", "Montaggio sul telescopio", [
        "Misura la circonferenza reale del tubo nel punto di fissaggio e "
        "dividi per pi greco (vedi 0.7).",
        "<b>Scegli la posizione angolare prima di stringere.</b> La sella copre "
        "solo 43 gradi di arco e puoi ruotare tutto il gruppo attorno al tubo: "
        "la cinematica non cambia. Su molti newtoniani focheggiatore e "
        "cercatore stanno vicino alla bocca del tubo, proprio dove va la sella.",
        "Metti 3-4 mm di EVA fra sella e tubo e stringi le due cinghie.",
        "<b>Ribilancia la montatura</b>: hai aggiunto 400-500 g in punta al "
        "tubo. Controlla anche che le fascette non slittino.",
    ])

    step("C7", "Ekos / INDI", [
        "Driver: <b>Alnitak Remote Dust Cover</b> / <b>Flip Flat</b> "
        "(<font face='Courier'>indi_flipflat</font>), porta seriale del Nano a "
        "9600 baud.",
        "Park = chiuso. Unpark = aperto.",
        "<b>Il tappo non va azionato durante la sessione</b>: si apre dopo aver "
        "sparcheggiato e si chiude prima di riparcheggiare, oppure viceversa a "
        "telescopio parcheggiato. La coppia richiesta dipende da quanto &egrave; "
        "alto il tubo in quel momento: vedi appendice B.",
    ])

    step("C8", "Collaudo finale", [
        "Cicla apertura e chiusura almeno 10 volte di seguito da Ekos: lo stato "
        "finale deve essere sempre 1 o 2, mai 3.",
        "Ripeti con il tubo alle altezze a cui lo parcheggi davvero.",
        "Controlla a tappo aperto che il disco non tocchi la scatola: la luce "
        "di progetto a fine corsa &egrave; circa 7,7 mm.",
        "Verifica che il tappo chiuso copra tutta l'apertura senza spiragli.",
        "Lascia il sistema fermo a tappo aperto per qualche minuto e controlla "
        "che non scenda da solo.",
    ])
    figure("F12_tappo_aperto.png", 100 * mm,
           "FIG. 10 - posizione di fine apertura, 90 gradi")

    # =========================================================== APPENDICI
    story.append(PageBreak())
    banner("Appendici")

    h2("A. &nbsp;Comandi seriali (protocollo Alnitak)")
    p("9600 8N1, comandi terminati da LF. Il firmware emula il product ID 98, "
      "Remote Dust Cover.")
    sp(3)
    table([
        ["Comando", "Risposta", "Effetto"],
        ["&gt;P000", "*P98000", "ping"],
        ["&gt;O000", "*O98000", "apri il tappo"],
        ["&gt;C000", "*C98000", "chiudi il tappo"],
        ["&gt;S000", "*S98xyz", "stato: x motore, y luce, z tappo"],
        ["&gt;V000", "*V98120", "versione del firmware"],
        ["&gt;J000", "*J98000", "luminosit&agrave; (non usata)"],
    ], [26 * mm, 30 * mm, CW - 56 * mm])

    h2("B. &nbsp;Coppia e posizione di park")
    p("La coppia che serve per staccare il tappo dipende da quanto &egrave; "
      "alto il tubo nel momento in cui il tappo si muove. Il caso peggiore "
      "&egrave; sempre l'<b>istante di distacco in apertura</b>, a tappo "
      "ancora chiuso.")
    sp(3)
    p("Coppia disponibile stimata: 28BYJ-48 a circa 12 giri/min in uscita "
      "(~30 mN&middot;m) per la riduzione stampata 15:1, con rendimento 0,72 su "
      "due stadi = <b>circa 0,32 N&middot;m</b>.")
    sp(4)
    p("<b>Margine di coppia per altezza del tubo sopra l'orizzonte</b> "
      "(valori sotto 1,00: il tappo non si apre)")
    sp(3)
    table([
        ["Materiale del tappo", "0 deg", "15 deg", "30 deg", "45 deg",
         "60 deg", "90 deg"],
        ["Forex 1,5 mm", "4,64", "2,54", "1,82", "1,48", "1,32", "1,28"],
        ["Forex 2 mm", "3,98", "2,10", "1,49", "1,21", "1,07", "1,04"],
        ["Forex 3 mm", "3,10", "1,57", "1,10",
         "<font color='#c0392b'>0,88</font>",
         "<font color='#c0392b'>0,78</font>",
         "<font color='#c0392b'>0,76</font>"],
        ["Alveolare PP 3 mm", "5,78", "3,36", "2,46", "2,03", "1,81", "1,76"],
        ["Depron 6 mm", "7,17", "4,52", "3,41", "2,85", "2,57", "2,50"],
    ], [44 * mm] + [(CW - 44 * mm) / 6] * 6,
        align={i: "CENTER" for i in range(1, 7)})
    sp(2)
    callout("Come usare questa tabella.",
            "Guarda l'altezza a cui parcheggi il telescopio, non quella a cui "
            "fotografi: il tappo si muove solo da fermo, prima di sparcheggiare "
            "e dopo aver parcheggiato. Con il <b>Forex 3 mm il limite &egrave; "
            "36 gradi di altezza</b>: sopra, non apre. Con l'alveolare da 3 mm "
            "il margine resta sopra 1,7 in qualsiasi posizione. Se parcheggi "
            "puntando la polare, ricordati che l'altezza della polare &egrave; "
            "uguale alla tua latitudine.")
    sp(2)
    p("Da circa -78 gradi di corsa in poi la gravit&agrave; aiuta l'apertura, "
      "quindi il tappo resta appoggiato aperto senza caricare il finecorsa.",
      "small")

    story.append(PageBreak())
    h2("C. &nbsp;Diagnostica")
    table([
        ["Sintomo", "Causa probabile", "Cosa fare"],
        ["Il motore vibra ma non gira", "ordine delle fasi sbagliato",
         "controlla D2-D5 verso IN1-IN4"],
        ["Gira nel verso sbagliato", "-",
         "MOTOR_REVERSED = true nel firmware"],
        ["Lo stato resta sempre 0", "nessun sensore scatta",
         "gira il magnete di 180 gradi, poi registra le asole della piastra"],
        ["Stato 3 a fine corsa",
         "il sensore di destinazione non ha scattato",
         "traferro troppo grande o magnete debole: verifica i 2,9 mm"],
        ["Stato 3 dopo pochi secondi", "passi persi o stallo",
         "controlla che il treno giri libero a mano; tappo pi&ugrave; leggero; "
         "parcheggia il tubo pi&ugrave; basso"],
        ["Apre solo con il tubo basso", "margine di coppia insufficiente",
         "&egrave; il caso del Forex 3 mm: vedi appendice B e capitolo 0.6"],
        ["Rumore ciclico dagli ingranaggi", "interasse motore troppo stretto",
         "riapri e rifai il passo A10"],
        ["Il tappo chiuso non appoggia piano", "flessione del disco",
         "normale con Forex 1,5 mm; passa a 3 mm o ad alveolare"],
        ["La sella balla sul tubo", "tubo pi&ugrave; piccolo di 362 mm",
         "EVA pi&ugrave; spessa, oppure rigenera l'housing: appendice E"],
    ], [40 * mm, 42 * mm, CW - 82 * mm])

    h2("D. &nbsp;Limiti verificati")
    p("Tutte le luci qui sotto sono misurate sulle mesh STL reali, non stimate. "
      "Lo script che le produce &egrave; <font face='Courier'>"
      "docs/verifica_collisioni.py</font> e si rilancia dopo ogni modifica.")
    sp(4)
    table([
        ["Grandezza", "Valore"],
        ["Luce disco tappo - scatola, a fine apertura", "7,7 mm"],
        ["Luce disco tappo - scatola, a tappo chiuso", "10,1 mm"],
        ["Luce monobraccio - scatola, su tutta la corsa", "2,0 mm"],
        ["Luce monobraccio - anello frontale del tubo", "2,5 mm"],
        ["Luce piastra sensori - bandierina (= traferro magnetico)", "2,9 mm"],
        ["Luce staffa - ingranaggio composto", "1,0 mm"],
        ["Corsa nominale", "7.642 passi full-step (90 gradi)"],
        ["<b>MAX_MOVE_STEPS</b>", "<b>8.100</b>"],
    ], [CW - 40 * mm, 40 * mm])
    callout("Perch&eacute; MAX_MOVE_STEPS non va alzato.",
            "Se il sensore OPEN non scatta, il conteggio dei passi &egrave; "
            "l'unica cosa che impedisce al tappo di sbattere contro la scatola. "
            "A 8.100 passi si ferma a -95,4 gradi, dove restano circa 4,6 mm di "
            "luce. A 8.500 passi sarebbe a -100 gradi con 2 mm, a 8.900 passi a "
            "-105 gradi con 0,5 mm. Nell'altro verso non serve protezione: "
            "chiudendo oltre lo zero il tappo va in appoggio sull'anello "
            "frontale del tubo, che fa da fermo meccanico.")

    story.append(PageBreak())
    h2("E. &nbsp;Rigenerare i pezzi per un tubo o un tappo diversi")
    p("Serve OpenSCAD (la libreria MCAD &egrave; inclusa nell'installazione). "
      "Tutti i parametri stanno in testa a "
      "<font face='Courier'>gp1_flipcap_V4_2.scad</font>.")
    sp(4)
    table([
        ["Cosa cambi", "Cosa rigenerare", "Comando"],
        ["Diametro del tubo", "housing", "<font face='Courier' size='7.6'>"
         "openscad -o stl/housing.stl -D 'part=\"housing\"' -D ota_d=355 "
         "gp1_flipcap_V4_2.scad</font>"],
        ["Spessore del tappo", "mono_arm",
         "<font face='Courier' size='7.6'>openscad -o stl/mono_arm.stl "
         "-D 'part=\"mono_arm\"' -D lid_thickness=1.5 gp1_flipcap_V4_2.scad"
         "</font><br/>Con spessori oltre i 4 mm alza anche "
         "<font face='Courier'>arm_dz</font> (da 42 a 44), altrimenti la "
         "piastra del braccio si avvicina troppo all'anello frontale del tubo"],
        ["Diametro del tappo", "nessun pezzo stampato",
         "&egrave; solo la misura a cui tagli il disco "
         "(<font face='Courier'>lid_d</font>)"],
    ], [30 * mm, 28 * mm, CW - 58 * mm])
    sp(2)
    p("<b>Dopo ogni modifica rilancia la verifica</b>, che controlla su tutta "
      "la corsa: integrit&agrave; dei solidi, braccio contro scatola, staffa "
      "contro scatola e ingranaggi, disco del tappo contro scatola, braccio "
      "contro tubo, piastra sensori contro bandierina, ed extracorsa in avaria.")
    sp(3)
    p("<font face='Courier'>python docs/verifica_collisioni.py</font>")
    p("Richiede numpy e scipy.", "small")

    h2("F. &nbsp;Note per chi viene dalla V4.1")
    p("Chi ha gi&agrave; stampato l'housing dalla versione V4.1 pu&ograve; "
      "riutilizzarlo: la geometria esterna non &egrave; cambiata. Servono per&ograve; "
      "<b>quattro fori Ø3,4 mm</b> che nella V4.1 non c'erano, due sul tetto "
      "per la staffa del motore e due sulla parete per la piastra dei sensori.")
    sp(3)
    p("Il metodo sicuro &egrave; <b>usare i pezzi stampati come dima</b>: "
      "appoggia la staffa in posizione (spinta contro soffitto, parete e i due "
      "boss del coperchio) e segna col punteruolo attraverso i suoi fori; "
      "stessa cosa per la piastra dei sensori. Le quote sotto servono da "
      "controllo. Fora a bassa velocit&agrave; e senza spingere.")
    sp(4)
    ui.figure_pair("F02_fori_tetto.png",
                   "FIG. 11 - i due fori del tetto (staffa motore)",
                   "F03_fori_parete.png",
                   "FIG. 12 - i due fori della parete (piastra sensori)")
    p("Restano da rifare comunque: <b>monobraccio</b> (quello V4.1 compenetra "
      "la scatola su tutta la corsa), <b>contropiastra</b> (nuovo schema a 4 "
      "fori) e i <b>supporti dei sensori</b>, sostituiti dalla piastra unica. "
      "La <b>staffa del motore</b> &egrave; un pezzo nuovo: nella V4.1 la "
      "piastra di supporto del motore era un solido staccato, sospeso in aria "
      "dentro la scatola. I dettagli sono in "
      "<font face='Courier'>CHANGELOG_V4.2.md</font>.")
    sp(10)
    p("<i>Documento generato automaticamente. Le figure sono prodotte dal "
      "modello parametrico e dalle mesh esportate: "
      "docs/genera_figure_manuale.py compone le immagini, "
      "docs/genera_manuale_pdf.py impagina il PDF, docs/contenuto_manuale.py "
      "contiene il testo.</i>", "small")
