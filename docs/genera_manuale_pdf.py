#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) 2026 Johannes1979I
"""
GP1 FlipCap V4.2 - genera il manuale di montaggio in PDF.

Uso:  python docs/genera_manuale_pdf.py
Esce: MANUALE_MONTAGGIO_V4.2.pdf nella radice del progetto.

Le figure devono esistere in docs/manuale/ (le crea genera_figure_manuale.py).
Richiede: reportlab, pillow.

NOTA sui caratteri: i font standard del PDF usano WinAnsiEncoding. Niente
frecce unicode, niente segni di spunta, niente >= : usare ->, "ok", ">=".
"""
import os
import sys

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "docs", "manuale")
OUT = os.path.join(ROOT, "MANUALE_MONTAGGIO_V4.2.pdf")

INK = colors.HexColor("#1b2b3a")
ACC = colors.HexColor("#1f6fb2")
WARN = colors.HexColor("#c0392b")
OKC = colors.HexColor("#1e8449")
GREY = colors.HexColor("#5a6b7a")
BG = colors.HexColor("#eef3f7")
BGW = colors.HexColor("#fdecea")
BGO = colors.HexColor("#eaf3ea")

MARGIN = 18 * mm
CW = A4[0] - 2 * MARGIN          # larghezza utile ~174 mm

ss = getSampleStyleSheet()
S = {}
S["h1"] = ParagraphStyle("h1", parent=ss["Normal"], fontName="Helvetica-Bold",
                         fontSize=19, leading=23, textColor=colors.white,
                         spaceAfter=0)
S["h2"] = ParagraphStyle("h2", parent=ss["Normal"], fontName="Helvetica-Bold",
                         fontSize=13.5, leading=17, textColor=INK,
                         spaceBefore=10, spaceAfter=5)
S["step"] = ParagraphStyle("step", parent=ss["Normal"],
                           fontName="Helvetica-Bold", fontSize=11.5,
                           leading=14.5, textColor=INK)
S["body"] = ParagraphStyle("body", parent=ss["Normal"], fontName="Helvetica",
                           fontSize=9.6, leading=13.4, textColor=INK,
                           alignment=TA_JUSTIFY)
S["bodyc"] = ParagraphStyle("bodyc", parent=S["body"], alignment=TA_CENTER)
S["small"] = ParagraphStyle("small", parent=S["body"], fontSize=8.4,
                            leading=11.2, textColor=GREY)
S["cap"] = ParagraphStyle("cap", parent=S["small"], alignment=TA_CENTER,
                          spaceBefore=2)
S["cell"] = ParagraphStyle("cell", parent=ss["Normal"], fontName="Helvetica",
                           fontSize=8.6, leading=11, textColor=INK)
S["cellb"] = ParagraphStyle("cellb", parent=S["cell"],
                            fontName="Helvetica-Bold")
S["cover1"] = ParagraphStyle("cover1", parent=ss["Normal"],
                             fontName="Helvetica-Bold", fontSize=30,
                             leading=35, textColor=INK, alignment=TA_CENTER)
S["cover2"] = ParagraphStyle("cover2", parent=ss["Normal"],
                             fontName="Helvetica", fontSize=13, leading=18,
                             textColor=GREY, alignment=TA_CENTER)

story = []


# ------------------------------------------------------------------ elementi
def h2(text):
    story.append(Paragraph(text, S["h2"]))


def p(text, style="body"):
    story.append(Paragraph(text, S[style]))


def sp(h=4):
    story.append(Spacer(1, h))


def banner(text, sub=""):
    """Barra di titolo di una parte del manuale."""
    inner = [[Paragraph(text, S["h1"])]]
    if sub:
        inner.append([Paragraph(
            '<font color="#d6e4f0" size="9.5">%s</font>' % sub, S["h1"])])
    t = Table(inner, colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), INK),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 9),
        ("TOPPADDING", (0, 1), (-1, -1), 0),
    ]))
    story.append(t)
    sp(9)


def step(num, title, lines, fig=None, figw=None, figcap=None, keep=True):
    """Un passo numerato: pallino col numero, titolo, elenco puntato."""
    badge = Table([[Paragraph(
        '<font color="white" size="12"><b>%s</b></font>' % num, S["cell"])]],
        colWidths=[13 * mm], rowHeights=[9 * mm])
    badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACC),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    body = [Paragraph(title, S["step"]), Spacer(1, 3)]
    for ln in lines:
        body.append(Paragraph("&bull;&nbsp;&nbsp;" + ln, S["body"]))
        body.append(Spacer(1, 1.5))
    head = Table([[badge, body]], colWidths=[16 * mm, CW - 16 * mm])
    head.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 3),
        ("LEFTPADDING", (1, 0), (1, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    block = [head, Spacer(1, 6)]
    if fig:
        block += _figure(fig, figw or 110 * mm, figcap)
        story.append(KeepTogether(block))
    else:
        for b in block:
            story.append(b)


def _figure(name, width, caption=None):
    path = os.path.join(FIG, name)
    if not os.path.exists(path):
        return [Paragraph("[figura mancante: %s]" % name, S["small"])]
    iw, ih = PILImage.open(path).size
    img = Image(path, width=width, height=width * ih / iw)
    out = [img]
    if caption:
        out.append(Paragraph(caption, S["cap"]))
    out.append(Spacer(1, 8))
    tw = Table([[o] for o in out], colWidths=[CW])
    tw.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return [tw]


def figure(name, width=115 * mm, caption=None):
    for el in _figure(name, width, caption):
        story.append(el)


def figure_pair(n1, c1, n2, c2, width=82 * mm):
    """Due figure affiancate, per non sprecare mezza pagina a testa."""
    def cell(name, cap):
        path = os.path.join(FIG, name)
        iw, ih = PILImage.open(path).size
        img = Image(path, width=width, height=width * ih / iw)
        t = Table([[img], [Paragraph(cap, S["cap"])]], colWidths=[width])
        t.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        return t

    outer = Table([[cell(n1, c1), cell(n2, c2)]],
                  colWidths=[CW / 2, CW / 2])
    outer.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(outer)
    sp(8)


def callout(title, text, kind="warn"):
    fc, ec = (BGW, WARN) if kind == "warn" else (
        (BGO, OKC) if kind == "ok" else (BG, ACC))
    t = Table([[Paragraph('<b><font color="#%s">%s</font></b>&nbsp; %s'
                          % (ec.hexval()[2:], title, text), S["body"])]],
              colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fc),
        ("BOX", (0, 0), (-1, -1), 0.9, ec),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    sp(7)


def table(rows, widths, header=True, align=None, fs=8.6):
    data = []
    for r_i, r in enumerate(rows):
        row = []
        for c in r:
            st = S["cellb"] if (header and r_i == 0) else S["cell"]
            row.append(Paragraph(str(c), st))
        data.append(row)
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c3d0db")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1),
         [colors.white, colors.HexColor("#f6f9fb")]),
    ]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), BG),
                  ("LINEBELOW", (0, 0), (-1, 0), 0.9, ACC)]
    if align:
        for col, a in align.items():
            style.append(("ALIGN", (col, 0), (col, -1), a))
    t.setStyle(TableStyle(style))
    # le tabelle corte non si spezzano: due righe orfane a inizio pagina
    # sprecano mezza pagina e si leggono male
    story.append(KeepTogether([t]) if len(rows) <= 8 else t)
    sp(8)


