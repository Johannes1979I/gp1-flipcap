#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) 2026 Johannes1979I
"""
GP1 FlipCap V6 - genera le figure del manuale.

Produce in docs/manuale/:
  - i render OpenSCAD dei passi di montaggio, con le etichette gia' messe
  - gli schemi disegnati (corsa, albero, motore, vano, cablaggio, cinghie)

Uso:  python docs/genera_figure_manuale.py
Serve: matplotlib, pillow, numpy e OpenSCAD (variabile OPENSCAD se non e' nel PATH).

Le etichette sui render sono posizionate proiettando i punti 3D con la
stessa camera ortografica usata da OpenSCAD (campo visivo 22,5 gradi), per
cui restano giuste anche se si cambiano i parametri del modello.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, Polygon
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "manuale")
SCAD = os.path.join(ROOT, "gp1_flipcap_V6.scad")
WORK = os.path.join(tempfile.gettempdir(), "gp1_v6_figure")

INK, ACC, WARN = "#1b2b3a", "#1f6fb2", "#c0392b"
RED, BLK, BLU, GRN, ORA, VIO = "#c0392b", "#2c3e50", "#1f6fb2", "#1e8449", "#e08214", "#7d3c98"
GREY = "#5a6b7a"


def openscad_exe():
    for c in (os.environ.get("OPENSCAD"), shutil.which("openscad"),
              r"C:\Program Files\OpenSCAD\openscad.exe",
              "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD", "/usr/bin/openscad"):
        if c and os.path.exists(c):
            return c
    sys.exit("OpenSCAD non trovato: imposta la variabile d'ambiente OPENSCAD")


OPENSCAD = openscad_exe()


# ------------------------------------------------------------ parametri
def read_params():
    names = ["hinge_y", "hinge_z", "arm_x", "arm_dz", "cap_d", "ota_d", "open_angle",
             "box_x0", "box_x1", "box_y0", "box_y1", "box_z0", "box_z1",
             "bay_y0", "bay_y1", "bay_z0", "bay_z1", "rest_z", "front_saddle_z",
             "rear_saddle_z", "saddle_x1", "compound_yz", "motor_yz", "can_yz",
             "byj_ears", "byj_w", "flag_x", "left_seat_x0", "left_seat_x1",
             "cover_seat_x0", "cover_seat_x1", "spacer_list", "nano_pos", "nano_size",
             "nano_holes", "buck_pos", "buck_size", "buck_holes", "uln_pos", "uln_size",
             "uln_holes", "usb_hole", "jack_yz", "cable_slot", "compound_x", "hall_standoff",
             "hall_screw_a", "hall_screw_r", "magnet_r", "cav_x0", "mb_screws",
             "bay_bosses", "rest_pad", "cap_thickness", "cover_t"]
    with open(os.path.join(WORK, "probe.scad"), "w") as f:
        f.write("include <modello.scad>\n")
        for n in names:
            f.write('echo(str("P %s=", %s));\n' % (n, n))
    echo = os.path.join(WORK, "probe.echo")
    subprocess.run([OPENSCAD, "-o", echo, "-D", 'part="none"', "probe.scad"],
                   cwd=WORK, capture_output=True)
    txt = open(echo, errors="ignore").read()
    P = {}
    for n, v in re.findall(r'ECHO: "P (\w+)=(.*)"\s*$', txt, re.M):
        v = v.replace('\\"', '"')
        try:
            P[n] = eval(v.replace("true", "True").replace("false", "False"))
        except Exception:
            P[n] = v
    missing = [n for n in names if n not in P]
    if missing:
        sys.exit("parametri non letti: %s" % missing)
    return P


# ------------------------------------------------------------ render 3D
FOV_TAN = np.tan(np.radians(22.5 / 2))


def to_view(p):
    """Il wrapper ruota il modello di +90 gradi attorno a X: Y del modello in alto."""
    x, y, z = p
    return np.array([x, -z, y], float)


class Cam:
    def __init__(self, eye, center, size):
        self.eye, self.center = np.array(eye, float), np.array(center, float)
        self.W, self.H = size
        d = self.center - self.eye
        self.dist = np.linalg.norm(d)
        d /= self.dist
        r = np.cross(d, [0, 0, 1])
        self.right = r / np.linalg.norm(r)
        self.up = np.cross(self.right, d)
        self.scale = (self.H / 2) / (self.dist * FOV_TAN)

    def arg(self):
        return "--camera=%s" % ",".join("%.3f" % v for v in (*self.eye, *self.center))

    def px(self, p_model):
        q = to_view(p_model) - self.center
        return (self.W / 2 + q.dot(self.right) * self.scale,
                self.H / 2 - q.dot(self.up) * self.scale)


def scad_scene(items):
    """items: righe OpenSCAD gia' pronte da mettere dentro la rotazione."""
    return ("include <modello.scad>\n$fn=72;\n" + BRG_MODULE + "\nrotate([90,0,0]){\n" +
            "\n".join("    " + s for s in items) + "\n}\n")


def render(name, items, cam, labels=(), title=None, crop=True):
    scad = os.path.join(WORK, name.replace(".png", ".scad"))
    with open(scad, "w") as f:
        f.write(scad_scene(items))
    raw = os.path.join(WORK, name)
    r = subprocess.run([OPENSCAD, "-o", raw, "--imgsize=%d,%d" % (cam.W, cam.H),
                        cam.arg(), "--projection=o", "--colorscheme=Tomorrow",
                        "-D", 'part="none"', os.path.basename(scad)],
                       cwd=WORK, capture_output=True)
    if r.returncode != 0 or not os.path.exists(raw):
        print("   %-28s FALLITO" % name)
        return
    img = np.asarray(Image.open(raw).convert("RGB"))
    annotate(img, cam, labels, os.path.join(OUT, name), title, crop)
    print("   %-28s ok" % name)


def _label_boxes(cam, labels):
    """Per ogni etichetta: punto indicato, centro del testo, mezze misure del riquadro."""
    out = []
    for text, p3, off, *rest in labels:
        ax_, ay_ = cam.px(p3)
        lines = text.split("\n")
        hw = 5.2 * max(len(l) for l in lines) + 12
        hh = 11 * len(lines) + 8
        out.append((text, (ax_, ay_), (ax_ + off[0], ay_ + off[1]), hw, hh, rest[0] if rest else INK))
    return out


def annotate(img, cam, labels, out, title, crop):
    H, W = img.shape[:2]
    boxes = _label_boxes(cam, labels)
    bg = img[2, 2].astype(int)
    mask = np.abs(img.astype(int) - bg).sum(2) > 12
    ys, xs = np.nonzero(mask)
    x0, x1, y0, y1 = 0, W, 0, H
    if crop and len(xs):
        pad = 30
        lx = [xs.min(), xs.max()] + [b[2][0] - b[3] for b in boxes] + [b[2][0] + b[3] for b in boxes]
        ly = [ys.min(), ys.max()] + [b[2][1] - b[4] for b in boxes] + [b[2][1] + b[4] for b in boxes]
        x0, x1 = int(min(lx)) - pad, int(max(lx)) + pad
        y0, y1 = int(min(ly)) - pad, int(max(ly)) + pad
    fig = plt.figure(figsize=((x1 - x0) / 100, (y1 - y0) / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(tuple(bg / 255.0))
    ax.imshow(img, extent=(0, W, H, 0))
    ax.set_xlim(x0, x1)
    ax.set_ylim(y1, y0)
    ax.axis("off")
    for text, anchor, pos, hw, hh, col in boxes:
        ax.annotate(text, anchor, pos, fontsize=15, color=col, weight="bold",
                    ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=col, lw=1.2, alpha=0.93),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6, shrinkA=2, shrinkB=1))
    if title:
        ax.text((x0 + x1) / 2, y0 + 18, title, ha="center", va="top", fontsize=17,
                color=INK, weight="bold")
    fig.savefig(out, dpi=100, facecolor=tuple(bg / 255.0))
    plt.close(fig)


