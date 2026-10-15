// SPDX-License-Identifier: CERN-OHL-S-2.0
// GP1 FlipCap V6 - angolari di fermo per la scatola del tappo
// Quattro angolari bassi incollati al tubo (colla a caldo) agli spigoli esterni
// delle due selle: tengono ferma la scatola lungo il tubo e attorno al tubo
// anche se le cinghie a strappo si allentano col freddo della notte.
// Ognuno abbraccia uno spigolo della sella: un braccio lungo contro la testata
// (blocca lo scivolamento lungo il tubo) e un braccio corto contro il fianco
// (blocca la rotazione attorno al tubo), senza invadere il passaggio delle cinghie.
// Stesso sistema di riferimento del modello gp1_flipcap_V6.scad.
//
// Uso: F5 = posizione sul tubo; part="print" = i quattro pezzi pronti da stampare.

part = "placed";            // placed | print
idx  = -1;                  // con part="print": -1 = tutti e quattro, 0..3 = un pezzo solo
$fn = 360;

ota_d      = 362;           // diametro esterno del tubo (stesso del progetto)
saddle_x   = [84, 150];     // fianchi delle selle (piani X)
front_end  = -30;           // testata anteriore della sella anteriore (verso la bocca)
rear_end   = -195;          // testata posteriore della sella posteriore
lc_front   = 2.5;           // braccio corto: contatto col fianco, prima della cinghia anteriore (Z -33)
lc_rear    = 3.5;           // idem prima della cinghia posteriore (Z -191)

H   = 8;      // altezza sopra il tubo (le selle sono alte 9 + 1,2 di EVA)
W   = 8;      // spessore delle pareti, anche superficie d'incollaggio
Le  = 25;     // braccio lungo, lungo la testata
g   = 0.4;    // gioco verso la sella
txt_depth = 0.6;

r0 = ota_d / 2;

module shell(r1, r2, z0, z1) {
    translate([0, 0, z0]) difference() {
        cylinder(r = r2, h = z1 - z0);
        translate([0, 0, -1]) cylinder(r = r1, h = z1 - z0 + 2);
    }
}
// rettangolo nel piano X-Z, esteso in Y quanto basta
module xz_box(xa, xb, za, zb) {
    translate([min(xa, xb), 0, min(za, zb)]) cube([abs(xb - xa), r0 + 50, abs(zb - za)]);
}

// xe: piano del fianco; sx = +1 se la sella sta a X maggiori; ze: piano della
// testata; sz = +1 se l'esterno e' verso +Z.
module angolare(xe, sx, ze, sz, lc, label) {
    zo = ze + sz * (g + W);                     // faccia esterna (verso fuori)
    difference() {
        intersection() {
            shell(r0, r0 + H, min(ze - sz * lc, zo) - 1, max(ze - sz * lc, zo) + 1);
            union() {
                xz_box(xe - sx * (g + W), xe + sx * Le, ze + sz * g, zo);          // braccio lungo
                xz_box(xe - sx * (g + W), xe - sx * g, ze - sz * lc, zo);          // braccio corto
            }
        }
        // sigla incisa sulla faccia esterna, leggibile da fuori
        xm = xe + sx * (Le - g - W) / 2;
        phi = asin(xm / (r0 + H / 2));
        u = [sin(phi), cos(phi), 0];  n = [0, 0, sz];  rr = cross(u, n);
        p = (r0 + H / 2) * u + [0, 0, zo];
        multmatrix([[rr[0], u[0], n[0], p[0]], [rr[1], u[1], n[1], p[1]], [rr[2], u[2], n[2], p[2]], [0, 0, 0, 1]])
            translate([0, 0, -txt_depth]) linear_extrude(txt_depth + 1)
                text(label, size = 4.2, halign = "center", valign = "center",
                     font = "Liberation Sans:style=Bold");
    }
}

PARTS = [
    // xe,          sx, ze,        sz, lc,       sigla
    [saddle_x[0], +1, front_end, +1, lc_front, "A-ALTO"],
    [saddle_x[1], -1, front_end, +1, lc_front, "A-BASSO"],
    [saddle_x[0], +1, rear_end,  -1, lc_rear,  "P-ALTO"],
    [saddle_x[1], -1, rear_end,  -1, lc_rear,  "P-BASSO"],
];

module placed(i) { p = PARTS[i]; angolare(p[0], p[1], p[2], p[3], p[4], p[5]); }

// Stampa: la faccia esterna (piana, con la sigla) sul piatto. Le sezioni lungo Z
// si restringono salendo: niente sbalzi, niente supporti, curvatura del tubo esatta.
module printed(i) {
    p = PARTS[i]; zo = p[2] + p[3] * (g + W);
    xm = p[0] + p[1] * (Le - g - W) / 2;
    ym = sqrt(pow(r0 + H / 2, 2) - xm * xm);
    if (p[3] > 0) translate([-xm, ym, zo]) rotate([180, 0, 0]) placed(i);
    else          translate([-xm, -ym, -zo]) placed(i);
}

if (part == "placed") for (i = [0:3]) color("orange") placed(i);
else if (idx >= 0) printed(idx);
else for (i = [0:3]) translate([(i % 2) * 60, floor(i / 2) * 75, 0]) printed(i);
