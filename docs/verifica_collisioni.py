#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) 2026 Johannes1979I
"""
GP1 FlipCap V6 - verifica geometrica automatica.

Lavora sulle mesh vere, non su stime:
  1) ogni STL di stl/ e' un solido unico (nessuna isola staccata)
  2) i pezzi fermi, montati, non si compenetrano (l'appoggio di faccia e'
     ammesso, la compenetrazione no) e che luce resta fra loro
  3) corsa completa 0 -> -270 gradi: braccio, contropiastra e disco del
     tappo contro scatola, coperchi, appoggi e tubo; bandierina contro
     piastra dei sensori
  4) posizione di parcheggio: il tappo sugli appoggi, la luce sopra il vano
     elettronica
  5) extracorsa se il sensore OPEN non scatta (limite MAX_MOVE_STEPS)

I pezzi in posizione di montaggio vengono esportati al volo da OpenSCAD
(orient="placed"), cosi' la verifica segue sempre il file .scad. Anche i
parametri (quota della cerniera, diametri...) vengono letti dal .scad.

Uso:     python docs/verifica_collisioni.py
Scrive:  docs/VERIFICA_COLLISIONI.txt
Serve:   numpy, scipy e OpenSCAD. Se openscad non e' nel PATH, indica il
         percorso con la variabile d'ambiente OPENSCAD.
"""
import hashlib
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile

import numpy as np
from scipy.spatial import cKDTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAD = os.environ.get("GP1_SCAD", os.path.join(ROOT, "gp1_flipcap_V6.scad"))
STL = os.environ.get("GP1_STL", os.path.join(ROOT, "stl"))
CACHE = os.path.join(tempfile.gettempdir(), "gp1_v6_verifica")

CONTACT_TOL = 0.25   # mm: sotto questa profondita' e' appoggio, non interferenza
STEPS_PER_TURN = 2038 * 15   # full-step per giro dell'albero di uscita
MAX_MOVE_STEPS = 24100       # come nel firmware

PLACED = ["housing", "cover", "motor_bracket", "hall_plate", "spacers",
          "bay_lid", "bay_tray", "output_gear", "compound_gear",
          "motor_pinion", "magnet_flag", "mono_arm", "cap_backplate",
          "cap_rest", "motor_dummy"]


# ------------------------------------------------------------------ OpenSCAD
def openscad_exe():
    for c in (os.environ.get("OPENSCAD"), shutil.which("openscad"),
              r"C:\Program Files\OpenSCAD\openscad.exe",
              "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD",
              "/usr/bin/openscad"):
        if c and os.path.exists(c):
            return c
    sys.exit("OpenSCAD non trovato: imposta la variabile d'ambiente OPENSCAD")


def read_params(exe):
    """Legge i parametri che servono direttamente dal file .scad."""
    names = ["hinge_y", "hinge_z", "arm_x", "arm_dz", "cap_d", "cap_thickness",
             "ota_d", "ota_clearance", "open_angle", "flag_x", "rest_z",
             "rest_pad", "bay_y1", "box_x0", "box_x1"]
    # include<> con percorso assoluto non funziona su Windows: si lavora su
    # una copia del .scad accanto alla sonda
    shutil.copyfile(SCAD, os.path.join(CACHE, "modello.scad"))
    probe = os.path.join(CACHE, "probe.scad")
    with open(probe, "w") as f:
        f.write("include <modello.scad>\n")
        for n in names:
            f.write('echo(str("P %s=", %s));\n' % (n, n))
    echo = os.path.join(CACHE, "probe.echo")
    subprocess.run([exe, "-o", echo, "-D", 'part="none"', probe], capture_output=True)
    with open(echo, errors="ignore") as f:
        txt = f.read()
    p = {}
    for n, v in re.findall(r'ECHO: "P (\w+)=([^"]+)"', txt):
        v = v.strip()
        p[n] = [float(x) for x in v.strip("[]").split(",")] if v.startswith("[") else float(v)
    missing = [n for n in names if n not in p]
    if missing:
        sys.exit("parametri non letti dal .scad: %s" % missing)
    return p