BRG_MODULE = ('module brg(x0,yz,od,id,w){ at_yz(yz,x0) difference(){ x_cyl(od/2,w,false);'
              ' translate([-1,0,0]) x_cyl(id/2,w+2,false); } }\n'
              # viteria per l'esploso: vite con la testa verso -X e il gambo verso +X
              'module vite_x(d,l,dk,k){ x_cyl(d/2,l,false); translate([-k,0,0]) x_cyl(dk/2,k,false); }\n'
              'module rondella_x(D,d,t){ difference(){ x_cyl(D/2,t,false); translate([-1,0,0]) x_cyl(d/2,t+2,false); } }\n'
              'module dado_x(s,m,d){ difference(){ rotate([0,90,0]) cylinder(d=s/cos(30),h=m,$fn=6);'
              ' translate([-1,0,0]) x_cyl(d/2,m+2,false); } }\n'
              'module asse_x(yz,x0,x1){ for(x=[x0:7:x1-3]) at_yz(yz,x) x_cyl(0.45,4,false); }')
BEARINGS_GEOM = ('union(){ brg(left_seat_x0,hinge_yz,19,6,6); brg(cover_seat_x0,hinge_yz,19,6,6);'
                 ' brg(compound_x+8.9,compound_yz,16,5,5); }')
BEARINGS = ['color([0.80,0.82,0.86]) ' + BEARINGS_GEOM + ';']


# pezzi con il loro colore
C = dict(housing="[0.13,0.36,0.60]", cover="[0.20,0.45,0.70,0.35]", bay_lid="[0.45,0.30,0.70,0.45]",
         bay_tray="[0.86,0.86,0.89]", motor_bracket="[0.20,0.62,0.32]", hall_plate="[0.92,0.92,0.96]",
         spacers="[0.98,0.98,0.98]", gears="[0.95,0.52,0.08]", magnet_flag="[0.97,0.78,0.10]",
         mono_arm="[0.80,0.12,0.10]", cap_backplate="[0.55,0.10,0.08]", cap_rest="[0.90,0.60,0.15]",
         motor="[0.42,0.42,0.47]", shaft="[0.75,0.75,0.80]", boards="[0.10,0.50,0.28]",
         cap="[0.16,0.45,0.20,0.55]", ota="[0.30,0.30,0.34,0.35]", strap="[0.15,0.15,0.18]")


def P(part, col=None, angle=0):
    return 'color(%s) render() part_placed("%s",%s);' % (col or C.get(part, "[0.6,0.6,0.6]"), part, angle)


BOLT = ['color([0.55,0.56,0.60]){ at_yz(compound_yz,box_x0-3.5) x_cyl(2.5,box_x1+cover_t+6-box_x0+3.5,false);'
        ' at_yz(compound_yz,box_x0-3.5) x_cyl(4.6,3.5,false,$fn=6); }']


def CLIP(geom, col, zmax):
    """Solo la parte con Z <= zmax, calcolata prima del disegno: vista in sezione."""
    return ("color(%s) render() intersection(){ %s translate([-500,-500,-1500]) cube([1000,1000,1500+(%s)]); }"
            % (col, geom, zmax))


def BOX(geom, col, x0, x1, y0, y1, z0, z1):
    """Solo la parte dentro il parallelepipedo dato, calcolata prima del disegno."""
    return ("color(%s) render() intersection(){ %s translate([%s,%s,%s]) cube([%s,%s,%s]); }"
            % (col, geom, x0, y0, z0, x1 - x0, y1 - y0, z1 - z0))


GEARS = ['color(%s){ render() part_placed("output_gear"); render() part_placed("compound_gear");'
         ' render() part_placed("motor_pinion"); }' % C["gears"]]
MOTOR = ['color(%s) motor_dummy();' % C["motor"]]
SHAFT = ['color(%s) shaft_dummy();' % C["shaft"]]
BOARDS = ['color(%s) boards_dummy();' % C["boards"]]


def OTA(length=650):
    return ['color(%s) translate([0,0,-%d]) cylinder(d=ota_d,h=%d,$fn=160);' % (C["ota"], length, length),
            'color([0.10,0.10,0.12,0.5]) translate([0,0,-5]) difference(){ cylinder(d=ota_d+8,h=8,$fn=160);'
            ' translate([0,0,-1]) cylinder(d=ota_d-8,h=10,$fn=160); }']


def CAP(a):
    return ['color(%s) cap_dummy(%s);' % (C["cap"], a)]


def STRAPS():
    """Cinghie da 25 mm: anello sul tubo piu' il tratto sopra la sella."""
    s = []
    for zs in ("front_saddle_z", "rear_saddle_z"):
        z0 = "(%s[0]+3)" % zs if zs == "front_saddle_z" else "(%s[0]+4)" % zs
        s.append("color(%s) translate([0,0,%s]) difference(){ cylinder(r=ota_d/2+1.6,h=25,$fn=180);"
                 " translate([0,0,-1]) cylinder(r=ota_d/2,h=27,$fn=180);"
                 " translate([saddle_x0,0,-1]) cube([saddle_x1-saddle_x0,300,27]); }" % (C["strap"], z0))
        s.append("color(%s) translate([0,0,%s]) intersection(){ difference(){ cylinder(r=ota_r+saddle_thickness+1.6,h=25,$fn=180);"
                 " translate([0,0,-1]) cylinder(r=ota_r+saddle_thickness,h=27,$fn=180); }"
                 " translate([saddle_x0,0,-1]) cube([saddle_x1-saddle_x0,300,27]); }" % (C["strap"], z0))
    return s


