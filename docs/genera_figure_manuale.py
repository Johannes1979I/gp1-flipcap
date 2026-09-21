#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) 2026 Johannes1979I
"""
GP1 FlipCap V4.2 - genera le figure del manuale di montaggio.

Produce in docs/manuale/:
  - i render OpenSCAD dei passi di montaggio
  - i disegni quotati delle forature sull'housing
  - lo schema di cablaggio

Uso:  python docs/genera_figure_manuale.py
Richiede: matplotlib, OpenSCAD installato.
"""
import os
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "manuale")
SCAD = os.path.join(ROOT, "gp1_flipcap_V4_2.scad")
OPENSCAD = r"C:\Program Files\OpenSCAD\openscad.exe"

INK, ACC, WARN = "#1b2b3a", "#1f6fb2", "#c0392b"
RED, BLK, BLU, GRN = "#c0392b", "#2c3e50", "#1f6fb2", "#1e8449"


# ------------------------------------------------------------------ render 3D
OFF_ALL = ["show_ota", "show_lid", "show_cover", "show_housing", "show_bracket",
           "show_gears", "show_motor", "show_shaft", "show_arm",
           "show_backplate", "show_hall", "show_flag"]


def render(name, camera, on, angle=0, size=(1300, 950)):
    """`on` = elenco degli elementi da mostrare; tutto il resto e' spento."""
    cmd = [OPENSCAD, "-o", os.path.join(OUT, name),
           "--imgsize=%d,%d" % size, "--camera=" + camera,
           "-D", "lid_angle=%s" % angle]
    for k in OFF_ALL:
        cmd += ["-D", "%s=%s" % (k, "true" if k in on else "false")]
    cmd.append(SCAD)
    r = subprocess.run(cmd, capture_output=True)
    print("   %-28s %s" % (name, "ok" if r.returncode == 0 else "FALLITO"))


# ------------------------------------------------------- disegni di foratura
def _frame(ax, w, h, title, sub):
    ax.add_patch(FancyBboxPatch((0, 0), w, h, boxstyle="round,pad=0,rounding_size=6",
                                fc="#eef3f7", ec=INK, lw=2))
    ax.set_xlim(-34, w + 34)
    ax.set_ylim(-34, h + 46)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(w / 2, h + 34, title, ha="center", va="top", fontsize=13,
            color=INK, weight="bold")
    ax.text(w / 2, h + 26, sub, ha="center", va="top", fontsize=9,
            color="#5a6b7a", style="italic")


def _hole(ax, x, y, label, lab_dy=9):
    ax.add_patch(Circle((x, y), 1.7, fc="white", ec=WARN, lw=2))
    ax.plot([x - 7, x + 7], [y, y], color=WARN, lw=0.8)
    ax.plot([x, x], [y - 7, y + 7], color=WARN, lw=0.8)
    ax.text(x, y + lab_dy, label, ha="center",
            va="bottom" if lab_dy > 0 else "top",
            fontsize=10, color=WARN, weight="bold")


def _dimh(ax, x0, x1, y, text, ext_to=None):
    if ext_to is not None:
        for xx in (x0, x1):
            ax.plot([xx, xx], [ext_to, y], color=ACC, lw=0.7, ls=":")
    ax.annotate("", (x0, y), (x1, y),
                arrowprops=dict(arrowstyle="<->", color=ACC, lw=1.1))
    ax.text((x0 + x1) / 2, y + 1.6, text, ha="center", va="bottom",
            fontsize=10, color=ACC)


def _dimv(ax, y0, y1, x, text, ext_to=None):
    if ext_to is not None:
        for yy in (y0, y1):
            ax.plot([ext_to, x], [yy, yy], color=ACC, lw=0.7, ls=":")
    ax.annotate("", (x, y0), (x, y1),
                arrowprops=dict(arrowstyle="<->", color=ACC, lw=1.1))
    ax.text(x - 1.6, (y0 + y1) / 2, text, ha="right", va="center",
            fontsize=10, color=ACC, rotation=90)


