#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) 2026 Johannes1979I
"""
GP1 FlipCap V6 - assieme COLLADA (.dae) per SketchUp e simili.

I pezzi vengono esportati da OpenSCAD gia' in posizione di montaggio
(orient="placed", stessa cache di verifica_collisioni.py), quindi l'assieme
segue sempre il file .scad. Tappo chiuso; tubo e disco del tappo sono
sagome semplici, non pezzi da stampare.

Uso:  python docs/genera_dae.py
Esce: docs/GP1_V6_assieme.dae
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verifica_collisioni as V  # noqa: E402

OUT = os.path.join(V.ROOT, "docs", "GP1_V6_assieme.dae")

COLORS = {
    "housing": (0.13, 0.36, 0.60), "cover": (0.20, 0.45, 0.70), "bay_lid": (0.45, 0.30, 0.70),
    "bay_tray": (0.86, 0.86, 0.89), "motor_bracket": (0.20, 0.62, 0.32),
    "hall_plate": (0.92, 0.92, 0.96), "spacers": (0.98, 0.98, 0.98),
    "output_gear": (0.95, 0.52, 0.08), "compound_gear": (0.95, 0.52, 0.08),
    "motor_pinion": (0.95, 0.52, 0.08), "magnet_flag": (0.97, 0.78, 0.10),
    "mono_arm": (0.80, 0.12, 0.10), "cap_backplate": (0.55, 0.10, 0.08),
    "cap_rest": (0.90, 0.60, 0.15), "cap_rest_2": (0.90, 0.60, 0.15),
    "motor_dummy": (0.42, 0.42, 0.47), "tappo": (0.16, 0.45, 0.20), "tubo": (0.30, 0.30, 0.34),
}


def cylinder(r, z0, z1, n=120, center=(0.0, 0.0)):
    """Cilindro chiuso lungo Z come lista di triangoli."""
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ring = np.c_[center[0] + r * np.cos(a), center[1] + r * np.sin(a)]
    tri = []
    for i in range(n):
        j = (i + 1) % n
        p0, p1 = ring[i], ring[j]
        b0, b1 = [*p0, z0], [*p1, z0]
        t0, t1 = [*p0, z1], [*p1, z1]
        tri += [[b0, b1, t1], [b0, t1, t0],
                [[center[0], center[1], z0], b1, b0], [[center[0], center[1], z1], t0, t1]]
    return np.array(tri, float)


def weld(tri):
    v = tri.reshape(-1, 3)
    key = np.round(v * 1000).astype(np.int64)
    uq, inv = np.unique(key, axis=0, return_inverse=True)
    return uq.astype(np.float64) / 1000.0, inv.reshape(-1, 3)


def main():
    os.makedirs(V.CACHE, exist_ok=True)
    exe = V.openscad_exe()
    P = V.read_params(exe)
    meshes = V.export_placed(exe)
    meshes["cap_rest_2"] = meshes["cap_rest"] + np.array([0, 0, P["rest_z"][1] - P["rest_z"][0]])
    hz, dz, t = P["hinge_z"], P["arm_dz"], P["cap_thickness"]
    meshes["tappo"] = cylinder(P["cap_d"] / 2, hz + dz - t / 2, hz + dz + t / 2)
    meshes["tubo"] = cylinder(P["ota_d"] / 2, -650, 0)

    geo, eff, mats, nodes = [], [], [], []
    for i, (name, tri) in enumerate(meshes.items()):
        verts, idx = weld(tri)
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
            f"</triangles></mesh></geometry>")
        r, g, b = COLORS.get(name, (0.6, 0.6, 0.6))
        eff.append(f'<effect id="e{i}"><profile_COMMON><technique sid="c"><lambert>'
                   f'<diffuse><color>{r} {g} {b} 1</color></diffuse>'
                   f"</lambert></technique></profile_COMMON></effect>")
        mats.append(f'<material id="mat{i}" name="{name}"><instance_effect url="#e{i}"/></material>')
        nodes.append(f'<node id="n{i}" name="{name}">'
                     f'<instance_geometry url="#{gid}"><bind_material><technique_common>'
                     f'<instance_material symbol="m{i}" target="#mat{i}"/>'
                     f"</technique_common></bind_material></instance_geometry></node>")
    dae = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">'
           "<asset><up_axis>Z_UP</up_axis><unit name=\"millimeter\" meter=\"0.001\"/></asset>"
           "<library_effects>" + "".join(eff) + "</library_effects>"
           "<library_materials>" + "".join(mats) + "</library_materials>"
           "<library_geometries>" + "".join(geo) + "</library_geometries>"
           '<library_visual_scenes><visual_scene id="scene" name="GP1_FlipCap_V6">'
           + "".join(nodes) + "</visual_scene></library_visual_scenes>"
           '<scene><instance_visual_scene url="#scene"/></scene></COLLADA>\n')
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(dae)
    print("scritto %s (%.1f MB, %d pezzi)" % (OUT, os.path.getsize(OUT) / 1e6, len(nodes)))


if __name__ == "__main__":
    main()