# ------------------------------------------------------------ figure 3D
def figure_renders(Pm):
    hy, hz = Pm["hinge_y"], Pm["hinge_z"]
    K, M, Cn = Pm["compound_yz"], Pm["motor_yz"], Pm["can_yz"]
    y0, y1 = Pm["box_y0"], Pm["box_y1"]
    bz0, bz1 = Pm["bay_z0"], Pm["bay_z1"]
    by0, by1 = Pm["bay_y0"], Pm["bay_y1"]
    w = np.array(Pm["byj_w"])
    rz = Pm["rest_z"]
    full = (['color(%s) render() part_placed("housing");' % C["housing"],
             P("cover"), P("bay_lid"), P("mono_arm"), P("cap_backplate"),
             "color(%s) for(z=rest_z) translate([0,0,z]) render() cap_rest();" % C["cap_rest"]])
    housing_gear = BOX('part_placed("housing");', C["housing"], 80, 160, y0 - 5, y1 + 5, -70, 20)
    jobs = []

    # F01 - assieme chiuso, dal davanti a destra
    cam = Cam(to_view((1150, 650, 420)), to_view((20, 120, -230)), (1700, 1300))
    jobs.append(("F01_assieme_chiuso.png", OTA() + CAP(0) + full + STRAPS(), cam, [
        ("riduttore", (156, 285, -10), (260, -150)),
        ("vano elettronica", (156, 205, -130), (300, -60)),
        ("braccio", (68, 250, 0), (-150, -170), RED),
        ("tappo chiuso", (-60, 40, 18), (80, -260), GRN),
        ("cinghie", (150, 110, -175), (330, 120)),
        ("appoggi del tappo", (0, 216, rz[0]), (40, -170), ORA),
    ], None))

    # F02 - parcheggiato, dal lato del braccio (braccio e contropiastra ruotati)
    oa = Pm["open_angle"]
    parked = (['color(%s) render() part_placed("housing");' % C["housing"], P("cover"), P("bay_lid"),
               P("mono_arm", angle=oa), P("cap_backplate", angle=oa),
               "color(%s) for(z=rest_z) translate([0,0,z]) render() cap_rest();" % C["cap_rest"]])
    cam = Cam(to_view((-900, 1050, 650)), to_view((40, 190, -240)), (1700, 1300))
    jobs.append(("F02_assieme_parcheggiato.png", OTA() + CAP(oa) + parked + STRAPS(), cam, [
        ("tappo parcheggiato", (-80, 223, -300), (-60, -200), GRN),
        ("braccio", (68, 232, -120), (-260, -150), RED),
        ("appoggi (sotto il tappo)", (0, 216, rz[1]), (-150, 150), ORA),
        ("scatola", (156, 285, -10), (180, -130)),
    ], None))

    # F05 - housing da solo, dal lato aperto
    cam = Cam(to_view((620, 420, 360)), to_view((115, 180, -90)), (1500, 1300))
    jobs.append(("F05_housing.png", [P("housing")], cam, [
        ("riduttore", (120, y1 - 15, 0), (330, -120)),
        ("vano elettronica\n(si apre da questo lato)", (140, 200, -110), (260, 40)),
        ("passaggio cavi", (111, 196, -58), (-230, -120)),
        ("sella anteriore", (118, 150, -45), (-330, 150)),
        ("sella posteriore", (120, 150, -178), (260, 170)),
        ("bossoli per gli inserti M3", (156, y0 + 6, 4), (-120, 230)),
    ], None))

    # F07 - piastra sensori, vista dal lato aperto, da vicino
    cam = Cam(to_view((360, hy, hz)), to_view((120, hy, hz)), (1100, 1000))
    xs = Pm["cav_x0"] + Pm["hall_standoff"] + 3
    a0, a1 = [np.radians(a) for a in Pm["hall_screw_a"]]
    r = Pm["hall_screw_r"]
    near = BOX('part_placed("housing");', C["housing"], 80, 160, hy - 42, hy + 42, hz - 42, hz + 42)
    sensors = ('color([0.08,0.08,0.10]) translate([cav_x0,hinge_y,hinge_z]) rotate([90,0,90])'
               ' for(a=[0,-open_angle]) translate([magnet_r*sin(a),magnet_r*cos(a),hall_seat_h-1.2])'
               ' rotate([0,0,-a]) cube([4.5,3.5,2.3],center=true);')
    jobs.append(("F07_piastra_sensori.png", [near, P("hall_plate"), sensors], cam, [
        ("sede CLOSED\n(verso la bocca del tubo)", (xs, hy, hz + Pm["magnet_r"]), (-260, -210), GRN),
        ("sede OPEN\n(verso il fondo)", (xs, hy - Pm["magnet_r"], hz), (-250, 230), RED),
        ("asola", (xs, hy + r * np.sin(a0), hz + r * np.cos(a0)), (-230, -40)),
        ("asola", (xs, hy + r * np.sin(a1), hz + r * np.cos(a1)), (220, -110)),
    ], None))

    # F08 - albero di uscita in sezione, visto dal davanti, da vicino
    cut = hz
    yl0, yl1 = hy - 38, hy + 45

    def SEC(geom, col):
        return ("color(%s) render() intersection(){ %s translate([-500,%s,-1500]) cube([1000,%s,1500+(%s)]); }"
                % (col, geom, yl0, yl1 - yl0, cut))

    sec = [SEC('part_placed("housing");', C["housing"]),
           SEC('part_placed("cover");', "[0.20,0.45,0.70]"),
           SEC('part_placed("hall_plate");', C["hall_plate"]),
           SEC('part_placed("spacers");', C["spacers"]),
           SEC('part_placed("magnet_flag",0);', C["magnet_flag"]),
           SEC('part_placed("output_gear");', C["gears"]),
           SEC('shaft_dummy();', C["shaft"]),
           SEC(BEARINGS_GEOM + ';', "[0.80,0.82,0.86]")]
    cam = Cam(to_view((112, hy + 4, cut + 300)), to_view((112, hy + 4, cut)), (1700, 1100))
    sp = {q[0]: q for q in Pm["spacer_list"]}
    jobs.append(("F08_albero.png", sec, cam, [
        ("626ZZ", (89.6, hy + 7.5, cut), (-60, -250)),
        ("s1", ((sp["s1"][1] + sp["s1"][2]) / 2, hy + 3.6, cut), (-10, -330), BLU),
        ("bandierina", (Pm["flag_x"], hy + 9, cut), (40, -280)),
        ("s3", ((sp["s3"][1] + sp["s3"][2]) / 2, hy + 3.6, cut), (0, -250), BLU),
        ("ingranaggio 70T", (128, hy + 22, cut), (-20, -170)),
        ("s2", ((sp["s2"][1] + sp["s2"][2]) / 2, hy + 3.6, cut), (0, -280), BLU),
        ("626ZZ", (151, hy + 7.5, cut), (40, -250)),
        ("albero 6 x 100", (72, hy, cut), (-20, 150)),
        ("sensori", (94.5, hy - 14, cut), (-40, 250)),
        ("parete sinistra", (86, hy - 30, cut), (-190, 120)),
        ("coperchio", (157.6, hy - 25, cut), (150, 130)),
    ], None))

    # F09 - staffa e motore
    cam = Cam(to_view((560, 330, 180)), to_view((136, 205, -28)), (1300, 1150))
    e0, e1 = Pm["byj_ears"]
    cap_pt = np.array(Cn) + 14.5 * w
    jobs.append(("F09_staffa_motore.png", [P("housing"), P("motor_bracket")] + MOTOR, cam, [
        ("staffa motore", (138.3, Cn[0] + 19, Cn[1] + 8), (230, -170), GRN),
        ("28BYJ-48", (139.3, Cn[0] - 5, Cn[1] + 9), (-300, -140)),
        ("vite M3 x 8", (139.3, e0[0], e0[1]), (-280, 120)),
        ("vite M3 x 8", (139.3, e1[0], e1[1]), (260, -60)),
        ("cappuccio dei fili\n(nell'intaglio)", (136, cap_pt[0], cap_pt[1]), (260, 200)),
    ], None))

    # F10 - riduttore completo, vista dal lato aperto
    cam = Cam(to_view((700, (y0 + y1) / 2, -25)), to_view((120, (y0 + y1) / 2, -25)), (1250, 1450))
    jobs.append(("F10_riduttore.png", [housing_gear, P("motor_bracket"), P("spacers"), P("hall_plate"),
                                       P("magnet_flag")] + GEARS + MOTOR + SHAFT + BOLT, cam, [
        ("ingranaggio di uscita 70T", (140, hy + 20, hz + 15), (230, -250)),
        ("composto 42T / 14T", (147, K[0] - 10, K[1] - 8), (330, 20)),
        ("pignone 14T", (148, M[0] - 2, M[1] + 4), (-330, 10)),
        ("motore 28BYJ-48", (140, Cn[0] - 9, Cn[1] - 6), (330, 120)),
        ("staffa", (139, y0 + 8, -20), (-280, 160), GRN),
    ], None))

    # F11 - vano elettronica con il vassoio, parete superiore tolta per vedere dentro
    zc, yc = (bz0 + bz1) / 2, (by0 + by1) / 2
    cam = Cam(to_view((470, 520, zc + 120)), to_view((120, 180, zc)), (1500, 1100))
    jobs.append(("F11_vano.png", [BOX('part_placed("housing");', C["housing"],
                                      80, 160, by0 - 10, by1 - 5, bz0 - 2, bz1 + 2),
                                  P("bay_tray")] + BOARDS, cam, [
        ("Arduino Nano\n(colonnine da 10 mm)", (Pm["nano_pos"][0], 182.6, Pm["nano_pos"][1]), (260, -80)),
        ("LM2596", (Pm["buck_pos"][0], 176.6, Pm["buck_pos"][1]), (230, 90)),
        ("ULN2003", (Pm["uln_pos"][0], 176.6, Pm["uln_pos"][1]), (-230, 120)),
        ("listello", (89, 173, -150), (-200, -90)),
    ], None))

    # F13 - selle e cinghie
    cam = Cam(to_view((900, 160, -40)), to_view((110, 150, -110)), (1500, 1250))
    jobs.append(("F13_cinghie.png", OTA(420) + [P("housing")] + STRAPS(), cam, [
        ("cinghia anteriore", (150, 115, -46), (-330, 250)),
        ("cinghia posteriore", (150, 115, -178), (300, 250)),
        ("sella anteriore", (120, 158, -32), (-300, -130)),
        ("sella posteriore", (118, 152, -192), (300, -140)),
    ], None))

    # F14 - braccio e contropiastra
    cam = Cam(to_view((-420, 520, 520)), to_view((60, 190, 0)), (1400, 1150))
    jobs.append(("F14_braccio.png", [P("housing"), P("cover"), P("mono_arm"), P("cap_backplate")] + CAP(0) + SHAFT, cam, [
        ("mozzo a morsetto", (60, hy, hz), (-220, -120), RED),
        ("piastra del braccio", (20, 170, 12), (-300, 60), RED),
        ("contropiastra", (30, 160, 21), (200, 230)),
    ], None))

    # F16 - esploso del riduttore: ogni pezzo sfila lungo il suo asse, nell'ordine in cui
    # si monta. Le viti che entrano da fuori (albero, M5, piastra sensori, staffa) restano
    # al loro posto o poco fuori; i pezzi che entrano dal lato aperto escono verso +X.
    sl = {q[0]: q for q in Pm["spacer_list"]}
    bx1, ct, cx, fx = Pm["box_x1"], Pm["cover_t"], Pm["compound_x"], Pm["flag_x"]
    lsx, csx = Pm["left_seat_x0"], Pm["cover_seat_x0"]
    # posizione in X del lato sinistro di ogni pezzo: (originale, esploso)
    X = dict(brgL=(lsx, 172), hall=(Pm["cav_x0"], 186), s1=(sl["s1"][1], 204), flag=(fx - 2.5, 216),
             s3=(sl["s3"][1], 229), g70=(sl["s3"][2], 258), s2=(sl["s2"][1], 276), brgC=(csx, 296),
             c1=(sl["c1"][1], 180), ptfe=(sl["c1"][2], 218), comp=(cx - 11, 226), b625=(cx + 8.9, 256),
             c2=(sl["c2"][1], 268), motor=(120.3, 283), pinion=(141, 318),
             cover=(csx, 344), m5w=(bx1 + ct, 366), m5n=(bx1 + ct + 1, 372), cvs=(bx1 + ct - 8, 380))
    dx = {k: v[1] - v[0] for k, v in X.items()}
    T = lambda k, s: "translate([%.2f,0,0]) %s" % (dx[k], s)
    SCR = "[0.30,0.31,0.35]"
    hs = [(hy + Pm["hall_screw_r"] * np.sin(np.radians(a)), hz + Pm["hall_screw_r"] * np.cos(np.radians(a)))
          for a in Pm["hall_screw_a"]]
    explo = [housing_gear, "color(%s) shaft_dummy();" % C["shaft"],
             # da fuori: vite M5 con rondella, due M3 x 16 della piastra, due M3 x 8 della staffa
             "color(%s){ at_yz(compound_yz,box_x0-1) vite_x(5,90,8.5,5); at_yz(compound_yz,box_x0-1) rondella_x(10,5.3,1); }" % SCR,
             "color(%s) for(p=[[%.2f,%.2f],[%.2f,%.2f]]) at_yz(p,box_x0-30) vite_x(3,16,5.5,3);" % (SCR, *hs[0], *hs[1]),
             "color(%s) for(s=mb_screws) translate([s[0],box_y0-22,s[1]]) rotate([-90,0,0]){ cylinder(d=3,h=8); translate([0,0,-3]) cylinder(d=5.5,h=3); }" % SCR,
             # asse di uscita
             "color([0.80,0.82,0.86]) " + T("brgL", "brg(left_seat_x0,hinge_yz,19,6,6);"),
             "color(%s) " % C["hall_plate"] + T("hall", 'part_placed("hall_plate");'),
             "color(%s) " % C["spacers"] + T("s1", "spacer_placed(spacer_list[0]);"),
             "color(%s) " % C["magnet_flag"] + T("flag", 'render() part_placed("magnet_flag",0);'),
             "color(%s) " % C["spacers"] + T("s3", "spacer_placed(spacer_list[2]);"),
             "color(%s) " % C["gears"] + T("g70", 'render() part_placed("output_gear");'),
             "color(%s) " % C["spacers"] + T("s2", "spacer_placed(spacer_list[1]);"),
             "color([0.80,0.82,0.86]) " + T("brgC", "brg(cover_seat_x0,hinge_yz,19,6,6);"),
             # perno del composto
             "color(%s) " % C["spacers"] + T("c1", "spacer_placed(spacer_list[3]);"),
             "color([0.97,0.97,0.93]) " + T("ptfe", "at_yz(compound_yz,%.2f) rondella_x(10,5.3,1);" % sl["c1"][2]),
             "color(%s) " % C["gears"] + T("comp", 'render() part_placed("compound_gear");'),
             "color([0.80,0.82,0.86]) " + T("b625", "brg(compound_x+8.9,compound_yz,16,5,5);"),
             "color(%s) " % C["spacers"] + T("c2", "spacer_placed(spacer_list[4]);"),
             "color(%s) " % SCR + T("m5w", "at_yz(compound_yz,box_x1+cover_t) rondella_x(10,5.3,1);"),
             "color(%s) " % SCR + T("m5n", "at_yz(compound_yz,box_x1+cover_t+1) dado_x(8,5,5);"),
             # motore con la staffa, poi il pignone
             "color(%s) " % C["motor_bracket"] + T("motor", 'render() part_placed("motor_bracket");'),
             "color(%s) " % C["motor"] + T("motor", "motor_dummy();"),
             "color(%s) " % SCR + T("motor", "for(e=byj_ears) at_yz(e,byj_face_x+14) mirror([1,0,0]) vite_x(3,8,5.5,3);"),
             "color(%s) " % C["gears"] + T("pinion", 'render() part_placed("motor_pinion");'),
             # coperchio e sue viti
             "color([0.20,0.45,0.70]) " + T("cover", 'render() part_placed("cover");'),
             "color(%s) " % SCR + T("cvs", "for(p=cover_screw_pts()) at_yz(p,box_x1+cover_t-8) mirror([1,0,0]) translate([-8,0,0]) vite_x(3,8,5.5,3);"),
             # assi tratteggiati
             "color([0.35,0.35,0.40]) { asse_x(hinge_yz,161,%.1f); asse_x(compound_yz,174,%.1f); asse_x(motor_yz,153,%.1f); }"
             % (X["cover"][1] + 30, X["m5n"][1] + 12, X["pinion"][1] + 12)]
    cam = Cam(to_view((225 + 700 * 0.42, 232 + 700 * 0.40, -25 + 700 * 0.815)), to_view((225, 232, -25)), (2100, 1250))

    def L(text, p, tx, ty, col=INK):
        """Etichetta con il riquadro nel punto (tx, ty) dell'immagine."""
        ax_, ay_ = cam.px(p)
        return (text, p, (tx - ax_, ty - ay_), col)

    Ky, Kz = K
    Mx = lambda k, a: X[k][1] + a                      # X esploso piu' un piccolo scarto
    jobs.append(("F16_esploso.png", explo, cam, [
        L("626ZZ", (Mx("brgL", 3), hy + 9.5, hz), 760, 165),
        L("piastra sensori", (Mx("hall", 4), hy + 27, hz), 905, 110),
        L("s1", (Mx("s1", 3), hy + 4.2, hz), 995, 270, BLU),
        L("bandierina\n+ magnete", (Mx("flag", 2.5), hy + 11, hz), 1075, 175),
        L("s3", (Mx("s3", 10), hy + 4.2, hz), 1078, 330, BLU),
        L("ingranaggio 70T\n+ grano M3", (Mx("g70", 5), hy + 28.8, hz), 1265, 235),
        L("s2", (Mx("s2", 6), hy + 4.2, hz), 1300, 385, BLU),
        L("626ZZ", (Mx("brgC", 3), hy + 9.5, hz), 1425, 355),
        L("coperchio", (Mx("cover", 11), 296, -10), 1580, 330),
        L("4 viti M3 x 8", (Mx("cvs", 9), 294, 4), 1860, 560),
        L("c1", (Mx("c1", 16), Ky - 4, Kz), 880, 765, BLU),
        L("rondella PTFE", (Mx("ptfe", 0.5), Ky - 5, Kz), 950, 840),
        L("composto\n42T / 14T", (Mx("comp", 15), Ky - 17.6, Kz), 1050, 960),
        L("625ZZ", (Mx("b625", 2.5), Ky - 8, Kz), 1165, 865),
        L("c2", (Mx("c2", 4.5), Ky - 3.7, Kz), 1225, 800, BLU),
        L("rondella + dado\nautobloccante M5", (Mx("m5n", 2.5), Ky - 4.6, Kz), 1850, 760),
        L("staffa + 28BYJ-48\n(2 viti M3 x 8)", (298, 190, -40), 1300, 1040, GRN),
        L("pignone 14T", (Mx("pinion", 3.5), M[0] + 6.4, M[1]), 1480, 1110),
        L("albero 6 x 100", (66, hy, hz), 235, 330),
        L("2 viti M3 x 16\n(piastra sensori)", (52, hs[0][0], hs[0][1]), 215, 520),
        L("vite M5 x 90\n(entra da fuori)", (166, Ky - 2.5, Kz), 835, 1085),
        L("2 viti M3 x 8\n(staffa, da sotto)", (147.5, 152, -40), 590, 1010, GRN),
    ], None))

    only = set(filter(None, os.environ.get("FIGURE_ONLY", "").split(",")))
    jobs = [j for j in jobs if not only or j[0] in only]
    with ThreadPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1)) as ex:
        list(ex.map(lambda j: render(j[0], j[1], j[2], j[3], j[4]), jobs))