# ------------------------------------------------------------------ pagina
def page_deco(canv, doc):
    canv.saveState()
    if doc.page > 1:
        canv.setStrokeColor(colors.HexColor("#c3d0db"))
        canv.setLineWidth(0.6)
        canv.line(MARGIN, A4[1] - MARGIN + 6, A4[0] - MARGIN, A4[1] - MARGIN + 6)
        canv.setFont("Helvetica", 7.6)
        canv.setFillColor(GREY)
        canv.drawString(MARGIN, A4[1] - MARGIN + 9,
                        "GP1 FlipCap V4.2 - Manuale di montaggio")
        canv.drawRightString(A4[0] - MARGIN, A4[1] - MARGIN + 9,
                             "pag. %d" % doc.page)
        canv.line(MARGIN, MARGIN - 8, A4[0] - MARGIN, MARGIN - 8)
        canv.setFont("Helvetica-Oblique", 7.2)
        canv.drawString(MARGIN, MARGIN - 15,
                        "Quote in mm. Verificare sempre il diametro reale "
                        "dell'OTA prima del fissaggio definitivo.")
    canv.restoreState()


# =========================================================== CONTENUTO
def build():
    # ---------------------------------------------------------- copertina
    story.append(Spacer(1, 26 * mm))
    story.append(Paragraph("GP1 FlipCap V4.2", S["cover1"]))
    sp(6)
    story.append(Paragraph("Manuale di montaggio", S["cover2"]))
    sp(2)
    story.append(Paragraph(
        "Tappo motorizzato per Sky-Watcher Quattro 300P f/4<br/>"
        "Meccanica &middot; Elettronica &middot; Integrazione", S["cover2"]))
    sp(10)
    figure("F01_assieme.png", 140 * mm)
    sp(4)
    callout("PRIMA DI COMINCIARE.",
            "Questo manuale presuppone che <b>housing, coperchio e i tre "
            "ingranaggi</b> siano gi&agrave; stampati dalla V4.1: quelle "
            "geometrie non sono cambiate. Vanno invece stampati ex novo la "
            "<b>staffa motore</b> e la <b>piastra sensori</b>, e ristampati "
            "<b>monobraccio</b> e <b>contropiastra</b>. Sull'housing servono "
            "4 fori. Tutto il dettaglio nel capitolo 0.")
    story.append(PageBreak())

    # ------------------------------------------------------------- indice
    banner("Indice")
    table([
        ["Capitolo", "Contenuto", "Pag."],
        ["<b>0. Prima di cominciare</b>",
         "Pezzi, viteria, attrezzi, scelta del materiale del tappo", "3"],
        ["<b>A. Meccanica</b>",
         "Forature, sensori, albero, ingranaggi, staffa, motore", "6"],
        ["<b>B. Elettronica</b>",
         "Schema, alimentazione, sensori, firmware, prova a banco", "12"],
        ["<b>C. Integrazione</b>",
         "Taratura, chiusura, braccio, tappo, montaggio su OTA, Ekos", "15"],
        ["<b>Appendici</b>",
         "Comandi seriali, coppie, diagnostica, limiti da non superare", "19"],
    ], [42 * mm, CW - 42 * mm - 16 * mm, 16 * mm],
        align={2: "CENTER"})
    callout("Come leggere i passi.",
            "Ogni passo &egrave; numerato progressivamente all'interno della "
            "sua parte (A1, A2, ... B1, ... C1, ...). <b>L'ordine conta</b>: "
            "alcuni componenti non sono pi&ugrave; raggiungibili dopo che ne "
            "sono stati montati altri. In particolare la piastra sensori va "
            "montata per prima e il tappo per ultimo.", kind="info")
    story.append(PageBreak())

    # =================================================== 0. PRIMA DI COMINCIARE
    banner("0. Prima di cominciare",
           "pezzi da stampare, minuteria, attrezzi, scelte da fare adesso")

    h2("0.1 &nbsp;Pezzi stampati")
    table([
        ["Pezzo", "Stato", "Volume", "Note di stampa"],
        ["housing.stl", "<font color='#1e8449'><b>gi&agrave; buono</b></font>",
         "251,5 cm3", "invariato dalla V4.1, servono solo 4 fori (passo A1)"],
        ["cover.stl", "<font color='#1e8449'><b>gi&agrave; buono</b></font>",
         "33,7 cm3", "invariato"],
        ["output_gear.stl", "<font color='#1e8449'><b>gi&agrave; buono</b></font>",
         "15,8 cm3", "invariato"],
        ["compound_gear.stl", "<font color='#1e8449'><b>gi&agrave; buono</b></font>",
         "4,9 cm3", "invariato"],
        ["motor_pinion.stl", "<font color='#1e8449'><b>gi&agrave; buono</b></font>",
         "0,5 cm3", "invariato"],
        ["magnet_flag.stl", "<font color='#1e8449'>gi&agrave; buono</font>",
         "1,9 cm3", "il pezzo V4.1 funziona: incolla il magnete nella tasca"],
        ["motor_bracket.stl", "<font color='#c0392b'><b>DA STAMPARE</b></font>",
         "33,8 cm3", "pezzo nuovo. Senza questo il motore non si monta"],
        ["mono_arm.stl", "<font color='#c0392b'><b>DA RISTAMPARE</b></font>",
         "54,6 cm3", "vedi 0.5: lo spessore del tappo cambia il pezzo"],
        ["lid_backplate.stl", "<font color='#c0392b'><b>DA RISTAMPARE</b></font>",
         "8,5 cm3", "nuovo schema a 4 fori"],
        ["hall_plate.stl", "<font color='#c0392b'><b>DA STAMPARE</b></font>",
         "3,5 cm3", "sostituisce i due hall_holder della V4.1"],
    ], [34 * mm, 26 * mm, 20 * mm, CW - 80 * mm])

    p("<b>Parametri di stampa.</b> PETG o ASA, layer 0,20 mm, 4-5 perimetri, "
      "30-40% di riempimento per staffa, braccio e contropiastra. La piastra "
      "sensori in piano, 3 perimetri, nessun supporto. Gli ingranaggi (se mai "
      "li rifacessi) vogliono layer 0,12-0,16 mm e almeno 5 perimetri.")
    sp(3)
    p("<b>Orientamenti consigliati.</b> <i>motor_bracket</i>: appoggiata sulla "
      "faccia grande della piastra motore, flangia in verticale, supporti solo "
      "sotto la flangia. <i>mono_arm</i>: mozzo sul piatto, piastra del tappo "
      "in alto, supporti sotto la piastra. <i>hall_plate</i>: faccia piatta "
      "sul piatto.")

    h2("0.2 &nbsp;Viteria e minuteria")
    table([
        ["Q.t&agrave;", "Componente", "Dove va"],
        ["1", "Albero acciaio 6 &times; 100 mm", "albero di uscita (la BOM V4.1 diceva 95: non basta)"],
        ["2", "Cuscinetto 626ZZ (6&times;19&times;6)", "parete sinistra e boss del coperchio"],
        ["1", "Cuscinetto 625ZZ (5&times;16&times;5)", "lato 42T dell'ingranaggio composto"],
        ["1", "Perno M5 &times; 80 + rondelle + dado autobloccante", "albero dell'ingranaggio composto"],
        ["1", "Rondella PTFE o nylon M5", "fra composto e parete sinistra"],
        ["4", "Inserti M3 + 4 viti M3&times;10", "coperchio scatola"],
        ["2", "Inserti M3 + 2 viti M3&times;10", "staffa motore, avvitata al tetto dall'esterno"],
        ["2", "Viti M3&times;12 + rondelle", "28BYJ-48 sulla staffa (asole di registrazione)"],
        ["2", "Viti M3&times;16 + rondelle + dadi", "piastra sensori sulla parete sinistra"],
        ["1", "Vite M3&times;25 + dado", "morsetto del mozzo del monobraccio"],
        ["1", "Grano o vite M3", "bandierina magnete sull'albero"],
        ["1", "Vite M3", "mozzo dell'ingranaggio di uscita sull'albero"],
        ["4", "Viti M4&times;16 + rondelle larghe + 4 dadi M4", "tappo sul monobraccio"],
        ["2", "Cinghie 25 mm &times; 1200 mm", "fissaggio all'OTA"],
        ["1", "Nastro EVA o gomma 3-4 mm", "fra sella e tubo"],
    ], [12 * mm, 62 * mm, CW - 74 * mm])

    h2("0.3 &nbsp;Elettronica")
    table([
        ["Q.t&agrave;", "Componente", "Nota"],
        ["1", "Arduino Nano (ATmega328P 5 V)", "CH340/USB-C vanno bene"],
        ["1", "28BYJ-48", "versione 5 V"],
        ["1", "Scheda ULN2003", "il motore ci si innesta col connettore a 5 poli"],
        ["1", "Buck LM2596", "12 V -> 5,0 V, almeno 2 A"],
        ["2", "Hall A3144 / AH3144", "interruttore unipolare: risponde a una sola polarit&agrave;"],
        ["1", "Magnete neodimio 6&times;3 mm", "N35 o superiore"],
        ["1", "Condensatore 1000 uF 10-16 V", "sul bus 5 V, vicino alla ULN2003"],
        ["2", "Condensatore 100 nF", "uno per sensore Hall"],
        ["1", "Fusibile 1-1,5 A + portafusibile", "lato 12 V"],
        ["1", "Connettore DC 5,5&times;2,1 o GX12-2", "ingresso alimentazione"],
        ["-", "Cavo 0,25-0,5 mm2 + termorestringente", ""],
    ], [12 * mm, 62 * mm, CW - 74 * mm])

    h2("0.4 &nbsp;Attrezzi")
    p("Trapano con punta da <b>3,4 mm</b> &middot; saldatore e stagno &middot; "
      "saldatore con punta per inserti filettati (o un saldatore vecchio) "
      "&middot; chiavi a brugola 2-2,5-3 mm &middot; chiave o bussola da 5,5 mm "
      "&middot; cutter e riga &middot; lima piatta piccola o lima a D &middot; "
      "multimetro &middot; metro flessibile da sarto &middot; un terminale "
      "seriale (Arduino IDE, PuTTY, minicom...).")

    story.append(PageBreak())

    h2("0.5 &nbsp;Decisione da prendere ADESSO: materiale del tappo")
    callout("Questa scelta cambia il file da stampare.",
            "Lo spessore del tappo determina la quota delle piazzole del "
            "monobraccio. Se cambi materiale <b>dopo</b> aver stampato il "
            "braccio, il braccio non va pi&ugrave; bene. Decidi prima, poi "
            "stampa.")
    table([
        ["Materiale", "Massa", "Freccia*", "Giudizio"],
        ["Forex / PVC espanso 1,5 mm",
         "82 g", "31 mm", "il default. Funziona, ma &egrave; il pi&ugrave; "
         "pesante e il pi&ugrave; flessibile dei tre"],
        ["<b>Polipropilene alveolare 3 mm</b>",
         "<b>50 g</b>", "<b>5 mm</b>",
         "<b>consigliato.</b> Impermeabile, robusto, si taglia col cutter. "
         "Orienta le nervature interne in direzione radiale, dall'attacco del "
         "braccio verso il bordo opposto"],
        ["Depron / XPS 6 mm",
         "23 g", "9 mm", "massa minima assoluta, ma fragile: una ditata lo "
         "ammacca. Solo per osservatorio fisso"],
        ["Cerchio stampato + tela", "78-110 g", "-",
         "<b>sconsigliato.</b> Non pesa meno, e un anello sottile da 374 mm "
         "caricato da un punto solo si affloscia (freccia stimata oltre 200 mm "
         "senza labbro di irrigidimento)"],
    ], [46 * mm, 16 * mm, 17 * mm, CW - 79 * mm])
    p("* freccia sotto peso proprio con il tubo allo zenit, sbalzo di 350 mm "
      "dall'attacco del braccio al bordo opposto. Meno massa significa anche "
      "pi&ugrave; margine di coppia: vedi appendice B.", "small")
    sp(4)
    p("<b>Se scegli uno spessore diverso da 1,5 mm</b>, rigenera il braccio "
      "prima di stamparlo:")
    sp(2)
    table([
        ["Materiale scelto", "Comando"],
        ["Forex 1,5 mm",
         "gli STL nella cartella <i>stl/</i> sono gi&agrave; cos&igrave;"],
        ["Alveolare 3 mm",
         "<font face='Courier'>openscad -o stl/mono_arm.stl -D 'part=\"mono_arm\"' "
         "-D lid_thickness=3 gp1_flipcap_V4_2.scad</font>"],
        ["Depron 6 mm",
         "<font face='Courier'>openscad -o stl/mono_arm.stl -D 'part=\"mono_arm\"' "
         "-D lid_thickness=6 -D arm_dz=44 gp1_flipcap_V4_2.scad</font><br/>"
         "(con 6 mm serve anche alzare arm_dz, altrimenti la piastra del "
         "braccio passa a 1 mm dall'anello frontale del tubo)"],
    ], [34 * mm, CW - 34 * mm])
    p("Dopo aver rigenerato, rilancia <font face='Courier'>python "
      "docs/verifica_collisioni.py</font> per confermare che le luci siano "
      "ancora buone.", "small")

    h2("0.6 &nbsp;Avvertenze generali")
    callout("Non alimentare mai il 28BYJ-48 dal 5 V del Nano o dalla USB.",
            "Lo stepper assorbe pi&ugrave; di quanto il regolatore del Nano "
            "possa dare. Serve il buck LM2596 con GND in comune.")
    callout("Regola il buck a 5,00 V <b>prima</b> di collegargli qualsiasi cosa.",
            "Un LM2596 nuovo esce spesso a 12 V o a tensione casuale: "
            "collegarlo com'&egrave; brucia il Nano e i sensori.")
    callout("Non forzare mai il meccanismo a mano con il motore alimentato.",
            "Il riduttore totale &egrave; di circa 960:1. Forzando il braccio "
            "si spanano i denti stampati o si rompe il riduttore interno del "
            "28BYJ.")

    # =========================================================== PARTE A
    story.append(PageBreak())
    banner("Parte A - Meccanica",
           "dalla scatola nuda al gruppo motore-ingranaggi funzionante")

    step("A1", "Preparare l'housing: quattro fori da 3,4 mm", [
        "Sull'housing gi&agrave; stampato servono 4 fori passanti Ø3,4 mm: "
        "due sul tetto per la staffa motore, due sulla parete del cuscinetto "
        "per la piastra sensori.",
        "<b>Il metodo pi&ugrave; sicuro &egrave; usare i pezzi stampati come dima</b>: "
        "appoggia la staffa in posizione (spinta contro soffitto, parete "
        "sinistra e i due boss del coperchio) e segna col punteruolo "
        "attraverso i suoi fori. Idem per la piastra sensori.",
        "Le quote delle figure 2 e 3 servono come controllo, non come metodo "
        "primario.",
        "Fora a bassa velocit&agrave;, senza spingere: il PETG si imbroda.",
        "I quattro fori della V4.1 per i vecchi supporti Hall restano "
        "inutilizzati: tappali con un pezzetto di nastro nero.",
        "La lastrina rettangolare uscita separata dalla stampa della V4.1 "
        "(la vecchia piastra motore sospesa in aria) &egrave; scarto: buttala.",
    ])
    figure_pair("F02_fori_tetto.png",
                "FIG. 2 - i due fori del tetto (staffa motore)",
                "F03_fori_parete.png",
                "FIG. 3 - i due fori della parete (piastra sensori)")

    step("A2", "Montare la piastra sensori Hall - VA PER PRIMA", [
        "I dadi delle sue viti stanno <b>dentro</b> la scatola: dopo aver "
        "montato albero e ingranaggi non ci arrivi pi&ugrave;.",
        "Infila i due A3144 nelle tasche ricavate nello spessore della "
        "piastra. La <b>faccia marcata</b> del sensore deve guardare verso "
        "l'interno della scatola, cio&egrave; verso il magnete.",
        "Salda i fili prima di infilare i sensori: dentro la scatola non hai "
        "spazio. Salda anche i due condensatori da 100 nF fra VCC e GND, il "
        "pi&ugrave; vicino possibile al chip.",
        "Lascia i cavi lunghi almeno 40 cm: usciranno dalla scatola verso la "
        "scatola elettronica.",
        "Fissa con due M3&times;16 e rondella dall'esterno, dado all'interno. "
        "<b>Lascia le asole a met&agrave; corsa</b>: serviranno per la "
        "taratura nel passo C1.",
        "La piastra resta staccata di 2,6 mm dalla parete: &egrave; voluto, "
        "deve scavalcare il boss del cuscinetto.",
    ], fig="F04_piastra_hall.png", figw=98 * mm,
        figcap="FIG. 4 - piastra sensori in posizione, vista dall'interno "
               "della scatola")

    step("A3", "Cuscinetti 626ZZ", [
        "Inserisci un 626ZZ nella sede della parete sinistra, spingendolo "
        "<b>dall'esterno</b>: lo spallamento interno lo trattiene.",
        "Inserisci il secondo 626ZZ nel boss del coperchio, anch'esso "
        "dall'esterno.",
        "Se entrano troppo duri, scalda leggermente il pezzo con un phon; se "
        "ballano, una goccia di frenafiletti sul diametro esterno.",
    ])

    step("A4", "Albero di uscita 6 &times; 100 mm", [
        "Infila l'albero attraverso il cuscinetto della parete sinistra, da "
        "fuori verso dentro.",
        "Deve sporgere <b>circa 19 mm dal lato sinistro</b> (per il "
        "monobraccio) e arrivare a filo del secondo cuscinetto dal lato del "
        "coperchio.",
        "Controlla che ruoti libero senza gioco assiale apprezzabile.",
    ], fig="F05_albero.png", figw=98 * mm,
        figcap="FIG. 5 - albero e bandierina magnete montati")

    step("A5", "Bandierina magnete", [
        "Incolla il magnete 6&times;3 nella tasca della bandierina. Se "
        "temi di sbagliare polarit&agrave;, <b>non incollarlo ancora</b>: "
        "tienilo a pressione e decidi dopo la prova del passo C1.",
        "Infila la bandierina sull'albero, magnete rivolto verso i sensori, "
        "e posizionala a <b>11 mm dalla faccia interna della parete "
        "sinistra</b>.",
        "Ruotala a mano su tutta la corsa: deve passare davanti ai sensori "
        "senza toccarli. La luce di progetto &egrave; 2,9 mm.",
        "Stringi il grano M3.",
    ])

    step("A6", "Ingranaggio di uscita 70T", [
        "Infila l'ingranaggio da 70 denti sull'albero, con il mozzo rivolto "
        "verso il coperchio.",
        "Posizionalo in modo che la dentatura sia allineata con quella del "
        "pignone piccolo del composto (che monterai al passo A7).",
        "Stringi la vite M3 radiale sul mozzo.",
    ], fig="F06_ruote.png", figw=98 * mm,
        figcap="FIG. 6 - ingranaggio di uscita 70T in posizione")

    step("A7", "Ingranaggio composto 42T/14T", [
        "Pianta il 625ZZ nella sede ricavata nel lato 42T del composto: entra "
        "dal lato esterno del 42T e appoggia su uno spallamento sottile.",
        "Infila il composto sul perno M5, con una <b>rondella PTFE o nylon</b> "
        "fra il composto e la parete sinistra.",
        "Il perno M5 attraversa la parete sinistra e il coperchio: blocca con "
        "rondelle e dado autobloccante, <b>senza stringere</b>. Il composto "
        "deve girare libero sul perno.",
        "Controlla a mano l'ingranamento 14/70: il composto deve trascinare "
        "l'ingranaggio di uscita senza punti duri.",
    ])

    step("A8", "Staffa motore", [
        "&Egrave; il pezzo nuovo della V4.2. Si autoallinea: spingila "
        "contemporaneamente <b>contro il soffitto</b> della cavit&agrave;, "
        "<b>contro la parete sinistra</b> e <b>fra i due boss superiori</b> "
        "del coperchio. In quella posizione i fori della flangia cadono "
        "esattamente sui due fori A e B fatti al passo A1.",
        "Inserisci a caldo i due inserti filettati M3 nelle sedi sulla faccia "
        "superiore della flangia, con il saldatore: tenuti in verticale, senza "
        "affondare.",
        "Fissa con due M3&times;10 avvitate <b>dall'esterno del tetto</b>. "
        "Stringi gradualmente, alternando.",
        "Il foro grande in basso sulla piastra &egrave; la luce per il mozzo "
        "dell'ingranaggio composto: deve restare libero.",
    ], fig="F07_staffa.png", figw=98 * mm,
        figcap="FIG. 7 - staffa motore montata (in verde)")

    figure("F13_staffa_pezzo.png", 104 * mm,
           "FIG. 8 - la staffa motore da sola: la flangia in alto va a "
           "contatto col soffitto, i due fori asolati sulla piastra verticale "
           "servono a registrare l'interasse del motore")

    step("A9", "Motore 28BYJ-48 e pignone 14T", [
        "Il corpo del motore passa <b>attraverso il foro grande</b> della "
        "piastra, da sinistra; le due orecchie si appoggiano sulla faccia "
        "destra.",
        "Fissa con due M3&times;12 e rondelle nelle asole. <b>Non stringere "
        "ancora</b>: servono libere per il passo A10.",
        "Infila il pignone 14T sull'albero del motore. Il foro &egrave; "
        "volutamente stretto: allargalo con una lima a D finch&eacute; entra a "
        "pressione, senza gioco.",
        "Il pignone deve arrivare quasi a filo della faccia della staffa, "
        "cos&igrave; da impegnare tutta la lunghezza utile dell'albero motore.",
    ], fig="F08_motore.png", figw=98 * mm,
        figcap="FIG. 9 - motore e pignone montati sulla staffa")

    step("A10", "Registrare l'ingranamento 14/42", [
        "&Egrave; il motivo per cui i fori del motore sono asolati: "
        "l'interasse si regola a mano, non dipende dalle tolleranze di stampa.",
        "Spingi il motore nelle asole finch&eacute; il pignone ingrana con il "
        "42T del composto <b>senza gioco eccessivo e senza forzare</b>. Deve "
        "restare un filo di gioco percepibile.",
        "Stringi le due M3&times;12.",
        "Troppo stretto: il motore fatica e stalla. Troppo lasco: i denti "
        "saltano sotto carico.",
    ])

    step("A11", "Verifica a mano - non saltare questo passo", [
        "Ruota il braccio (o direttamente l'albero di uscita) a mano su tutta "
        "la corsa, lentamente.",
        "Tutto il treno deve girare <b>libero, senza punti duri e senza "
        "rumore di raschiamento</b>.",
        "Se senti un punto duro periodico, l'interasse di quella coppia "
        "&egrave; troppo stretto. Se senti gioco e scatti, &egrave; troppo largo.",
        "Controlla anche che la bandierina non tocchi la piastra sensori in "
        "nessuna posizione.",
        "<b>Solo quando il meccanismo gira bene a mano</b> ha senso collegare "
        "l'elettronica.",
    ])

    # =========================================================== PARTE B
    story.append(PageBreak())
    banner("Parte B - Elettronica",
           "alimentazione, sensori, firmware, prova a banco")

    figure("F10_cablaggio.png", CW, "FIG. 10 - schema di cablaggio completo")

    step("B1", "Regolare il buck LM2596 - prima di tutto il resto", [
        "Collega <b>solo</b> il buck all'alimentazione 12 V, attraverso il "
        "fusibile. Nient'altro a valle.",
        "Con il multimetro sull'uscita, gira il trimmer finch&eacute; leggi "
        "<b>5,00 V</b> (accettabile 4,95-5,10).",
        "Il trimmer &egrave; multigiro: servono parecchi giri, non forzare a "
        "fondo corsa.",
        "Solo a questo punto stacca l'alimentazione e collega il resto.",
    ])
    callout("Perch&eacute; &egrave; il passo 1.",
            "Un LM2596 nuovo pu&ograve; uscire a 12 V. Se lo colleghi al Nano "
            "e ai sensori prima di regolarlo, li bruci tutti in un colpo.")

    step("B2", "Bus 5 V e GND", [
        "Realizza due nodi di distribuzione (morsettiera o WAGO): uno per il "
        "<b>+5 V</b>, uno per il <b>GND</b>.",
        "Dal buck partono entrambi. Al bus 5 V si attaccano: ULN2003, sensori "
        "Hall. Al bus GND: ULN2003, sensori, <b>e il GND dell'Arduino</b>.",
        "Monta il condensatore da <b>1000 uF</b> fra i due bus, il pi&ugrave; "
        "vicino possibile alla ULN2003, rispettando la polarit&agrave;.",
        "Il Nano resta alimentato dalla USB di AstroArch. Il GND in comune "
        "&egrave; obbligatorio, altrimenti i segnali dei sensori non hanno "
        "riferimento.",
    ])

    step("B3", "Nano - ULN2003", [
        "D2 -> IN1, D3 -> IN2, D4 -> IN3, D5 -> IN4.",
        "Il 28BYJ-48 si innesta sulla ULN2003 con il suo connettore a 5 poli "
        "(4 fasi + comune): non c'&egrave; niente da cablare.",
        "Alimenta la ULN2003 dal bus 5 V, non dal Nano.",
    ])

    step("B4", "Sensori Hall", [
        "Guardando l'A3144 dal lato della <b>faccia marcata</b>, con i "
        "reofori in basso: pin 1 = VCC, pin 2 = GND, pin 3 = uscita.",
        "VCC e GND ai rispettivi bus, 100 nF fra i due il pi&ugrave; vicino "
        "possibile al corpo del sensore.",
        "Uscita del sensore <b>CLOSED</b> (quello nella sede a 0 gradi) -> "
        "<b>D10</b>. Uscita del sensore <b>OPEN</b> (sede a 90 gradi) -> "
        "<b>D11</b>.",
        "Il firmware usa INPUT_PULLUP: non servono resistenze esterne di "
        "pull-up. Il sensore deve <b>portare il pin a GND</b> quando il "
        "magnete gli passa davanti.",
    ])

    step("B5", "Scatola elettronica", [
        "In <i>stl/accessori/</i> c'&egrave; <i>GP1_electronics_box_MINI.stl</i>: "
        "scatola con coperchio e quattro colonnine, per Nano, ULN2003 e buck.",
        "Non &egrave; generata dal file SCAD e la sua mesh ha isole a facce "
        "coincidenti: si stampa senza problemi ma non &egrave; watertight. Se "
        "lo slicer protesta, usa la riparazione automatica.",
        "Fai uscire dalla scatola: il cavo dei sensori (4 fili), il cavo del "
        "motore, il cavo USB e l'ingresso 12 V.",
        "Monta fusibile e connettore DC sul lato 12 V, fuori dalla scatola o "
        "su una parete.",
    ])

    step("B6", "Caricare il firmware", [
        "Apri <i>firmware/GP1_Alnitak_DustCover_V4_2.ino</i> nell'IDE Arduino.",
        "Scheda: Arduino Nano. Processore: ATmega328P (oppure "
        "<i>ATmega328P (Old Bootloader)</i> se il caricamento fallisce).",
        "Non modificare nulla al primo caricamento. In particolare <b>non "
        "alzare MAX_MOVE_STEPS</b>: &egrave; un limite meccanico, vedi "
        "appendice D.",
        "Carica e apri il monitor seriale a <b>9600 baud</b>, terminatore "
        "<b>Nuova riga (LF)</b>.",
    ])

    step("B7", "Prova a banco, motore scollegato dalla meccanica", [
        "Prima di collegare il motore agli ingranaggi, verifica che "
        "l'elettronica risponda. Alimenta e manda i comandi della tabella qui "
        "sotto.",
        "Con il motore innestato sulla ULN2003 ma <b>non</b> accoppiato al "
        "treno, mandando <font face='Courier'>&gt;O000</font> l'albero del "
        "motore deve girare per circa 19 secondi e poi fermarsi in timeout "
        "(stato 3), perch&eacute; nessun sensore scatta.",
        "Avvicinando il magnete a mano al sensore OPEN durante il movimento, "
        "il motore si deve fermare subito e lo stato deve diventare 2.",
        "Se il motore vibra ma non gira, hai invertito due fili sul "
        "connettore: controlla l'ordine IN1-IN4.",
    ])
    table([
        ["Comando", "Risposta attesa", "Significato"],
        ["&gt;P000", "*P98000", "ping: risponde il product ID 98"],
        ["&gt;V000", "*V98120", "versione firmware 1.20"],
        ["&gt;S000", "*S98xyz", "stato (vedi tabella sotto)"],
        ["&gt;O000", "*O98000", "apri"],
        ["&gt;C000", "*C98000", "chiudi"],
    ], [26 * mm, 34 * mm, CW - 60 * mm])
    table([
        ["Cifra", "Posizione", "Valori"],
        ["x", "motore", "0 = fermo, 1 = in movimento"],
        ["y", "luce", "sempre 0 (il product 98 non ha pannello flat)"],
        ["z", "tappo", "0 = intermedio, 1 = chiuso, 2 = aperto, 3 = timeout/errore"],
    ], [16 * mm, 26 * mm, CW - 42 * mm])

    # =========================================================== PARTE C
    story.append(PageBreak())
    banner("Parte C - Integrazione",
           "taratura, chiusura, braccio, tappo, montaggio sul telescopio")

    step("C1", "Taratura dei sensori, a scatola aperta", [
        "Scatola aperta, coperchio non montato, meccanica completa "
        "(passi A1-A11) ed elettronica collegata.",
        "Ruota a mano l'albero fino alla posizione di <b>tappo chiuso</b> "
        "(braccio in avanti). Manda <font face='Courier'>&gt;S000</font>: "
        "l'ultima cifra deve essere <b>1</b>.",
        "Se resta 0, il sensore CLOSED non scatta: <b>prima prova a girare il "
        "magnete di 180 gradi</b> nella sua tasca. L'A3144 &egrave; unipolare "
        "e risponde a una sola faccia.",
        "Se ancora non scatta, allenta le due viti della piastra sensori e "
        "ruotala leggermente nelle asole, poi ristringi.",
        "Ripeti per la posizione aperta: ruota di 90 gradi e verifica che "
        "l'ultima cifra diventi <b>2</b>.",
        "Le asole ruotano <b>entrambi</b> i sensori insieme: regola sul CLOSED, "
        "che &egrave; quello che deve essere preciso. L'OPEN segue a 90 gradi "
        "esatti per costruzione.",
        "Quando sei soddisfatto, incolla definitivamente il magnete.",
    ])

    step("C2", "Verso di rotazione", [
        "Manda <font face='Courier'>&gt;O000</font> partendo da chiuso: il "
        "braccio deve muoversi <b>in apertura</b>, allontanandosi dal tubo.",
        "Se va nel verso sbagliato, nel firmware metti "
        "<font face='Courier'>MOTOR_REVERSED = true</font> e ricarica.",
        "Cronometra la corsa completa: deve durare <b>circa 19 secondi</b>. "
        "Molto di pi&ugrave; significa passi persi.",
    ])

    step("C3", "Chiusura del coperchio", [
        "Inserisci i 4 inserti M3 a caldo nei boss della scatola, se non "
        "l'hai gi&agrave; fatto.",
        "Controlla un'ultima volta che il treno giri libero e che i cavi non "
        "vadano a finire fra gli ingranaggi. Fermali con una fascetta.",
        "Chiudi con le 4 viti M3&times;10, serrando a croce.",
    ])

    step("C4", "Monobraccio", [
        "Infila il mozzo del braccio sull'estremit&agrave; sinistra "
        "dell'albero. Il mozzo &egrave; a morsetto: entra libero.",
        "Posizionalo lasciando <b>2 mm di luce fra il mozzo e il boss del "
        "cuscinetto</b>. &Egrave; la luce di progetto verificata.",
        "Orienta il braccio: a tappo chiuso la piastra deve essere parallela "
        "al piano del tappo, rivolta in avanti.",
        "Stringi la vite M3 del morsetto, con il dado nella sua sede "
        "esagonale. Serra deciso: &egrave; questo morsetto che trasmette tutta "
        "la coppia.",
    ], fig="F09_braccio.png", figw=104 * mm,
        figcap="FIG. 11 - monobraccio e contropiastra montati sull'albero")

    step("C5", "Preparare e fissare il tappo", [
        "Taglia il disco del diametro di <b>374 mm</b> nel materiale scelto "
        "al capitolo 0.5. Un compasso improvvisato con uno spago e una puntina "
        "&egrave; pi&ugrave; preciso di quanto sembri.",
        "Se usi polipropilene alveolare, orienta le nervature interne in "
        "direzione <b>radiale</b>, cio&egrave; lungo la linea che va "
        "dall'attacco del braccio al bordo opposto.",
        "Appoggia la piastra del braccio sul disco e <b>usala come dima</b> "
        "per i 4 fori Ø4,5.",
        "Inserisci i 4 dadi M4 nelle sedi esagonali sul lato inferiore delle "
        "piazzole del braccio.",
        "Serra le 4 viti M4&times;16 dal lato cielo, con la contropiastra e "
        "rondelle larghe. <b>Non strizzare</b>: il materiale del tappo si "
        "schiaccia e perdi il serraggio.",
    ])

    step("C6", "Misurare il tubo e fissare all'OTA", [
        "Il modello assume un diametro OTA di <b>362 mm</b>. Misura la "
        "<b>circonferenza reale</b> con un metro flessibile nel punto di "
        "fissaggio e dividi per pi greco.",
        "Tubo reale minore di 362: la sella balla. Riempi con EVA pi&ugrave; "
        "spessa (3-4 mm). Nessun problema.",
        "Tubo reale maggiore di 363,2: la sella non appoggia. Carteggia "
        "l'interno, oppure rigenera l'housing con il valore giusto e ristampa.",
        "<b>Scegli la posizione angolare prima di stringere.</b> La sella "
        "copre solo 43 gradi di arco e puoi ruotare tutto il gruppo attorno al "
        "tubo: la cinematica non cambia. Sul Quattro 300P focheggiatore e "
        "cercatore stanno vicino alla bocca del tubo, proprio dove va la "
        "sella: scegli il lato libero.",
        "Metti 3-4 mm di EVA fra sella e tubo e stringi le due cinghie.",
        "<b>Ribilancia la montatura</b>: hai aggiunto 400-500 g in punta a un "
        "tubo da 1200 mm.",
    ])

    step("C7", "Ekos / INDI", [
        "Driver: <b>Alnitak Remote Dust Cover</b> / <b>Flip Flat</b> "
        "(<font face='Courier'>indi_flipflat</font>).",
        "Porta seriale: quella del Nano, 9600 baud.",
        "Il product ID 98 &egrave; un <b>dust cover</b>: non c'&egrave; "
        "pannello flat. Per i flat servono cielo crepuscolare o un pannello "
        "separato.",
        "Park = chiuso. Unpark = aperto.",
        "<b>Imposta la posizione di park con il tubo lontano dallo zenit.</b> "
        "&Egrave; la singola cosa che d&agrave; pi&ugrave; margine a tutto il "
        "meccanismo: vedi appendice B.",
    ])

    step("C8", "Collaudo finale", [
        "Cicla apertura e chiusura almeno 10 volte di seguito da Ekos, "
        "controllando che lo stato finale sia sempre 1 o 2 e mai 3.",
        "Ripeti con il tubo in tre posizioni diverse: orizzontale, a 45 gradi "
        "e vicino allo zenit. &Egrave; allo zenit che il meccanismo fatica di "
        "pi&ugrave;.",
        "Controlla a tappo aperto che il disco non tocchi la scatola. La luce "
        "di progetto a fine corsa &egrave; 7,9 mm.",
        "Verifica che il tappo chiuso copra tutta l'apertura senza lasciare "
        "spiragli.",
        "Lascia il sistema fermo a tappo aperto per qualche minuto e controlla "
        "che non scenda da solo.",
    ])
    figure("F12_tappo_aperto.png", 105 * mm,
           "FIG. 12 - posizione di fine apertura, 90 gradi")

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
        ["&gt;V000", "*V98120", "versione firmware"],
        ["&gt;J000", "*J98000", "luminosit&agrave; (non usata)"],
    ], [26 * mm, 30 * mm, CW - 56 * mm])

    h2("B. &nbsp;Coppie e posizione di park")
    p("La coppia resistente alla cerniera dipende dall'<b>offset verticale del "
      "baricentro del tappo rispetto all'asse cerniera</b>, quindi dalla "
      "posizione in cui punta il telescopio. Con tappo da 105 g complessivi:")
    sp(3)
    table([
        ["Condizione", "Coppia resistente", "Margine"],
        ["Tubo allo zenit, tappo chiuso (inizio apertura)",
         "~0,23 N&middot;m", "<font color='#c0392b'><b>1,4&times;</b></font>"],
        ["Tubo a 45 gradi, tappo chiuso", "~0,16 N&middot;m", "2,0&times;"],
        ["Tubo orizzontale, tappo chiuso",
         "~0,04 N&middot;m", "<font color='#1e8449'><b>8&times;</b></font>"],
        ["Qualsiasi posizione, tappo a 90 gradi", "~0,04 N&middot;m", "8&times;"],
    ], [CW - 60 * mm, 30 * mm, 30 * mm], align={1: "CENTER", 2: "CENTER"})
    p("Coppia disponibile stimata: 28BYJ-48 a circa 12 giri/min in uscita "
      "(~30 mN&middot;m) moltiplicata per la riduzione stampata 15:1, con "
      "rendimento 0,72 su due stadi = <b>~0,32 N&middot;m</b>.", "small")
    sp(3)
    callout("Da -78 gradi in poi la gravit&agrave; aiuta l'apertura.",
            "Il tappo resta quindi appoggiato in posizione aperta senza "
            "caricare il finecorsa. Il momento critico &egrave; sempre "
            "l'<b>istante di distacco in apertura</b>, a tappo chiuso.",
            kind="info")

    h2("C. &nbsp;Diagnostica")
    table([
        ["Sintomo", "Causa probabile", "Cosa fare"],
        ["Il motore vibra ma non gira",
         "ordine delle fasi sbagliato",
         "controlla D2-D5 verso IN1-IN4"],
        ["Gira nel verso sbagliato", "-",
         "MOTOR_REVERSED = true nel firmware"],
        ["Lo stato resta sempre 0",
         "nessun Hall scatta",
         "gira il magnete di 180 gradi; poi registra le asole della piastra"],
        ["Stato 3 a fine corsa",
         "il sensore di destinazione non ha scattato",
         "traferro troppo grande o magnete debole; verifica i 2,9 mm"],
        ["Stato 3 dopo pochi secondi",
         "passi persi o stallo",
         "controlla che il treno giri libero a mano; alleggerisci il tappo; "
         "parcheggia lontano dallo zenit"],
        ["Il tappo si apre solo con il tubo basso",
         "margine di coppia insufficiente",
         "tappo pi&ugrave; leggero (cap. 0.5) e park lontano dallo zenit"],
        ["Rumore ciclico dagli ingranaggi",
         "interasse motore troppo stretto",
         "riapri e rifai il passo A10"],
        ["Il tappo chiuso non appoggia piano",
         "flessione del disco",
         "normale con Forex 1,5 mm; passa ad alveolare 3 mm"],
    ], [40 * mm, 42 * mm, CW - 82 * mm])

    h2("D. &nbsp;Limiti verificati - da non modificare senza ricontrollare")
    p("Tutte le luci qui sotto sono state misurate sulle mesh STL reali, non "
      "stimate. Lo script che le produce &egrave; "
      "<font face='Courier'>docs/verifica_collisioni.py</font>.")
    sp(4)
    table([
        ["Grandezza", "Valore", "Nota"],
        ["Luce disco tappo - scatola, a fine apertura", "7,9 mm",
         "a 90 gradi. A 105 gradi (la V4.1) era 0,65 mm"],
        ["Luce disco tappo - scatola, a tappo chiuso", "10,1 mm", ""],
        ["Luce monobraccio - scatola, su tutta la corsa", "2,0 mm",
         "fra la colonna del braccio e il boss del cuscinetto"],
        ["Luce monobraccio - anello frontale OTA", "3,3 mm",
         "con tappo da 1,5 mm. Cala di met&agrave; dello spessore in pi&ugrave;"],
        ["Luce piastra sensori - bandierina", "2,9 mm",
         "&egrave; anche il traferro magnetico"],
        ["Luce staffa - ingranaggio composto", "1,0 mm", "assiale"],
        ["Corsa nominale", "7.642 passi", "full-step, 90 gradi"],
        ["<b>MAX_MOVE_STEPS</b>", "<b>8.100</b>",
         "<b>limite meccanico, non una tolleranza</b>"],
    ], [66 * mm, 24 * mm, CW - 90 * mm])
    callout("Perch&eacute; MAX_MOVE_STEPS non va alzato.",
            "Se il sensore OPEN non scatta, il conteggio passi &egrave; "
            "l'unica cosa che impedisce al tappo di sbattere contro la "
            "scatola. A 8.100 passi il tappo si ferma a -95,4 gradi, dove "
            "restano circa 5 mm di luce. A 8.500 passi sarebbe a -100 gradi "
            "con 2 mm, a 8.900 passi a -105 gradi con 0,8 mm. Nell'altro "
            "verso non serve protezione: chiudendo oltre lo zero il tappo va "
            "in appoggio sull'anello frontale del tubo, che fa da fermo "
            "meccanico.")

    h2("E. &nbsp;Riverificare dopo una modifica")
    p("Se cambi un parametro nel file SCAD, rigenera gli STL interessati e "
      "rilancia la verifica:")
    sp(3)
    p("<font face='Courier' size='8.5'>openscad -o stl/mono_arm.stl "
      "-D 'part=\"mono_arm\"' gp1_flipcap_V4_2.scad<br/>"
      "python docs/verifica_collisioni.py</font>")
    sp(4)
    p("Controlla integrit&agrave; dei solidi, braccio contro housing, staffa "
      "contro housing e ingranaggi, disco del tappo contro housing, braccio "
      "contro tubo, piastra sensori contro housing e bandierina, ed "
      "extracorsa in avaria. Richiede numpy e scipy.")
    sp(10)
    p("<i>Documento generato automaticamente da "
      "docs/genera_manuale_pdf.py. Le figure vengono da "
      "docs/genera_figure_manuale.py, che le costruisce dal modello "
      "parametrico e dalle mesh esportate.</i>", "small")


def main():
    if not os.path.isdir(FIG):
        print("Mancano le figure: lancia prima docs/genera_figure_manuale.py")
        return 1
    build()
    doc = BaseDocTemplate(OUT, pagesize=A4,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN, bottomMargin=MARGIN,
                          title="GP1 FlipCap V4.2 - Manuale di montaggio",
                          author="GP1", subject="Manuale di montaggio")
    frame = Frame(MARGIN, MARGIN, CW, A4[1] - 2 * MARGIN, id="main",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="std", frames=[frame],
                                       onPage=page_deco)])
    doc.build(story)
    print("scritto %s (%.2f MB)" % (OUT, os.path.getsize(OUT) / 1e6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
