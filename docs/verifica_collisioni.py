#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) 2026 Johannes1979I
"""
GP1 FlipCap V4.2 - verifica geometrica automatica sugli STL esportati.

Controlla, direttamente sulle mesh che finiscono in stampa:
  1) che ogni pezzo sia un solido unico (nessuna isola staccata)
  2) che il monobraccio non compenetri l'housing su tutta la corsa
  3) che la staffa motore non compenetri l'housing ne' il treno ingranaggi
  4) la luce minima fra disco del tappo e housing lungo tutta la corsa
  5) la luce minima fra braccio e tubo OTA

Uso:  python docs/verifica_collisioni.py
Richiede: numpy, scipy
"""
import os
import struct
import sys

import numpy as np
from scipy.spatial import cKDTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(ROOT, "stl")

# --- geometria di assieme (deve combaciare con gp1_flipcap_V4_2.scad) ---
HINGE_Y, HINGE_Z = 212.0, -25.0
ARM_X = 70.0
ARM_DZ = 42.0
FLAG_X = 99.0
OPEN_ANGLE = -90.0
LID_D = 374.0
LID_T = 1.5
OTA_D = 362.0
BOX = dict(x=(84.0, 156.0), y=(174.0, 310.0), z=(-62.0, 12.0))


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
    """Ritorna la lista dei sottoinsiemi di triangoli connessi per vertice."""
    v = tri.reshape(-1, 3)
    key = np.round(v * 1000).astype(np.int64)
    uq, inv = np.unique(key, axis=0, return_inverse=True)
    parent = np.arange(len(uq))

    def find(a):
        r = a
        while parent[r] != r:
            r = parent[r]
        while parent[a] != r:
            parent[a], a = r, parent[a]
        return r

    idx = inv.reshape(len(tri), 3)
    for t in idx:
        a, b, c = find(t[0]), find(t[1]), find(t[2])
        r = min(a, b, c)
        parent[a] = parent[b] = parent[c] = r
    roots = np.array([find(i) for i in range(len(uq))])
    lab = roots[idx[:, 0]]
    u, cnt = np.unique(lab, return_counts=True)
    return [tri[lab == u[i]] for i in np.argsort(-cnt)]


def sample(tri, step=1.2):
    """Nuvola di punti sulla superficie, passo ~step mm."""
    pts = [tri.reshape(-1, 3)]
    e1, e2 = tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
    area = 0.5 * np.linalg.norm(np.cross(e1, e2), axis=1)
    n = np.clip((np.sqrt(area) / step).astype(int) + 1, 1, 14)
    for k in range(1, 15):
        sel = n == k
        if not sel.any():
            continue
        t = tri[sel]
        a, u, v = t[:, 0], t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]
        for i in range(k + 1):
            for j in range(k + 1 - i):
                pts.append(a + u * (i / k) + v * (j / k))
    return np.vstack(pts)


def _inside_axis(pts, tri, axis, chunk=2000):
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
    """Point-in-mesh robusto: voto di maggioranza su tre raggi ortogonali.

    Un singolo raggio da falsi positivi quando colpisce esattamente uno
    spigolo della mesh; il voto 2-su-3 li elimina.
    """
    v = (_inside_axis(pts, tri, 0).astype(np.int8)
         + _inside_axis(pts, tri, 1).astype(np.int8)
         + _inside_axis(pts, tri, 2).astype(np.int8))
    return v >= 2


def rotx(deg):
    c, s = np.cos(np.radians(deg)), np.sin(np.radians(deg))
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


CONTACT_TOL = 0.25   # mm: sotto questa profondita' e' appoggio, non interferenza


def penetration(pts, tri, tree):
    """Separa l'appoggio di faccia dalla compenetrazione vera.

    Le facce progettate a contatto (colonnine della piastra sensori sulla
    parete, flangia della staffa sul soffitto) risultano 'dentro' al test
    punto-in-mesh ma hanno profondita' nulla. Conta solo cio' che affonda.
    """
    ins = inside(pts, tri)
    if not ins.any():
        return 0, 0, 0.0
    d, _ = tree.query(pts[ins], k=1)
    deep = d > CONTACT_TOL
    return int(ins.sum() - deep.sum()), int(deep.sum()), float(d.max())