# ------------------------------------------------------------ pezzi da stampare
def load_vertices(path):
    import struct
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        head = f.read(84)
        n = struct.unpack("<I", head[80:84])[0]
        if 84 + n * 50 == size:
            data = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
            return data[:, 12:48].copy().view("<f4").reshape(-1, 3).astype(float)
    vals = []
    with open(path, "r", errors="ignore") as f:
        for line in f:
            t = line.split()
            if t and t[0] == "vertex":
                vals.append([float(t[1]), float(t[2]), float(t[3])])
    return np.array(vals)


def figure_parts():
    """Tutti i pezzi da stampare, come escono dallo slicer, in scala fra loro."""
    stl = os.path.join(ROOT, "stl")
    rows = [[("housing", "housing"), ("cover", "cover"), ("bay_lid", "bay_lid"), ("bay_tray", "bay_tray")],
            [("mono_arm", "mono_arm"), ("motor_bracket", "motor_bracket"),
             ("cap_rest", "cap_rest (x2)"), ("cap_backplate", "cap_backplate")],
            [("output_gear", "output_gear"), ("compound_gear", "compound_gear"),
             ("motor_pinion", "motor_pinion"), ("magnet_flag", "magnet_flag"),
             ("hall_plate", "hall_plate"), ("spacers", "spacers")]]
    pitch_x = [250, 250, 120]
    step_y = [260, 190]
    lines, anchors = [], []
    y = 0.0
    for r, row in enumerate(rows):
        for c, (f, lab) in enumerate(row):
            shutil.copyfile(os.path.join(stl, f + ".stl"), os.path.join(WORK, f + ".stl"))
            v = load_vertices(os.path.join(WORK, f + ".stl"))
            lo, hi = v.min(0), v.max(0)
            x = c * pitch_x[r]
            lines.append('translate([%.1f,%.1f,%.1f]) color([0.20,0.45,0.70]) import("%s.stl");'
                         % (x - (lo[0] + hi[0]) / 2, y - (lo[1] + hi[1]) / 2, -lo[2], f))
            anchors.append((lab, x, y - (hi[1] - lo[1]) / 2))
        if r < len(step_y):
            y -= step_y[r]
    with open(os.path.join(WORK, "pezzi.scad"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    xs = [a[1] for a in anchors]
    ys = [a[2] for a in anchors]
    ctr = np.array([(min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2 + 60, 0.0])
    cam = Cam(ctr + np.array([220.0, -1500.0, 1400.0]), ctr, (2400, 1700))
    raw = os.path.join(WORK, "pezzi.png")
    subprocess.run([OPENSCAD, "-o", raw, "--imgsize=2400,1700", "--projection=o", cam.arg(),
                    "--colorscheme=Tomorrow", "pezzi.scad"], cwd=WORK, capture_output=True)
    img = np.asarray(Image.open(raw).convert("RGB"))
    bg = img[2, 2].astype(int)
    mask = np.abs(img.astype(int) - bg).sum(2) > 12
    ys_, xs_ = np.nonzero(mask)
    fig = plt.figure(figsize=(24, 17), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(tuple(bg / 255.0))
    ax.imshow(img, extent=(0, cam.W, cam.H, 0))
    ax.axis("off")
    for lab, x, yb in anchors:
        q = np.array([x, yb - 12, 0.0]) - cam.center
        px = cam.W / 2 + q.dot(cam.right) * cam.scale
        py = cam.H / 2 - q.dot(cam.up) * cam.scale
        ax.text(px, py, lab, ha="center", va="top", fontsize=20, color=INK, weight="bold")
    ax.set_xlim(max(0, xs_.min() - 90), min(cam.W, xs_.max() + 90))
    ax.set_ylim(min(cam.H, ys_.max() + 110), max(0, ys_.min() - 40))
    fig.savefig(os.path.join(OUT, "F04_pezzi.png"), dpi=70, bbox_inches="tight", pad_inches=0.1,
                facecolor=tuple(bg / 255.0))
    plt.close(fig)
    print("   %-28s ok" % "F04_pezzi.png")


# ------------------------------------------------------------ schemi 2D
def fig_corsa(Pm):
    hy, hz, dz = Pm["hinge_y"], Pm["hinge_z"], Pm["arm_dz"]
    rc, ro = Pm["cap_d"] / 2, Pm["ota_d"] / 2

    def cap(th):
        c, s = np.cos(np.radians(th)), np.sin(np.radians(th))
        Cc = np.array([hy + (-hy) * c - dz * s, hz + (-hy) * s + dz * c])
        d = np.array([c, s])
        return Cc + rc * d, Cc - rc * d

    fig, ax = plt.subplots(figsize=(15.5, 8.6))
    ax.add_patch(Rectangle((-700, -ro), 700, 2 * ro, fc="#d9dee3", ec=INK, lw=1.6, zorder=2))
    ax.text(-480, -100, "TUBO", ha="center", fontsize=13, color=GREY)
    ax.add_patch(Rectangle((Pm["box_z0"], Pm["box_y0"]), Pm["box_z1"] - Pm["box_z0"],
                           Pm["box_y1"] - Pm["box_y0"], fc=ACC, ec=INK, lw=1.5, alpha=.85, zorder=4))
    ax.add_patch(Rectangle((Pm["bay_z0"], Pm["bay_y0"]), Pm["bay_z1"] - Pm["bay_z0"],
                           Pm["bay_y1"] - Pm["bay_y0"], fc=VIO, ec=INK, lw=1.5, alpha=.85, zorder=4))
    for z in Pm["rest_z"]:
        top = hy - dz - Pm["cap_thickness"] / 2 - Pm["rest_pad"]
        ax.add_patch(Rectangle((z - 20, ro), 40, top - ro, fc=ORA, ec=INK, lw=1.1, zorder=5))
    ax.annotate("riduttore", ((Pm["box_z0"] + Pm["box_z1"]) / 2, Pm["box_y1"] - 10), (120, 380),
                fontsize=11, color=ACC, weight="bold", arrowprops=dict(arrowstyle="->", color=ACC, lw=1.3))
    ax.annotate("vano elettronica", ((Pm["bay_z0"] + Pm["bay_z1"]) / 2, Pm["bay_y1"] - 10), (-600, 430),
                fontsize=11, color=VIO, weight="bold", arrowprops=dict(arrowstyle="->", color=VIO, lw=1.3))
    ax.annotate("appoggi del tappo", (Pm["rest_z"][1], ro + 15), (-650, ro - 60),
                fontsize=11, color=ORA, weight="bold", arrowprops=dict(arrowstyle="->", color=ORA, lw=1.2))
    ax.plot([hz], [hy], "o", color=WARN, ms=10, zorder=8)
    ax.annotate("cerniera (albero di uscita)", (hz, hy), (130, 250), fontsize=11, color=WARN,
                weight="bold", arrowprops=dict(arrowstyle="->", color=WARN, lw=1.1))
    for t, col, lw in ((0, GRN, 3.2), (-60, "#b6c0c9", 1.3), (-120, "#b6c0c9", 1.3),
                       (-180, "#b6c0c9", 1.6), (-240, "#b6c0c9", 1.3), (Pm["open_angle"], GRN, 3.2)):
        p1, p2 = cap(t)
        ax.plot([p1[1], p2[1]], [p1[0], p2[0]], color=col, lw=lw, solid_capstyle="round", zorder=7)
    ax.annotate("0 gradi: chiuso", (17, -120), (140, -165), fontsize=12, color=GRN, weight="bold",
                arrowprops=dict(arrowstyle="->", color=GRN, lw=1.3))
    ax.annotate("%d gradi: appoggiato sul tubo" % Pm["open_angle"], (-330, hy - dz), (-330, 560),
                fontsize=12, color=GRN, weight="bold", ha="center",
                arrowprops=dict(arrowstyle="->", color=GRN, lw=1.3))
    R = np.hypot(hy + rc, dz)
    a0 = np.degrees(np.arctan2(dz, -(hy + rc)))
    tt = np.radians(np.linspace(0, Pm["open_angle"], 220) + a0)
    ax.plot(hz + R * np.sin(tt), hy + R * np.cos(tt), ls="--", color=WARN, lw=1.1, zorder=6)
    ax.set_xlim(-740, 760)
    ax.set_ylim(-260, 720)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "F03_corsa.png"), dpi=140, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("   %-28s ok" % "F03_corsa.png")


def fig_asse(Pm):
    """Pila assiale dell'albero di uscita e del perno del composto, in scala."""
    sp = {s[0]: s for s in Pm["spacer_list"]}
    fig, ax = plt.subplots(figsize=(15, 7.2))
    x0, x1 = Pm["box_x0"], Pm["box_x1"]
    cov = x1 + 3.2

    def wall(xa, xb, y, h, label=None):
        ax.add_patch(Rectangle((xa, y - h), xb - xa, 2 * h, fc="#9fb6cc", ec=INK, lw=1.2))

    def part(xa, xb, r, fc, label, y, dy=0, col=INK):
        ax.add_patch(Rectangle((xa, y - r), xb - xa, 2 * r, fc=fc, ec=INK, lw=1.1, zorder=3))
        if label:
            ax.annotate(label, ((xa + xb) / 2, y + r), ((xa + xb) / 2, y + r + 9 + dy), ha="center",
                        fontsize=9.5, color=col, weight="bold",
                        arrowprops=dict(arrowstyle="-", color=col, lw=0.8))

    # albero di uscita (riga in alto)
    y = 40
    ax.plot([Pm["arm_x"] - 8, Pm["arm_x"] - 8 + 100], [y, y], color=GREY, lw=5, solid_capstyle="butt", zorder=2)
    wall(x0, x0 + 4, y, 16)
    ax.add_patch(Rectangle((x0 + 4, y - 12.5), Pm["left_seat_x1"] - x0 - 4, 25, fc="#9fb6cc", ec=INK, lw=1.2))
    ax.add_patch(Rectangle((x1, y - 16), 3.2, 32, fc="#9fb6cc", ec=INK, lw=1.2))
    ax.add_patch(Rectangle((Pm["cover_seat_x0"], y - 13), x1 - Pm["cover_seat_x0"], 26, fc="#9fb6cc", ec=INK, lw=1.2))
    part(Pm["left_seat_x0"], Pm["left_seat_x1"], 9.5, "#d0d3d4", "626ZZ", y, 0)
    part(Pm["cover_seat_x0"], Pm["cover_seat_x1"], 9.5, "#d0d3d4", "626ZZ", y, 0)
    part(sp["s1"][1], sp["s1"][2], 4.25, "white", "s1", y, 10, BLU)
    part(Pm["flag_x"] - 2.5, Pm["flag_x"] + 2.5, 11, "#f7c518", "bandierina", y, 16)
    part(sp["s3"][1], sp["s3"][2], 4.25, "white", "s3", y, 10, BLU)
    part(125, 131, 28.8 / 2, "#f39c12", "70T", y, 0)
    ax.add_patch(Rectangle((131, y - 11), 4, 22, fc="#f39c12", ec=INK, lw=1.1, zorder=3))
    part(sp["s2"][1], sp["s2"][2], 4.25, "white", "s2", y, 10, BLU)
    part(Pm["arm_x"] - 8, Pm["arm_x"] + 8, 13, "#e74c3c", "mozzo braccio", y, 0, RED)
    ax.text(x0 - 30, y, "ALBERO\nDI USCITA\n6 x 100", ha="right", va="center", fontsize=10.5,
            weight="bold", color=INK)
    # perno del composto (riga in basso)
    y = -22
    ax.plot([x0 - 3, cov + 5], [y, y], color=GREY, lw=4, solid_capstyle="butt", zorder=2)
    wall(x0, x0 + 4, y, 12)
    ax.add_patch(Rectangle((x1, y - 12), 3.2, 24, fc="#9fb6cc", ec=INK, lw=1.2))
    part(sp["c1"][1], sp["c1"][2], 4.0, "white", "c1", y, 6, BLU)
    part(sp["c1"][2], sp["c1"][2] + 1.0, 5, "#bdc3c7", "", y)
    cx = Pm["compound_x"]
    part(cx - 11, cx + 11, 4, "#f39c12", "", y)
    part(cx - 8, cx - 2, 6.4, "#f39c12", "14T", y, 6)
    part(cx + 8, cx + 14, 17.6 / 2 + 4, "#f39c12", "42T + 625ZZ", y, 2)
    part(sp["c2"][1], sp["c2"][2], 3.75, "white", "c2", y, 6, BLU)
    ax.text(x0 - 30, y, "PERNO M5\nDEL COMPOSTO", ha="right", va="center", fontsize=10.5,
            weight="bold", color=INK)
    ax.text(x0 + 2, -52, "parete\nsinistra", ha="center", va="top", fontsize=9.5, color=INK)
    ax.text(x1 + 1.6, -52, "coperchio", ha="center", va="top", fontsize=9.5, color=INK)
    ax.text(sp["c1"][2] + 0.5, -40, "rondella\nPTFE", ha="center", va="top", fontsize=8.5, color=GREY)
    ax.set_xlim(Pm["arm_x"] - 70, cov + 20)
    ax.set_ylim(-62, 80)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "F06_assi.png"), dpi=150, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("   %-28s ok" % "F06_assi.png")


def fig_28byj():
    """Il 28BYJ-48 visto dal lato dell'albero: l'albero e' fuori centro di 8 mm."""
    fig, ax = plt.subplots(figsize=(8.6, 6.6))
    ax.add_patch(Circle((0, 0), 14, fc="#b5bcc4", ec=INK, lw=1.6))
    ax.add_patch(Polygon([(-17.5, -3.5), (17.5, -3.5), (21, 0), (17.5, 3.5), (-17.5, 3.5), (-21, 0)],
                         closed=True, fc="#8d99a6", ec=INK, lw=1.3, zorder=2))
    for x in (-17.5, 17.5):
        ax.add_patch(Circle((x, 0), 2.1, fc="white", ec=INK, lw=1.2, zorder=3))
    ax.add_patch(Rectangle((-8.75, -17), 17.5, 5, fc="#5dade2", ec=INK, lw=1.2, zorder=2))
    ax.add_patch(Circle((0, 8), 4.5, fc="#d5d8dc", ec=INK, lw=1.2, zorder=3))
    ax.add_patch(Circle((0, 8), 2.5, fc="#566573", ec=INK, lw=1.0, zorder=4))
    ax.plot([0, 0], [0, 8], color=WARN, lw=2, zorder=5)
    ax.plot([0], [0], "+", color=INK, ms=14, mew=1.6, zorder=6)
    ax.annotate("8 mm", (0, 5.8), (-9, 13), color=WARN, fontsize=12, weight="bold", zorder=6,
                ha="center", arrowprops=dict(arrowstyle="-", color=WARN, lw=0.8))
    ax.annotate("albero (qui va il pignone)", (0, 10.5), (-2, 22), ha="center", fontsize=11, color=INK,
                arrowprops=dict(arrowstyle="->", color=INK))
    ax.annotate("centro della carcassa", (0, 0), (-24, -10), ha="center", fontsize=11, color=INK,
                arrowprops=dict(arrowstyle="->", color=INK))
    ax.annotate("cappuccio azzurro\ncon i 5 fili", (0, -15), (15, -24), ha="center", fontsize=11, color=ACC,
                arrowprops=dict(arrowstyle="->", color=ACC))
    ax.annotate("fori delle orecchie\ninterasse 35 mm", (17.5, 0), (24, 13), ha="center", fontsize=11,
                color=INK, arrowprops=dict(arrowstyle="->", color=INK))
    ax.set_xlim(-34, 34)
    ax.set_ylim(-30, 27)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "F09b_28byj.png"), dpi=150, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("   %-28s ok" % "F09b_28byj.png")


def fig_vassoio(Pm):
    """Vassoio del vano visto dall'alto, in scala, con schede e coperchio."""
    fig, ax = plt.subplots(figsize=(12.5, 8.8))
    x0, x1 = Pm["box_x0"] + 3.5, Pm["box_x1"] - 0.5
    z0, z1 = Pm["bay_z0"] + 3.5, Pm["bay_z1"] - 3.5

    # asse orizzontale = Z (retro a sinistra), verticale = X (coperchio in alto)
    def R(xa, xb, za, zb, **kw):
        ax.add_patch(Rectangle((za, xa), zb - za, xb - xa, **kw))

    R(Pm["box_x0"], Pm["box_x1"] + 3, Pm["bay_z0"], Pm["bay_z1"], fc="#e8eef4", ec=INK, lw=1.6)
    R(x0, x1, z0, z1, fc="#f7f9fa", ec=GREY, lw=1.2)
    R(Pm["box_x1"], Pm["box_x1"] + 3, Pm["bay_z0"], Pm["bay_z1"], fc="#b39ddb", ec=INK, lw=1.2)
    ax.text((Pm["bay_z0"] + Pm["bay_z1"]) / 2, Pm["box_x1"] + 8, "COPERCHIO DEL VANO (qui la presa 12 V e l'USB)",
            ha="center", fontsize=11, color=VIO, weight="bold")
    ax.text((Pm["bay_z0"] + Pm["bay_z1"]) / 2, Pm["box_x0"] - 6, "parete sinistra (lato braccio)",
            ha="center", va="top", fontsize=10.5, color=INK)
    for name, key, col in (("Arduino Nano", "nano", BLU), ("LM2596", "buck", RED), ("ULN2003", "uln", GRN)):
        pos, size, holes = Pm[key + "_pos"], Pm[key + "_size"], Pm[key + "_holes"]
        R(pos[0] - size[0] / 2, pos[0] + size[0] / 2, pos[1] - size[1] / 2, pos[1] + size[1] / 2,
          fc="white", ec=col, lw=2.2)
        for sx in (-1, 1):
            for sz in (-1, 1):
                ax.add_patch(Circle((pos[1] + sz * holes[1] / 2, pos[0] + sx * holes[0] / 2), 1.6,
                                    fc=col, ec=col))
        ax.text(pos[1], pos[0], name, ha="center", va="center", fontsize=12, color=col, weight="bold")
    u = Pm["usb_hole"]
    ax.add_patch(Rectangle((u[0], Pm["box_x1"]), u[1] - u[0], 3, fc="white", ec=BLU, lw=1.6, hatch="//"))
    ax.annotate("foro USB", ((u[0] + u[1]) / 2, Pm["box_x1"] + 3), ((u[0] + u[1]) / 2 - 10, Pm["box_x1"] + 17),
                fontsize=10.5, color=BLU, ha="center", arrowprops=dict(arrowstyle="->", color=BLU))
    j = Pm["jack_yz"]
    ax.add_patch(Circle((j[1], Pm["box_x1"] + 1.5), 4.1, fc="white", ec=RED, lw=1.6))
    ax.annotate("presa 12 V", (j[1], Pm["box_x1"] + 3), (j[1] + 12, Pm["box_x1"] + 17), fontsize=10.5,
                color=RED, ha="center", arrowprops=dict(arrowstyle="->", color=RED))
    ax.annotate("passaggio cavi dal riduttore\n(motore e sensori)", (Pm["bay_z1"], (Pm["cable_slot"][0] + Pm["cable_slot"][1]) / 2),
                (Pm["bay_z1"] + 14, 100), fontsize=10.5, color=ORA, ha="left",
                arrowprops=dict(arrowstyle="->", color=ORA))
    ax.add_patch(Rectangle((Pm["bay_z1"] - 3, Pm["cable_slot"][0]), 6, Pm["cable_slot"][1] - Pm["cable_slot"][0],
                           fc=ORA, ec=INK, lw=1.0))
    ax.text(-84, 140, "morsetti\n+5 V / GND\ne condensatore", ha="center", va="center", fontsize=10,
            color=GREY, style="italic")
    ax.set_xlim(Pm["bay_z0"] - 12, Pm["bay_z1"] + 70)
    ax.set_ylim(Pm["box_x0"] - 14, Pm["box_x1"] + 22)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "F11b_vassoio.png"), dpi=150, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("   %-28s ok" % "F11b_vassoio.png")


