#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) 2026 Johannes1979I
"""
GP1 FlipCap V4.2 - genera un COLLADA (.dae) dell'assieme a partire dagli STL
reali, gia' posizionati come nell'assieme dello SCAD.

Serve per aprire il progetto in SketchUp, che importa il .dae nativamente.
Le trasformazioni qui sotto devono restare allineate ad assembly() in
gp1_flipcap_V4_2.scad.

Uso:  python docs/genera_dae.py
Esce: docs/GP1_V4_2_assieme_SketchUp.dae
"""
import os

import numpy as np

from verifica_collisioni import load_stl  # riusa il lettore STL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(ROOT, "stl")
OUT = os.path.join(ROOT, "docs", "GP1_V4_2_assieme_SketchUp.dae")

HINGE = (212.0, -25.0)
I3 = np.eye(3)
# rotate([90,0,90]) dello SCAD: (a,b,c) -> (c,a,b)
CYC = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], float)

# nome, file, rotazione 3x3, traslazione, colore RGB
PARTS = [
    ("housing",       "housing",       I3,  (0, 0, 0),              (0.08, 0.26, 0.45)),
    ("coperchio",     "cover",         I3,  (0, 0, 0),              (0.10, 0.32, 0.55)),
    ("staffa_motore", "motor_bracket", I3,  (140, 268, -25),        (0.20, 0.55, 0.30)),
    ("ruota_uscita",  "output_gear",   I3,  (125, 212, -25),        (0.95, 0.52, 0.08)),
    ("composto",      "compound_gear", I3,  (133, 245.6, -25),      (0.95, 0.52, 0.08)),
    ("pignone",       "motor_pinion",  I3,  (141, 268, -25),        (0.95, 0.52, 0.08)),
    ("monobraccio",   "mono_arm",      I3,  (70, 212, -25),         (0.80, 0.12, 0.10)),
    ("contropiastra", "lid_backplate", I3,  (70, 212, 17.75),       (0.55, 0.10, 0.08)),
    ("piastra_hall",  "hall_plate",    CYC, (88, 212, -25),         (0.85, 0.85, 0.90)),
    ("bandierina",    "magnet_flag",   I3,  (99, 212, -25),         (0.95, 0.75, 0.10)),
]


def weld(tri):
    v = tri.reshape(-1, 3)
    key = np.round(v * 1000).astype(np.int64)
    uq, inv = np.unique(key, axis=0, return_inverse=True)
    return uq.astype(np.float64) / 1000.0, inv.reshape(-1, 3)


def main():
    geo, mat, nodes = [], [], []
    for i, (name, f, rot, tra, col) in enumerate(PARTS):
        path = os.path.join(STL, f + ".stl")
        if not os.path.exists(path):
            print("manca", path)
            continue
        verts, idx = weld(load_stl(path))
        gid = "g%d" % i
        pos = " ".join("%.4g" % x for x in verts.ravel())
        p = " ".join(str(x) for x in idx.ravel())
        geo.append(
            f'<geometry id="{gid}" name="{name}"><mesh>'
            f'<source id="{gid}-p"><float_array id="{gid}-pa" count="{verts.size}">{pos}</float_array>'
            f'<technique_common><accessor source="#{gid}-pa" count="{len(verts)}" stride="3">'
            f'<param name="X" type="float"/><param name="Y" type="float"/><param name="Z" type="float"/>'
            f"</accessor></technique_common></source>"
            f'<vertices id="{gid}-v"><input semantic="POSITION" source="#{gid}-p"/></vertices>'
            f'<triangles count="{len(idx)}" material="m{i}">'
            f'<input semantic="VERTEX" source="#{gid}-v" offset="0"/><p>{p}</p>'
            f"</triangles></mesh></geometry>"
        )
        r, g, b = col
        mat.append(
            f'<effect id="e{i}"><profile_COMMON><technique sid="c"><lambert>'
            f'<diffuse><color>{r} {g} {b} 1</color></diffuse>'
            f"</lambert></technique></profile_COMMON></effect>"
        )
        m = np.eye(4)
        m[:3, :3] = rot
        m[:3, 3] = tra
        mtx = " ".join("%.6g" % x for x in m.ravel())
        nodes.append(
            f'<node id="n{i}" name="{name}"><matrix>{mtx}</matrix>'
            f'<instance_geometry url="#{gid}"><bind_material><technique_common>'
            f'<instance_material symbol="m{i}" target="#mat{i}"/>'
            f"</technique_common></bind_material></instance_geometry></node>"
        )

    materials = "".join(
        f'<material id="mat{i}" name="{PARTS[i][0]}"><instance_effect url="#e{i}"/></material>'
        for i in range(len(PARTS))
    )
    dae = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">'
        "<asset><up_axis>Z_UP</up_axis>"
        '<unit name="millimeter" meter="0.001"/></asset>'
        "<library_effects>" + "".join(mat) + "</library_effects>"
        "<library_materials>" + materials + "</library_materials>"
        "<library_geometries>" + "".join(geo) + "</library_geometries>"
        '<library_visual_scenes><visual_scene id="scene" name="GP1_FlipCap_V4_2">'
        + "".join(nodes)
        + "</visual_scene></library_visual_scenes>"
        '<scene><instance_visual_scene url="#scene"/></scene></COLLADA>\n'
    )
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(dae)
    print("scritto %s (%.1f MB, %d pezzi)"
          % (OUT, os.path.getsize(OUT) / 1e6, len(nodes)))


if __name__ == "__main__":
    main()