# ----------------------------------------------------------------- controlli
def main():
    out = []

    def say(s=""):
        print(s)
        out.append(s)

    say("GP1 FlipCap V4.2 - VERIFICA GEOMETRICA AUTOMATICA")
    say("=" * 66)
    say()

    # --- 1) solidi unici -----------------------------------------------
    say("1) INTEGRITA' DEI SOLIDI (ogni pezzo = 1 corpo connesso)")
    parts = sorted(f for f in os.listdir(STL)
                   if f.endswith(".stl") and os.path.isfile(os.path.join(STL, f)))
    ok_all = True
    meshes = {}
    for f in parts:
        tri = load_stl(os.path.join(STL, f))
        meshes[f[:-4]] = tri
        isl = islands(tri)
        v = tri.reshape(-1, 3)
        mn, mx = v.min(0), v.max(0)
        a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
        vol = np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6000.0
        flag = "OK " if len(isl) == 1 else "!! "
        ok_all &= len(isl) == 1
        say(f"   {flag}{f[:-4]:16s} isole={len(isl)}  "
            f"{mx[0]-mn[0]:6.1f} x {mx[1]-mn[1]:6.1f} x {mx[2]-mn[2]:6.1f} mm   "
            f"{vol:6.1f} cm3")
    say(f"   -> {'TUTTI I PEZZI SONO SOLIDI UNICI' if ok_all else 'ATTENZIONE: isole presenti'}")
    say()

    H = meshes["housing"]
    ph = sample(H, 1.5)

    # --- 2) braccio vs housing -----------------------------------------
    say("2) MONOBRACCIO vs HOUSING (corsa 0 -> %d gradi)" % OPEN_ANGLE)
    A = meshes["mono_arm"]
    pa = sample(A, 1.2)
    say(f"   punti campionati sul braccio: {len(pa)}")
    worst = 0
    tree_h = cKDTree(ph)
    dmin_glob, ang_glob = 1e9, None
    for ang in range(0, int(OPEN_ANGLE) - 1, -3):
        P = (rotx(ang) @ pa.T).T + np.array([ARM_X, HINGE_Y, HINGE_Z])
        ins = inside(P, H)
        worst += int(ins.sum())
        d, _ = tree_h.query(P, k=1)
        if d.min() < dmin_glob:
            dmin_glob, ang_glob = d.min(), ang
    say(f"   punti in compenetrazione su tutta la corsa: {worst}")
    say(f"   luce minima braccio-housing: {dmin_glob:.2f} mm (a {ang_glob} gradi)")
    say(f"   -> {'NESSUNA COLLISIONE' if worst == 0 else 'COLLISIONE'}")
    say()

    # --- 3) staffa motore ------------------------------------------------
    say("3) STAFFA MOTORE vs HOUSING / INGRANAGGI")
    MB = meshes["motor_bracket"]
    pm = sample(MB, 1.2) + np.array([140.0, 268.0, -25.0])
    n_c, n_p, dmax = penetration(pm, H, tree_h)
    say(f"   appoggio di faccia (voluto): {n_c} punti")
    say(f"   compenetrazione vera:        {n_p} punti (prof. max {dmax:.2f} mm)")
    gears = {
        "output_gear": np.array([125.0, HINGE_Y, HINGE_Z]),
        "compound_gear": np.array([133.0, 245.6, HINGE_Z]),
        "motor_pinion": np.array([141.0, 268.0, HINGE_Z]),
    }
    for g, off in gears.items():
        pg = sample(meshes[g], 1.0) + off
        # distanza minima staffa <-> ingranaggio
        d, _ = cKDTree(pm).query(pg, k=1)
        say(f"   luce staffa <-> {g:14s}: {d.min():6.2f} mm")
    say(f"   -> {'STAFFA LIBERA' if n_p == 0 else 'COLLISIONE'}")
    say()

    # --- 4) disco tappo vs housing --------------------------------------
    say("4) DISCO TAPPO (D=%.0f, sp.%.1f) vs HOUSING" % (LID_D, LID_T))
    rng = np.random.default_rng(7)
    n = 60000
    r = np.sqrt(rng.random(n)) * (LID_D / 2)
    a = rng.random(n) * 2 * np.pi
    base = np.stack([r * np.cos(a), r * np.sin(a), np.zeros(n)], 1)
    base = np.repeat(base, 2, axis=0)
    base[0::2, 2] = +LID_T / 2
    base[1::2, 2] = -LID_T / 2
    tree_box = cKDTree(ph[ph[:, 0] > 78])
    worst_d, worst_a = 1e9, None
    for ang in range(0, int(OPEN_ANGLE) - 1, -5):
        P = (rotx(ang) @ (base + np.array([0, -HINGE_Y, ARM_DZ])).T).T \
            + np.array([0, HINGE_Y, HINGE_Z])
        sel = ((P[:, 0] > 70) & (P[:, 0] < 170) & (P[:, 1] > 150)
               & (P[:, 1] < 330) & (P[:, 2] > -80) & (P[:, 2] < 60))
        if not sel.any():
            continue
        d, _ = tree_box.query(P[sel], k=1)
        if d.min() < worst_d:
            worst_d, worst_a = d.min(), ang
        say(f"   {ang:5d} gradi : luce = {d.min():6.2f} mm")
    say(f"   -> luce minima su tutta la corsa: {worst_d:.2f} mm (a {worst_a} gradi)")
    say()

    # --- 5) braccio vs tubo OTA ------------------------------------------
    say("5) MONOBRACCIO vs TUBO OTA (D=%.0f, bordo in Z=0)" % OTA_D)
    worst = 1e9
    worst_ang = None
    for ang in range(0, int(OPEN_ANGLE) - 1, -3):
        P = (rotx(ang) @ pa.T).T + np.array([ARM_X, HINGE_Y, HINGE_Z])
        rad = np.hypot(P[:, 0], P[:, 1])
        # dentro il cilindro OTA e dietro il piano frontale -> collisione
        pen = (rad < OTA_D / 2 + 1.2) & (P[:, 2] < 0)
        if pen.any():
            say(f"   !! {ang} gradi: {pen.sum()} punti dentro il tubo")
            worst = -1
        else:
            m = rad < OTA_D / 2 + 1.2
            if m.any():
                z = P[m, 2].min()
                if z < worst:
                    worst, worst_ang = z, ang
    if worst >= 0:
        say(f"   -> il braccio resta sempre davanti al tubo; quota minima Z = {worst:.2f} mm "
            f"(a {worst_ang} gradi)")
    say()

    # --- 6) sistema Hall --------------------------------------------------
    say("6) PIASTRA SENSORI vs HOUSING e vs BANDIERINA MAGNETE")
    HP = meshes["hall_plate"]
    # rotate([90,0,90]): (a,b,c) -> (c,a,b)
    php = sample(HP, 1.0)[:, [2, 0, 1]] + np.array([88.0, HINGE_Y, HINGE_Z])
    n_c, n_p, dmax = penetration(php, H, tree_h)
    say(f"   appoggio di faccia (voluto): {n_c} punti")
    say(f"   compenetrazione vera:        {n_p} punti (prof. max {dmax:.2f} mm)")
    MF = sample(meshes["magnet_flag"], 1.0)
    tree_hp = cKDTree(php)
    dmin = 1e9
    dang = None
    for ang in range(0, int(OPEN_ANGLE) - 1, -3):
        P = (rotx(ang) @ MF.T).T + np.array([FLAG_X, HINGE_Y, HINGE_Z])
        d, _ = tree_hp.query(P, k=1)
        if d.min() < dmin:
            dmin, dang = d.min(), ang
    say(f"   luce minima piastra <-> bandierina: {dmin:.2f} mm (a {dang} gradi)")
    say(f"   -> {'SISTEMA HALL LIBERO' if n_p == 0 and dmin > 1.0 else 'DA CONTROLLARE'}")
    say()

    # --- 7) extracorsa in avaria -----------------------------------------
    say("7) EXTRACORSA (sensore OPEN guasto): da dove il firmware deve fermare")
    say("   corsa nominale = %d passi full-step" % round(abs(OPEN_ANGLE) / 360 * 30570))
    for ang in range(int(OPEN_ANGLE), int(OPEN_ANGLE) - 21, -5):
        P = (rotx(ang) @ (base + np.array([0, -HINGE_Y, ARM_DZ])).T).T \
            + np.array([0, HINGE_Y, HINGE_Z])
        sel = ((P[:, 0] > 70) & (P[:, 0] < 170) & (P[:, 1] > 150)
               & (P[:, 1] < 330) & (P[:, 2] > -80) & (P[:, 2] < 60))
        d = tree_box.query(P[sel], k=1)[0].min()
        Q = (rotx(ang) @ pa.T).T + np.array([ARM_X, HINGE_Y, HINGE_Z])
        da = tree_h.query(Q, k=1)[0].min()
        st = round(abs(ang) / 360 * 30570)
        mark = "  <- OLTRE QUI SI TOCCA" if d < 3 else ""
        say(f"   {ang:5d} gradi ({st:5d} passi): disco {d:6.2f} mm, "
            f"braccio {da:5.2f} mm{mark}")
    say("   -> MAX_MOVE_STEPS nel firmware deve restare 8100 (-95,4 gradi)")
    say()
    say("=" * 66)

    with open(os.path.join(ROOT, "docs", "VERIFICA_COLLISIONI.txt"), "w") as f:
        f.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