def fig_cablaggio():
    fig, ax = plt.subplots(figsize=(12.4, 8.0))
    ax.set_xlim(0, 124)
    ax.set_ylim(0, 80)
    ax.axis("off")

    def box(x, y, w, h, title, sub="", fc="#eef3f7", ec=INK):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2",
                                    fc=fc, ec=ec, lw=1.8))
        ax.text(x + w / 2, y + h - 2.6, title, ha="center", va="top", fontsize=10.5, weight="bold", color=INK)
        if sub:
            ax.text(x + w / 2, y + h - 6.6, sub, ha="center", va="top", fontsize=8.3, color="#4a5c6b")

    def seg(pts, color, lw=2.0):
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, lw=lw,
                solid_capstyle="round", solid_joinstyle="round", zorder=1)

    def node(x, y, color):
        ax.add_patch(Circle((x, y), 0.7, fc=color, ec=color, zorder=3))

    box(2, 63, 22, 10, "12 V DC", "alimentatore del setup\n(fusibile 1 A sul cavo)", fc="#fdecea", ec=RED)
    box(30, 63, 17, 10, "PRESA DC", "sul coperchio del vano", fc="#fdecea", ec=RED)
    box(53, 61, 30, 12, "LM2596", "12 V -> 5,0 V\nREGOLARE A VUOTO, PRIMA", fc="#fdecea", ec=RED)
    seg([(24, 68), (30, 68)], RED)
    seg([(47, 68.8), (53, 68.8)], RED)
    seg([(47, 66.4), (53, 66.4)], BLK)
    ax.text(50, 70.2, "+12", ha="center", fontsize=8, color=RED)
    ax.text(50, 64.4, "GND", ha="center", fontsize=8, color=BLK)
    y5, yg = 55.0, 50.0
    seg([(3, y5), (110, y5)], RED, 2.6)
    seg([(3, yg), (110, yg)], BLK, 2.6)
    ax.text(111.5, y5, "+5 V (morsetto WAGO)", ha="left", va="center", fontsize=9.5, weight="bold", color=RED)
    ax.text(111.5, yg, "GND (morsetto WAGO)", ha="left", va="center", fontsize=9.5, weight="bold", color=BLK)
    seg([(75, 61), (75, y5)], RED)
    node(75, y5, RED)
    seg([(61, 61), (61, 57.5), (16, 57.5), (16, yg)], BLK)
    node(16, yg, BLK)
    seg([(26, y5), (26, 53.4)], RED)
    node(26, y5, RED)
    seg([(23.6, 53.4), (28.4, 53.4)], RED, 2.6)
    seg([(23.6, 52.0), (28.4, 52.0)], BLK, 2.6)
    seg([(26, 52.0), (26, yg)], BLK)
    node(26, yg, BLK)
    ax.text(30, 52.7, "1000 uF 10-16 V (attenzione alla polarita')", va="center", fontsize=8.6, color="#4a5c6b")
    box(8, 26, 32, 16, "Arduino Nano", "USB verso il PC\n(dal foro nel coperchio)")
    box(54, 26, 26, 16, "ULN2003", "scheda driver")
    box(92, 26, 24, 16, "28BYJ-48", "5 V, nel riduttore", fc="#eaf3ea", ec=GRN)
    box(8, 3, 44, 15, "2 x Hall A3144 (nel riduttore)",
        "CLOSED = sede verso il bordo anteriore\nOPEN = sede verso il fondo della scatola\n100 nF fra VCC e GND di ognuno", fc="#eaf3ea", ec=GRN)
    seg([(64, y5), (64, 42)], RED)
    node(64, y5, RED)
    ax.text(65, 47, "+", fontsize=9, color=RED, weight="bold")
    seg([(72, yg), (72, 42)], BLK)
    node(72, yg, BLK)
    ax.text(73, 45, "-", fontsize=11, color=BLK, weight="bold")
    seg([(32, yg), (32, 42)], BLK)
    node(32, yg, BLK)
    ax.text(33, 45, "GND", fontsize=8.6, color=BLK)
    seg([(4.5, y5), (4.5, 20.5), (12, 20.5), (12, 18)], RED)
    node(4.5, y5, RED)
    ax.text(3.6, 34, "5 V ai\nsensori", fontsize=8.6, color=RED, ha="right", va="center")
    seg([(7, yg), (7, 22.5), (17, 22.5), (17, 18)], BLK)
    node(7, yg, BLK)
    ax.text(7.8, 24.6, "GND", fontsize=8.6, color=BLK)
    for i, (d, inn) in enumerate([("D2", "IN1"), ("D3", "IN2"), ("D4", "IN3"), ("D5", "IN4")]):
        y = 39.5 - i * 3.2
        seg([(40, y), (54, y)], BLU, 1.7)
        ax.text(47, y + 0.5, "%s -> %s" % (d, inn), ha="center", fontsize=8.4, color=BLU)
    seg([(80, 34), (92, 34)], GRN, 2.2)
    ax.text(86, 35.2, "connettore\nbianco 5 poli", ha="center", va="bottom", fontsize=8.4, color=GRN)
    seg([(29, 26), (29, 18)], BLU, 1.7)
    ax.text(29.9, 23.4, "D10 <- CLOSED", fontsize=8.6, color=BLU)
    seg([(37, 26), (37, 20.8), (46, 20.8), (46, 18)], BLU, 1.7)
    ax.text(37.9, 19.4, "D11 <- OPEN", fontsize=8.6, color=BLU)
    ax.text(88, 11, "Il firmware usa le resistenze di pull-up\ninterne del Nano: il sensore porta il\n"
            "pin a GND quando il magnete e' davanti.", ha="center", va="center", fontsize=9, color="#4a5c6b")
    ax.text(62, 0.4, "Il Nano si alimenta dalla USB. Il motore NO: prende i 5 V dal buck. "
            "Tutti i GND in comune.", ha="center", fontsize=9.4, color=RED, style="italic")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "F12_cablaggio.png"), dpi=170, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("   %-28s ok" % "F12_cablaggio.png")