def fig_fori_tetto():
    """Faccia superiore, 72 x 74 mm, vista da sopra (dal lato dove si trapana).
    Pagina: bordo anteriore (lato tappo) in basso, uscita albero a sinistra."""
    w, h = 72.0, 74.0
    fig, ax = plt.subplots(figsize=(7.4, 7.2))
    _frame(ax, w, h, "FIG. 2 - Fori M3 sul TETTO (staffa motore)",
           "vista da sopra, quote in mm dai bordi esterni")
    ys = 37.0                                  # Z=-25 -> 37 dal bordo anteriore
    _hole(ax, 16, ys, "A")
    _hole(ax, 48, ys, "B")
    _dimh(ax, 0, 16, h + 8, "16", ext_to=ys)
    _dimh(ax, 0, 48, h + 17, "48", ext_to=ys)
    _dimv(ax, 0, ys, -12, "37", ext_to=16)
    ax.text(w / 2, -9, "bordo ANTERIORE  (lato tappo)", ha="center", va="top",
            fontsize=10.5, color=INK, weight="bold")
    ax.text(-26, h / 2, "lato USCITA ALBERO", ha="center", va="center",
            fontsize=10.5, color=INK, weight="bold", rotation=90)
    ax.text(w / 2, ys - 12,
            "I due fori stanno sulla mezzeria\ndel lato da 74 mm",
            ha="center", va="top", fontsize=9, color="#5a6b7a")
    ax.text(w / 2, -20, "forare \u00d83,4 passante (parete 4 mm)",
            ha="center", va="top", fontsize=9.5, color=WARN)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "F02_fori_tetto.png"), dpi=190)
    plt.close(fig)
    print("   F02_fori_tetto.png            ok")


def fig_fori_parete():
    """Parete con il boss del cuscinetto, VISTA DA FUORI (dal lato del braccio).
    Guardando la parete da fuori con Y in alto, +Z (lato tappo) va a destra."""
    w, h = 74.0, 136.0
    fig, ax = plt.subplots(figsize=(6.6, 9.6))
    _frame(ax, w, h, "FIG. 3 - Fori M3 sulla PARETE del cuscinetto",
           "vista DA FUORI, dal lato del braccio - quote in mm dal centro del boss")

    def P(Y, Z):
        return (Z + 62.0, Y - 174.0)

    bx, by = P(212.0, -25.0)
    ax.add_patch(Circle((bx, by), 13, fc="#d8e4ee", ec=INK, lw=1.6))
    ax.add_patch(Circle((bx, by), 3.2, fc="#9fb3c4", ec=INK, lw=1.0))
    ax.plot([bx - 18, bx + 18], [by, by], color=INK, lw=0.7)
    ax.plot([bx, bx], [by - 18, by + 18], color=INK, lw=0.7)
    ax.text(bx - 16, by - 10, "boss cuscinetto\n626ZZ", ha="right", va="top",
            fontsize=9.5, color=INK)

    cx, cy = P(203.35, 1.63)
    dx, dy = P(238.63, -33.65)
    _hole(ax, cx, cy, "C", lab_dy=-16)
    _hole(ax, dx, dy, "D", lab_dy=-16)
    _dimh(ax, bx, cx, by - 30, "26,6", ext_to=cy)
    _dimv(ax, cy, by, cx + 16, "8,7", ext_to=cx)
    _dimh(ax, dx, bx, by + 38, "8,7", ext_to=dy)
    _dimv(ax, by, dy, dx - 14, "26,6", ext_to=dx)

    ax.text(w / 2, -9, "lato SELLA / TUBO", ha="center", va="top",
            fontsize=10.5, color=INK, weight="bold")
    ax.text(w + 9, h / 2, "lato TAPPO", ha="center", va="center",
            fontsize=10.5, color=INK, weight="bold", rotation=90)
    ax.text(-11, h / 2, "lato POSTERIORE\n(attacco sella)", ha="center",
            va="center", fontsize=9.5, color="#5a6b7a", rotation=90)
    ax.text(w / 2, h + 8,
            "C sta verso il TAPPO e in BASSO,  D verso il RETRO e in ALTO",
            ha="center", va="bottom", fontsize=9.5, color=WARN)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "F03_fori_parete.png"), dpi=190)
    plt.close(fig)
    print("   F03_fori_parete.png           ok")