def export_placed(exe):
    """Esporta i pezzi in posizione di montaggio; li rifa' solo se il .scad cambia."""
    with open(SCAD, "rb") as f:
        tag = hashlib.sha1(f.read()).hexdigest()[:12]
    d = os.path.join(CACHE, tag)
    os.makedirs(d, exist_ok=True)
    procs = []
    for p in PLACED:
        out = os.path.join(d, p + ".stl")
        if not os.path.exists(out):
            procs.append(subprocess.Popen(
                [exe, "-o", out, "-D", 'part="%s"' % p, "-D", 'orient="placed"', SCAD],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        while len([q for q in procs if q.poll() is None]) >= os.cpu_count():
            procs[0].wait()
    for q in procs:
        q.wait()
    return {p: load_stl(os.path.join(d, p + ".stl")) for p in PLACED}


# ----------------------------------------------------------------- mesh I/O
def load_stl(path):
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        head = f.read(84)
        n = struct.unpack("<I", head[80:84])[0]
        if 84 + n * 50 == size:
            data = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
            return data[:, 12:48].copy().view("<f4").reshape(n, 3, 3).astype(np.float64)
    vals = []
    with open(path, "r", errors="ignore") as f:
        for line in f:
            s = line.split()
            if s and s[0] == "vertex":
                vals.append([float(s[1]), float(s[2]), float(s[3])])
    return np.array(vals).reshape(-1, 3, 3)


def islands(tri):
    """Numero di corpi connessi (per vertice condiviso)."""
    v = tri.reshape(-1, 3)
    key = np.round(v * 1000).astype(np.int64)
    _, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.reshape(len(tri), 3)
    parent = np.arange(inv.max() + 1)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for t in inv:
        a, b, c = find(t[0]), find(t[1]), find(t[2])
        r = min(a, b, c)
        parent[a] = parent[b] = parent[c] = r
    return len({find(i) for i in np.unique(inv)})


def volume(tri):
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    return np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6000.0


def sample(tri, step=1.2, normals=False):
    """Punti sulla superficie con spaziatura ~step mm (e, a richiesta, normali uscenti).

    Due contributi: punti lungo gli spigoli di ogni triangolo, cosi' anche i
    triangoli lunghi e sottili delle mesh CAD restano coperti, e punti casuali
    all'interno in numero proporzionale all'area. Il generatore ha seme fisso:
    due esecuzioni danno lo stesso risultato.
    """
    rng = np.random.default_rng(12345)
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    cr = np.cross(b - a, c - a)
    area = 0.5 * np.linalg.norm(cr, axis=1)
    nrm = cr / np.maximum(2 * area, 1e-12)[:, None]
    pts, nor = [tri.reshape(-1, 3)], [np.repeat(nrm, 3, axis=0)]
    for p0, p1 in ((a, b), (b, c), (c, a)):
        n = np.maximum(np.ceil(np.linalg.norm(p1 - p0, axis=1) / step).astype(int), 1)
        idx = np.repeat(np.arange(len(tri)), n)
        t = np.concatenate([np.arange(k) / k for k in n])
        pts.append(p0[idx] + (p1[idx] - p0[idx]) * t[:, None])
        nor.append(nrm[idx])
    cnt = np.floor(2.0 * area / step ** 2 + rng.random(len(tri))).astype(int)
    idx = np.repeat(np.arange(len(tri)), cnt)
    r1, r2 = np.sqrt(rng.random(len(idx))), rng.random(len(idx))
    pts.append(a[idx] * (1 - r1)[:, None] + b[idx] * (r1 * (1 - r2))[:, None] + c[idx] * (r1 * r2)[:, None])
    nor.append(nrm[idx])
    P = np.vstack(pts)
    return (P, np.vstack(nor)) if normals else P


def _inside_axis(pts, tri, axis, chunk=1500):
    """Point-in-mesh per ray casting lungo +axis (0=X, 1=Y, 2=Z)."""
    u1, u2 = [i for i in (0, 1, 2) if i != axis]
    v0, v1, v2 = tri[:, 0], tri[:, 1], tri[:, 2]
    amin = np.minimum.reduce([v0[:, u1], v1[:, u1], v2[:, u1]])
    amax = np.maximum.reduce([v0[:, u1], v1[:, u1], v2[:, u1]])
    bmin = np.minimum.reduce([v0[:, u2], v1[:, u2], v2[:, u2]])
    bmax = np.maximum.reduce([v0[:, u2], v1[:, u2], v2[:, u2]])
    e1, e2 = v1 - v0, v2 - v0
    d = np.zeros(3)
    d[axis] = 1.0
    h = np.cross(d, e2)
    a = np.einsum("ij,ij->i", e1, h)
    ok = np.abs(a) > 1e-12
    res = np.zeros(len(pts), bool)
    for s in range(0, len(pts), chunk):
        P = pts[s:s + chunk]
        m = ((P[:, None, u1] >= amin) & (P[:, None, u1] <= amax)
             & (P[:, None, u2] >= bmin) & (P[:, None, u2] <= bmax) & ok)
        cnt = np.zeros(len(P), int)
        pi, ti = np.nonzero(m)
        if len(pi):
            T = P[pi] - v0[ti]
            f = 1.0 / a[ti]
            uu = f * np.einsum("ij,ij->i", T, h[ti])
            q = np.cross(T, e1[ti])
            vv = f * np.einsum("j,ij->i", d, q)
            tt = f * np.einsum("ij,ij->i", e2[ti], q)
            hit = (uu >= 0) & (uu <= 1) & (vv >= 0) & (uu + vv <= 1) & (tt > 1e-9)
            np.add.at(cnt, pi[hit], 1)
        res[s:s + chunk] = (cnt % 2) == 1
    return res


def inside(pts, tri):
    """Point-in-mesh robusto: voto di maggioranza su tre raggi ortogonali."""
    if len(pts) == 0:
        return np.zeros(0, bool)
    v = (_inside_axis(pts, tri, 0).astype(np.int8)
         + _inside_axis(pts, tri, 1).astype(np.int8)
         + _inside_axis(pts, tri, 2).astype(np.int8))
    return v >= 2


def in_box(pts, tri, pad=0.5):
    v = tri.reshape(-1, 3)
    lo, hi = v.min(0) - pad, v.max(0) + pad
    return np.all((pts >= lo) & (pts <= hi), axis=1)


def surface_distance(pts, tri, reach=4.0, chunk=256):
    """Distanza esatta di ogni punto dalla superficie della mesh (fino a reach)."""
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    lo = np.minimum.reduce([a, b, c]) - reach
    hi = np.maximum.reduce([a, b, c]) + reach
    ab, ac, bc = b - a, c - a, c - b
    nrm = np.cross(ab, ac)
    nl = np.linalg.norm(nrm, axis=1)
    good = nl > 1e-12
    nrm[good] /= nl[good, None]
    out = np.full(len(pts), float(reach))

    def seg(p, s0, v):
        t = np.clip(np.einsum("ij,ij->i", p - s0, v) / np.maximum(np.einsum("ij,ij->i", v, v), 1e-18), 0, 1)
        return np.linalg.norm(p - (s0 + v * t[:, None]), axis=1)

    for s in range(0, len(pts), chunk):
        P = pts[s:s + chunk]
        m = np.all((P[:, None, :] >= lo) & (P[:, None, :] <= hi), axis=2)
        pi, ti = np.nonzero(m)
        if not len(pi):
            continue
        p, A, n = P[pi], a[ti], nrm[ti]
        dp = np.einsum("ij,ij->i", p - A, n)
        q = p - dp[:, None] * n
        # coordinate baricentriche della proiezione
        v0, v1, v2 = ab[ti], ac[ti], q - A
        d00 = np.einsum("ij,ij->i", v0, v0); d01 = np.einsum("ij,ij->i", v0, v1)
        d11 = np.einsum("ij,ij->i", v1, v1); d20 = np.einsum("ij,ij->i", v2, v0)
        d21 = np.einsum("ij,ij->i", v2, v1)
        den = d00 * d11 - d01 * d01
        ok = (np.abs(den) > 1e-18) & good[ti]
        den[~ok] = 1.0
        v = (d11 * d20 - d01 * d21) / den
        w = (d00 * d21 - d01 * d20) / den
        inside_tri = ok & (v >= 0) & (w >= 0) & (v + w <= 1)
        d = np.minimum.reduce([seg(p, A, ab[ti]), seg(p, A, ac[ti]), seg(p, b[ti], bc[ti])])
        d = np.where(inside_tri, np.abs(dp), d)
        best = np.full(len(P), float(reach))
        np.minimum.at(best, pi, d)
        out[s:s + chunk] = np.minimum(out[s:s + chunk], best)
    return out


def penetration(pts, nor, tri):
    """Punti di A che, arretrati di CONTACT_TOL dentro A, stanno ancora dentro B.

    Due facce appoggiate l'una sull'altra non contano: arretrando, i punti di A
    lasciano B. Resta solo la sovrapposizione vera, piu' profonda di CONTACT_TOL.
    Ritorna (numero di punti, profondita' massima fra i punti trovati).
    """
    q = pts - nor * CONTACT_TOL
    sel = in_box(q, tri)
    if not sel.any():
        return 0, 0.0
    ins = np.zeros(len(q), bool)
    ins[sel] = inside(q[sel], tri)
    if not ins.any():
        return 0, 0.0
    # i punti che cadono esattamente sul bordo di una faccia d'appoggio danno
    # esiti casuali al test dei raggi: vale solo cio' che sta davvero dentro
    d = surface_distance(pts[ins], tri)
    deep = d > CONTACT_TOL
    return int(deep.sum()), float(d.max()) if deep.any() else 0.0


def exact_clearance(pts, tri, tree=None, keep=400):
    """Luce esatta fra una nuvola di punti e una mesh: si rifiniscono i punti piu' vicini."""
    if tree is None:
        tree = cKDTree(sample(tri, 1.5))
    d, _ = tree.query(pts, k=1)
    near = np.argsort(d)[:keep]
    reach = float(d[near].max()) + 3.0
    return float(surface_distance(pts[near], tri, reach=reach).min())


def rot_about_hinge(pts, deg, hy, hz):
    c, s = np.cos(np.radians(deg)), np.sin(np.radians(deg))
    y, z = pts[:, 1] - hy, pts[:, 2] - hz
    return np.stack([pts[:, 0], hy + c * y - s * z, hz + s * y + c * z], 1)


# ----------------------------------------------------------------- controlli
def main():
    os.makedirs(CACHE, exist_ok=True)
    exe = openscad_exe()
    P = read_params(exe)
    hy, hz = P["hinge_y"], P["hinge_z"]
    open_angle = P["open_angle"]
    ota_r = P["ota_d"] / 2

    out = []

    def say(s=""):
        print(s)
        out.append(s)

    say("GP1 FlipCap V6 - VERIFICA GEOMETRICA AUTOMATICA")
    say("=" * 70)
    say("cerniera Y=%.1f Z=%.1f  braccio X=%.1f  tappo D=%.0f sp.%.1f  tubo D=%.0f"
        % (hy, hz, P["arm_x"], P["cap_d"], P["cap_thickness"], P["ota_d"]))
    say()

    # --- 1) solidi unici -----------------------------------------------
    say("1) PEZZI DA STAMPARE (stl/): ogni file deve essere un solido unico")
    total = 0.0
    ok_all = True
    for f in sorted(x for x in os.listdir(STL) if x.endswith(".stl")):
        tri = load_stl(os.path.join(STL, f))
        n_isl = islands(tri)
        v = tri.reshape(-1, 3)
        size = v.max(0) - v.min(0)
        vol = volume(tri)
        # gli assi di prova sono facoltativi: non entrano nel totale
        total += 0 if f.startswith("test_") else vol * (2 if f.startswith("cap_rest") else 1)
        # i distanziali sono cinque tubetti separati per scelta; il perno di prova ha la sua ghiera
        expected = 5 if f.startswith("spacers") else (2 if f.startswith("test_pin") else 1)
        good = n_isl == expected
        ok_all &= good
        say("   %s %-18s corpi=%d  %6.1f x %6.1f x %6.1f mm  %6.1f cm3  base Z=%.2f"
            % ("OK" if good else "!!", f[:-4], n_isl, size[0], size[1], size[2],
               vol, v[:, 2].min()))
    say("   -> %s" % ("tutti i pezzi sono solidi unici" if ok_all else "ATTENZIONE"))
    say("   -> materiale totale (appoggi x2): %.0f cm3" % total)
    say()

    M = export_placed(exe)
    rest2 = M["cap_rest"] + np.array([0, 0, P["rest_z"][1] - P["rest_z"][0]])

    # --- 2) pezzi fermi --------------------------------------------------
    say("2) PEZZI FERMI MONTATI: compenetrazioni e luci")
    static = ["housing", "cover", "motor_bracket", "hall_plate", "spacers",
              "bay_lid", "bay_tray", "output_gear", "compound_gear",
              "motor_pinion", "magnet_flag", "motor_dummy"]
    # coppie che ingranano: i denti si avvicinano per progetto
    meshing = {("compound_gear", "output_gear"), ("compound_gear", "motor_pinion")}
    # coppie da non confrontare: l'albero del motore attraversa il pignone
    skip = {("motor_dummy", "motor_pinion")}
    samples = {k: sample(M[k], 0.8, normals=True) for k in static}
    trees = {k: cKDTree(samples[k][0]) for k in static}
    bad = 0
    for i, a in enumerate(static):
        for b in static[i + 1:]:
            pair = tuple(sorted((a, b)))
            if pair in skip:
                continue
            va, vb = M[a].reshape(-1, 3), M[b].reshape(-1, 3)
            if np.any(va.min(0) > vb.max(0) + 3) or np.any(vb.min(0) > va.max(0) + 3):
                continue
            dmin = exact_clearance(samples[a][0], M[b], trees[b])
            if pair in meshing:
                say("   %-14s <-> %-14s ingranano (luce minima %.2f mm)" % (a, b, dmin))
                continue
            # si controllano solo i punti vicini all'altro pezzo: una sovrapposizione
            # vera attraversa per forza la superficie dell'altro pezzo
            na = trees[b].query(samples[a][0], k=1, distance_upper_bound=3.0)[0] < 3.0
            nb = trees[a].query(samples[b][0], k=1, distance_upper_bound=3.0)[0] < 3.0
            n1, d1 = penetration(samples[a][0][na], samples[a][1][na], M[b])
            n2, d2 = penetration(samples[b][0][nb], samples[b][1][nb], M[a])
            pen = n1 + n2
            bad += pen
            if pen:
                state = "!! COMPENETRAZIONE %d punti, prof. %.2f mm" % (pen, max(d1, d2))
            elif dmin < 0.3:
                state = "appoggio di faccia"
            else:
                state = "luce %.2f mm" % dmin
            if dmin < 6 or pen:
                say("   %-14s <-> %-14s %s" % (a, b, state))
    say("   -> %s" % ("nessuna compenetrazione" if bad == 0 else "CI SONO COMPENETRAZIONI"))
    say()

    # --- 3) corsa completa -----------------------------------------------
    say("3) CORSA COMPLETA 0 -> %d gradi" % open_angle)
    fixed = {k: M[k] for k in ("housing", "cover", "bay_lid", "motor_bracket")}
    fixed_pts = {k: sample(v, 1.5) for k, v in fixed.items()}
    fixed_pts["appoggi"] = np.vstack([sample(M["cap_rest"], 1.5), sample(rest2, 1.5)])
    fixed_tree = {k: cKDTree(v) for k, v in fixed_pts.items()}

    arm = np.vstack([sample(M["mono_arm"], 1.0), sample(M["cap_backplate"], 1.0)])
    flag = sample(M["magnet_flag"], 0.6)
    hall_tree = cKDTree(sample(M["hall_plate"], 0.8))
    fixed_mesh = dict(fixed)
    fixed_mesh["appoggi"] = np.vstack([M["cap_rest"], rest2])

    # disco del tappo: due facce e bordo
    rng = np.random.default_rng(7)
    n = 50000
    r = np.sqrt(rng.random(n)) * (P["cap_d"] / 2)
    a = rng.random(n) * 2 * np.pi
    disc = np.stack([r * np.cos(a), r * np.sin(a)], 1)
    rim_a = np.linspace(0, 2 * np.pi, 1400, endpoint=False)
    rim = np.stack([np.cos(rim_a), np.sin(rim_a)], 1) * (P["cap_d"] / 2)
    t = P["cap_thickness"]
    cap_local = np.vstack([
        np.c_[disc, np.full(n, -t / 2)], np.c_[disc, np.full(n, t / 2)],
        np.c_[rim, np.full(len(rim), -t / 2)], np.c_[rim, np.zeros(len(rim))],
        np.c_[rim, np.full(len(rim), t / 2)]])
    # sistema del tappo -> globale a braccio fermo (angolo 0)
    cap0 = np.c_[cap_local[:, 0], cap_local[:, 1], cap_local[:, 2] + P["arm_dz"] + hz]

    def tube_clear(pts):
        """Luce dal tubo: distanza dalla superficie del cilindro per Z<0."""
        rad = np.hypot(pts[:, 0], pts[:, 1])
        m = pts[:, 2] < 0
        if not m.any():
            return 1e9, 0
        d = rad[m] - ota_r
        return float(d.min()), int((d < 0).sum())

    worst = {}

    def keep(key, val, ang, pts=None, mesh=None):
        if key not in worst or val < worst[key][0]:
            worst[key] = (val, ang, pts, mesh)

    angles = list(range(0, int(open_angle) - 1, -3))
    if angles[-1] != int(open_angle):
        angles.append(int(open_angle))
    for ang in angles:
        A = rot_about_hinge(arm, ang, hy, hz)
        C = rot_about_hinge(cap0, ang, hy, hz)
        for k, tr in fixed_tree.items():
            keep("braccio - " + k, float(tr.query(A, k=1)[0].min()), ang, A, k)
            if k == "appoggi" and ang == int(open_angle):
                continue          # a fine corsa il tappo appoggia sugli appoggi per progetto
            keep("tappo - " + k, float(tr.query(C, k=1)[0].min()), ang, C, k)
        dt, nin = tube_clear(A)
        keep("braccio - tubo", dt if nin == 0 else -1.0, ang)
        dt, nin = tube_clear(C)
        keep("tappo - tubo", dt if nin == 0 else -1.0, ang)
        F = rot_about_hinge(flag, ang, hy, hz)
        keep("bandierina - piastra sensori", float(hall_tree.query(F, k=1)[0].min()), ang, F, "hall")
    fixed_mesh["hall"] = M["hall_plate"]
    fixed_tree["hall"] = hall_tree
    for k in sorted(worst):
        v, ang, pts, mk = worst[k]
        if mk is not None and v < 60:
            v = exact_clearance(pts, fixed_mesh[mk], fixed_tree[mk])
        flag_s = "!!" if v < 2.0 else "  "
        say("   %s luce minima %-32s %7.2f mm  (a %d gradi)" % (flag_s, k, v, ang))
    say("   (tappo - appoggi e' escluso a fine corsa: li' il tappo ci appoggia)")
    say()

    # --- 4) parcheggio ---------------------------------------------------
    say("4) PARCHEGGIO (%d gradi)" % open_angle)
    C = rot_about_hinge(cap0, open_angle, hy, hz)
    lower = C[:, 1].min()
    rv = np.vstack([M["cap_rest"].reshape(-1, 3), rest2.reshape(-1, 3)])
    say("   faccia inferiore del tappo: Y = %.1f mm" % lower)
    say("   sommita' degli appoggi:     Y = %.1f mm  (+%.0f mm di EVA = appoggio)"
        % (rv[:, 1].max(), P["rest_pad"]))
    say("   coperchio vano elettronica: Y = %.1f mm  -> luce %.1f mm"
        % (P["bay_y1"], lower - P["bay_y1"]))
    say()

    # --- 5) extracorsa ----------------------------------------------------
    say("5) EXTRACORSA (sensore OPEN guasto)")
    nominal = round(abs(open_angle) / 360 * STEPS_PER_TURN)
    stop = -MAX_MOVE_STEPS / STEPS_PER_TURN * 360
    say("   corsa nominale %d passi, MAX_MOVE_STEPS %d -> arresto a %.1f gradi"
        % (nominal, MAX_MOVE_STEPS, stop))
    say("   oltre i %d gradi il tappo e' gia' sugli appoggi: il motore si ferma"
        % open_angle)
    say("   contro di loro (il 28BYJ in stallo non si danneggia) e il firmware")
    say("   lo spegne al piu' tardi a MAX_MOVE_STEPS, segnalando lo stato 3.")
    say()
    say("=" * 70)

    with open(os.path.join(ROOT, "docs", "VERIFICA_COLLISIONI.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
