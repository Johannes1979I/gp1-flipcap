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


# =========================================================== ASSEMBLAGGIO
class UI:
    """Raccoglie gli elementi di impaginazione per docs/contenuto_manuale.py."""
    banner = staticmethod(banner)
    step = staticmethod(step)
    table = staticmethod(table)
    callout = staticmethod(callout)
    figure = staticmethod(figure)
    figure_pair = staticmethod(figure_pair)
    h2 = staticmethod(h2)
    p = staticmethod(p)
    sp = staticmethod(sp)
    mm = mm
    CW = CW
    PageBreak = PageBreak
    story = story
    Paragraph = Paragraph
    Spacer = Spacer
    S = S


def main():
    if not os.path.isdir(FIG):
        print("Mancano le figure: lancia prima docs/genera_figure_manuale.py")
        return 1
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import contenuto_manuale
    contenuto_manuale.build(UI)
    doc = BaseDocTemplate(OUT, pagesize=A4,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN, bottomMargin=MARGIN,
                          title="GP1 FlipCap V4.2 - Manuale di montaggio",
                          author="GP1 FlipCap", subject="Manuale di montaggio")
    frame = Frame(MARGIN, MARGIN, CW, A4[1] - 2 * MARGIN, id="main",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="std", frames=[frame],
                                       onPage=page_deco)])
    doc.build(story)
    print("scritto %s (%.2f MB)" % (OUT, os.path.getsize(OUT) / 1e6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