# ---------------------------------------------------------- schema cablaggio
def fig_cablaggio():
    fig, ax = plt.subplots(figsize=(11.6, 7.6))
    ax.set_xlim(0, 116)
    ax.set_ylim(0, 78)
    ax.axis("off")

    def box(x, y, w, h, title, sub="", fc="#eef3f7", ec=INK):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle="round,pad=0,rounding_size=1.2",
                                    fc=fc, ec=ec, lw=1.8))
        ax.text(x + w / 2, y + h - 3.0, title, ha="center", va="top",
                fontsize=10.5, weight="bold", color=INK)
        if sub:
            ax.text(x + w / 2, y + h - 7.2, sub, ha="center", va="top",
                    fontsize=8.4, color="#4a5c6b")

    def seg(pts, color, lw=2.0):
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, lw=lw,
                solid_capstyle="round", solid_joinstyle="round", zorder=1)

    def node(x, y, color):
        ax.add_patch(Circle((x, y), 0.7, fc=color, ec=color, zorder=3))

    ax.text(58, 76, "GP1 FlipCap V4.2 - schema di cablaggio",
            ha="center", fontsize=14, weight="bold", color=INK)

    # catena di alimentazione
    box(3, 63, 18, 9, "12 V DC", "ingresso astronomico", fc="#fdecea", ec=RED)
    box(26, 63, 15, 9, "FUSIBILE", "1 - 1,5 A", fc="#fdecea", ec=RED)
    box(46, 61, 28, 11, "LM2596",
        "buck 12 V -> 5,0 V\nREGOLARE A VUOTO, PRIMA", fc="#fdecea", ec=RED)
    seg([(21, 67.5), (26, 67.5)], RED)
    seg([(41, 67.5), (46, 67.5)], RED)

    # bus 5 V e GND
    y5, yg = 55.0, 50.0
    seg([(3, y5), (104, y5)], RED, 2.6)
    seg([(3, yg), (104, yg)], BLK, 2.6)
    ax.text(105.5, y5, "+5 V", ha="left", va="center", fontsize=10,
            weight="bold", color=RED)
    ax.text(105.5, yg, "GND", ha="left", va="center", fontsize=10,
            weight="bold", color=BLK)
    seg([(66, 61), (66, y5)], RED)
    node(66, y5, RED)
    seg([(53, 61), (53, 57.5), (14, 57.5), (14, yg)], BLK)
    node(14, yg, BLK)

    # condensatore di bulk fra i due bus
    seg([(24, y5), (24, 53.4)], RED)
    node(24, y5, RED)
    seg([(21.6, 53.4), (26.4, 53.4)], RED, 2.6)
    seg([(21.6, 52.0), (26.4, 52.0)], BLK, 2.6)
    seg([(24, 52.0), (24, yg)], BLK)
    node(24, yg, BLK)
    ax.text(28, 52.7, "1000 uF 10-16 V  (sul bus, vicino alla ULN2003)",
            va="center", fontsize=8.6, color="#4a5c6b")

    # blocchi logici
    box(8, 26, 30, 16, "Arduino Nano", "ATmega328P 5 V\nUSB -> AstroArch")
    box(50, 26, 26, 16, "ULN2003", "scheda driver")
    box(86, 26, 24, 16, "28BYJ-48", "5 V", fc="#eaf3ea", ec=GRN)
    box(8, 4, 42, 14, "2x Hall A3144",
        "CLOSED = sede a 0 gradi\nOPEN = sede a 90 gradi\n"
        "100 nF fra VCC e GND su ogni sensore", fc="#eaf3ea", ec=GRN)

    # alimentazioni dai bus
    seg([(60, y5), (60, 42)], RED)
    node(60, y5, RED)
    ax.text(61, 47, "5 V", fontsize=8.6, color=RED)
    seg([(70, yg), (70, 42)], BLK)
    node(70, yg, BLK)
    ax.text(71, 45, "GND", fontsize=8.6, color=BLK)
    seg([(30, yg), (30, 42)], BLK)
    node(30, yg, BLK)
    ax.text(31, 45, "GND", fontsize=8.6, color=BLK)
    # alimentazione sensori: instradata a sinistra, fuori dai fili di segnale
    seg([(4.5, y5), (4.5, 20.5), (11, 20.5), (11, 18)], RED)
    node(4.5, y5, RED)
    ax.text(3.6, 34, "5 V ai\nsensori", fontsize=8.6, color=RED,
            ha="right", va="center")
    seg([(7, yg), (7, 22.5), (16, 22.5), (16, 18)], BLK)
    node(7, yg, BLK)
    ax.text(7.8, 24.6, "GND", fontsize=8.6, color=BLK)

    # segnali Nano -> ULN2003
    for i, (d, inn) in enumerate([("D2", "IN1"), ("D3", "IN2"),
                                  ("D4", "IN3"), ("D5", "IN4")]):
        y = 39.5 - i * 3.2
        seg([(38, y), (50, y)], BLU, 1.7)
        ax.text(44, y + 0.5, "%s \u2192 %s" % (d, inn), ha="center",
                fontsize=8.4, color=BLU)

    # ULN2003 -> motore
    seg([(76, 34), (86, 34)], GRN, 2.2)
    ax.text(81, 35.2, "connettore\n5 poli", ha="center", va="bottom",
            fontsize=8.4, color=GRN)
    ax.text(81, 32.6, "4 fasi + comune", ha="center", va="top",
            fontsize=7.8, color="#4a5c6b")

    # segnali Hall -> Nano
    seg([(28, 26), (28, 18)], BLU, 1.7)
    ax.text(28.9, 23.4, "D10 \u2190 CLOSED", fontsize=8.6, color=BLU)
    seg([(36, 26), (36, 20.8), (44, 20.8), (44, 18)], BLU, 1.7)
    ax.text(36.9, 19.4, "D11 \u2190 OPEN", fontsize=8.6, color=BLU)

    ax.text(83, 11,
            "Il firmware usa INPUT_PULLUP: il sensore\n"
            "deve portare il pin a GND quando il\n"
            "magnete gli passa davanti.",
            ha="center", va="center", fontsize=9, color="#4a5c6b")

    ax.text(58, 0.6,
            "Il 28BYJ-48 NON va alimentato dal 5 V del Nano. GND del buck, "
            "della ULN2003, dei sensori e dell'Arduino devono essere in comune.",
            ha="center", fontsize=9.2, color=RED, style="italic")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "F10_cablaggio.png"), dpi=190)
    plt.close(fig)
    print("   F10_cablaggio.png             ok")