def fig_appoggi(Pm):
    """Dove vanno cinghie e appoggi lungo il tubo, visto di lato."""
    fig, ax = plt.subplots(figsize=(14, 4.6))
    ro = Pm["ota_d"] / 2
    ax.add_patch(Rectangle((-520, ro - 60), 520, 60, fc="#d9dee3", ec=INK, lw=1.4))
    ax.text(-470, ro - 30, "tubo (parte alta)", va="center", fontsize=11, color=GREY)
    ax.plot([0, 0], [ro - 70, ro + 150], color=INK, lw=1.2, ls="--")
    ax.text(3, ro + 140, "bocca del tubo", fontsize=10.5, color=INK, va="top")
    top = Pm["hinge_y"] - Pm["arm_dz"] - Pm["cap_thickness"] / 2 - Pm["rest_pad"]
    for i, z in enumerate(Pm["rest_z"]):
        ax.add_patch(Rectangle((z - 20, ro), 40, top - ro, fc=ORA, ec=INK, lw=1.2))
        ax.annotate("", (0, ro + 85 + 18 * i), (z, ro + 85 + 18 * i),
                    arrowprops=dict(arrowstyle="<->", color=ORA, lw=1.2))
        ax.text(z / 2, ro + 87 + 18 * i, "%.0f mm" % abs(z), ha="center", va="bottom", fontsize=10.5,
                color=ORA, weight="bold")
    ax.text(Pm["rest_z"][1], top + 6, "appoggio 2", ha="center", va="bottom", fontsize=10.5, color=INK)
    ax.text(Pm["rest_z"][0], top + 6, "appoggio 1", ha="center", va="bottom", fontsize=10.5, color=INK)
    for zs, name in (("front_saddle_z", "cinghia\nanteriore"), ("rear_saddle_z", "cinghia\nposteriore")):
        z0 = Pm[zs][0] + (3 if zs == "front_saddle_z" else 4)
        ax.add_patch(Rectangle((z0, ro - 60), 25, 64, fc="#2c3e50", ec=INK, lw=1.0, alpha=0.8))
        ax.text(z0 + 12.5, ro - 66, name, ha="center", va="top", fontsize=9.5, color=INK)
    ax.set_xlim(-540, 60)
    ax.set_ylim(ro - 100, ro + 160)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "F15_appoggi.png"), dpi=150, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("   %-28s ok" % "F15_appoggi.png")


# ----------------------------------------------------------------------- main
def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(WORK, exist_ok=True)
    shutil.copyfile(SCAD, os.path.join(WORK, "modello.scad"))
    Pm = read_params()
    only = set(sys.argv[1:])
    print("Schemi:")
    for f in (fig_corsa, fig_asse, fig_vassoio, fig_appoggi):
        if not only or f.__name__ in only:
            f(Pm)
    if not only or "fig_28byj" in only:
        fig_28byj()
    if not only or "fig_cablaggio" in only:
        fig_cablaggio()
    print("Pezzi stampati:")
    if not only or "figure_parts" in only:
        figure_parts()
    print("Render 3D (OpenSCAD, qualche minuto):")
    if not only or "figure_renders" in only:
        figure_renders(Pm)
    print("Fatto:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