# ----------------------------------------------------------------------- main
def main():
    os.makedirs(OUT, exist_ok=True)
    B = "show_housing"
    print("Figure 3D (OpenSCAD):")
    render("F01_assieme.png", "650,480,900,40,110,-10", OFF_ALL, angle=0)
    render("F04_piastra_hall.png", "300,180,180,100,215,-18", [B, "show_hall"])
    render("F05_albero.png", "430,230,150,118,248,-22",
           [B, "show_hall", "show_shaft", "show_flag"])
    render("F06_ruote.png", "430,230,150,118,248,-22",
           [B, "show_hall", "show_shaft", "show_flag", "show_gears"])
    render("F07_staffa.png", "430,230,150,118,248,-22",
           [B, "show_hall", "show_shaft", "show_flag", "show_gears", "show_bracket"])
    render("F08_motore.png", "430,230,150,118,248,-22",
           [B, "show_hall", "show_shaft", "show_flag", "show_gears",
            "show_bracket", "show_motor"])
    render("F09_braccio.png", "-260,150,430,90,200,-8",
           [B, "show_shaft", "show_arm", "show_backplate"])
    render("F11_tappo_chiuso.png", "650,480,900,40,110,-10", OFF_ALL, angle=0)
    render("F12_tappo_aperto.png", "1150,950,1350,0,190,140", OFF_ALL, angle=-90)
    render("F13_staffa_pezzo.png", "200,330,140,137,268,-22", [B, "show_bracket"])
    print("Disegni quotati e schemi:")
    fig_fori_tetto()
    fig_fori_parete()
    fig_cablaggio()
    print("Fatto:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
