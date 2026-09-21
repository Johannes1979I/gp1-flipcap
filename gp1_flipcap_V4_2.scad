// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright (C) 2026 Johannes1979I
/*
 GP1 FlipCap V4.2 - mono-motore / mono-braccio
 Sky-Watcher Quattro 300P f/4 - ota_d di default 362 mm (VERIFICARE il tubo reale)

 =====================================================================
 COSA CAMBIA RISPETTO ALLA V4.1  (dettagli in CHANGELOG_V4.2.md)
 ---------------------------------------------------------------------
 1. La piastra di supporto motore NON e' piu' dentro housing(): in V4.1
    era un solido staccato, sospeso a 12,45 mm da qualunque parete.
    Ora e' un pezzo a se': motor_bracket(), che si aggancia al soffitto
    della cavita' e si autoallinea contro parete sinistra + boss coperchio.
 2. mono_arm() completamente ridisegnato: in V4.1 compenetrava l'housing
    su TUTTA la corsa (mozzo dentro il boss del 626ZZ, nervature dentro
    la parete sinistra, flangia dentro lo spigolo della scatola).
 3. open_angle da -105 a -90 gradi: a -105 il disco del tappo passava a
    0,65 mm dallo spigolo anteriore della scatola. A -90 la luce e' ~14 mm.
 4. Piano tappo portato da Z=+12 a Z=+17 (arm_dz): serve spazio sotto la
    piastra del braccio per una struttura rigida che scavalchi l'anello
    frontale dell'OTA.
 5. Attacco tappo da 2 viti M4 a 20 mm di interasse a 4 viti M4 su un
    quadrilatero di 61 x 33 mm.
 6. hall_holder() -> hall_plate(): piastra unica con i due A3144 gia'
    posizionati a 0 e 90 gradi. In V4.1 la faccia sensibile del sensore
    era ortogonale all'asse del magnete (accoppiamento sbagliato) e il
    supporto compenetrava la bandierina.
 7. Mozzo braccio a morsetto (pinch clamp) invece del solo grano.
 =====================================================================

 Sistema di riferimento (invariato rispetto a V4/V4.1):
   X = sinistra/destra sull'OTA
   Y = verticale in vista frontale
   Z = asse ottico; l'OTA si estende verso Z negativo
   Asse albero di uscita / cerniera = X
*/

use <MCAD/involute_gears.scad>
$fn=72;

// ================= SELETTORE PEZZO =================
part="assembly";
// assembly | housing | cover | motor_bracket | motor_pinion | compound_gear |
// output_gear | mono_arm | lid_backplate | hall_plate | magnet_flag

// ================= PARAMETRI UTENTE =================
ota_d=362;              // MISURARE il tubo reale: circonferenza / pi
ota_clearance=1.2;
lid_d=374;
lid_thickness=3;        // spessore del disco del tappo.
                        // Determina la quota delle piazzole del braccio:
                        // se lo cambi, RIGENERA mono_arm.stl prima di stampare.
lid_angle=0;            // 0 = chiuso, open_angle = aperto
show_ota=true;          // false = nascondi il tubo nei render
show_lid=true;
show_cover=true;          // false = nascondi il disco del tappo nei render
open_angle=-90;         // V4.1 era -105: il tappo sbatteva sulla scatola

// Geometria cerniera (VINCOLATA dall'housing gia' stampato: non toccare)
hinge_y=212;
hinge_z=-25;

// Braccio
arm_x=70;               // V4.1 era 76 -> mozzo dentro il boss del cuscinetto
arm_dz=42;              // quota piano medio tappo rispetto all'asse cerniera
arm_w=16;               // larghezza colonna braccio in X (= lunghezza mozzo:
                        // tiene 2 mm di luce dal boss del 626ZZ a X=80)
plate_h=10;             // spessore struttura piastra tappo
lid_closed_z=hinge_z+arm_dz;   // = +17

// Treno ingranaggi V4.1 (INVARIATO: i pezzi stampati restano buoni)
gear_module=0.8;
pressure_angle=20;
backlash=0.22;
gear_t=6;
motor_teeth=14;
compound_big_teeth=42;
compound_small_teeth=14;
final_teeth=70;

stage1_center=(motor_teeth+compound_big_teeth)*gear_module/2; // 22.4
stage2_center=(compound_small_teeth+final_teeth)*gear_module/2; // 33.6
compound_y=hinge_y+stage2_center;   // 245.6
motor_y=compound_y+stage1_center;   // 268.0

// Posizioni assiali del treno (invariate)
final_x=5;
compound_small_x=5;
compound_big_x=21;
motor_pinion_x=21;

// Scatola (INVARIATA: housing gia' stampato)
box_x=120;
box_depth_x=72;
box_height_y=136;
box_width_z=74;
box_center_y=(hinge_y+motor_y)/2+2;   // 242
box_center_z=hinge_z;
wall=4;
corner_r=6;
cover_t=3.2;

// Facce utili della cavita' (derivate)
cav_left_x = box_x-box_depth_x/2+wall;          // 88
cav_top_y  = box_center_y+box_height_y/2-wall;  // 306

// Alberi / cuscinetti
output_shaft_d=6;
output_bearing_od=19.2;
output_bearing_w=6;
intermediate_shaft_d=5.3;
compound_bearing_od=16.2;
motor_shaft_d=5.05;

// Sella di fissaggio
saddle_z0=-122;
saddle_z1=-64;
saddle_thickness=9;
strap_slot_w=28;
strap_slot_h=6;

// Sistema Hall
magnet_d=6.2;
magnet_depth=3.2;
magnet_r=14;
flag_x=box_x-21;        // = 99, posizione bandierina sull'albero
hall_plate_t=3;         // spessore piastra sensori
hall_standoff=2.6;      // distacco dalla parete: scavalca il boss del 626ZZ
                        // che sporge in cavita' fino a X=90
hall_seat_h=hall_standoff+hall_plate_t;  // 5.6 -> faccia sensore a X=93.6
hall_r_in=6;
hall_r_out=31;
hall_screw_r=28;
hall_screw_a=[-18,108]; // angoli viti (0 = CLOSED, 90 = OPEN)

// Staffa motore
mb_face_x=140;          // faccia di appoggio orecchie 28BYJ
mb_plate_t=6;
mb_flange_t=6;
mb_screw_x=[100,132];   // viti M3 dall'esterno attraverso il tetto
mb_screw_z=-25;

// ================= HELPER =================
function pitch_r(t)=t*gear_module/2;
function outside_r(t)=pitch_r(t)+gear_module;

module x_cyl(r,h,center=true){ rotate([0,90,0]) cylinder(r=r,h=h,center=center); }

module rounded_box_x(depth, sy, sz, r){
    hull(){
        for(y=[-sy/2+r, sy/2-r])
            for(z=[-sz/2+r, sz/2-r])
                translate([0,y,z]) x_cyl(r,depth,true);
    }
}

module gear_x(teeth,bore,th=gear_t,hub_d=16,hub_t=gear_t){
    rotate([0,90,0])
        gear(number_of_teeth=teeth,
             circular_pitch=180*gear_module,
             pressure_angle=pressure_angle,
             clearance=0.18,
             gear_thickness=th,
             rim_thickness=th,
             rim_width=3,
             hub_thickness=hub_t,
             hub_diameter=hub_d,
             bore_diameter=bore,
             backlash=backlash,
             involute_facets=8);
}

function arcpts(r,a0,a1,n)=[for(i=[0:n]) let(a=a0+(a1-a0)*i/n) [r*sin(a), r*cos(a)]];

// ================= SELLA OTA =================
module saddle_shell_raw(){
    inner_r=ota_d/2+ota_clearance;
    outer_r=inner_r+saddle_thickness;
    intersection(){
        difference(){
            translate([0,0,saddle_z0]) cylinder(r=outer_r,h=saddle_z1-saddle_z0);
            translate([0,0,saddle_z0-1]) cylinder(r=inner_r,h=saddle_z1-saddle_z0+2);
        }
        translate([40,102,saddle_z0-2])
            cube([110,88,saddle_z1-saddle_z0+4]);
    }
}

module strap_ears_raw(){
    for(zp=[-108,-78]){
        for(s=[-1,1]){
            translate([(s<0)?52:138,(s<0)?170:124,zp])
                hull(){
                    cube([20,16,10],center=true);
                    translate([(s<0)?10:-10,8,0]) cube([12,12,10],center=true);
                }
        }
    }
}

module strap_slots_cut(){
    for(zp=[-108,-78])
        for(s=[-1,1])
            translate([(s<0)?52:138,(s<0)?172:126,zp])
                cube([strap_slot_h,strap_slot_w,14],center=true);
}

// ================= HOUSING =================
module housing_outer_shell(){
    translate([box_x,box_center_y,box_center_z])
    difference(){
        rounded_box_x(box_depth_x,box_height_y,box_width_z,corner_r);
        translate([4,0,0]) rounded_box_x(box_depth_x,box_height_y-2*wall,box_width_z-2*wall,corner_r-2);
    }
}

module cover_bosses_raw(){
    for(yv=[box_center_y-box_height_y/2+6, box_center_y+box_height_y/2-6])
        for(zv=[box_center_z-box_width_z/2+6, box_center_z+box_width_z/2-6])
            translate([box_x,yv,zv]) x_cyl(5.5,66,true);
}

module output_bearing_boss_raw(){
    left_face=box_x-box_depth_x/2;
    translate([left_face+1,hinge_y,hinge_z]) x_cyl(13,10,true);
}

module rear_bridge_raw(){
    hull(){
        translate([box_x,190,box_center_z-box_width_z/2+2]) cube([58,25,7],center=true);
        translate([105,150,saddle_z1+2]) cube([82,20,8],center=true);
    }
}

module body_raw(){
    union(){
        housing_outer_shell();
        cover_bosses_raw();
        output_bearing_boss_raw();
        saddle_shell_raw();
        strap_ears_raw();
        rear_bridge_raw();
    }
    // NB: motor_mount_plate_raw() RIMOSSA -> vedi motor_bracket()
}

module body_cuts(){
    // luce OTA attraverso sella e fondo scatola
    translate([0,0,-150]) cylinder(r=ota_d/2+ota_clearance,h=260);

    strap_slots_cut();

    // sede 626ZZ sinistra, inserita dall'esterno, con spallamento interno
    left_face=box_x-box_depth_x/2;
    translate([left_face-1,hinge_y,hinge_z]) x_cyl(output_bearing_od/2,6.4,true);
    translate([left_face+3,hinge_y,hinge_z]) x_cyl((output_shaft_d+0.35)/2,18,true);

    // albero intermedio M5
    translate([box_x,compound_y,hinge_z]) x_cyl(intermediate_shaft_d/2,80,true);

    // viti coperchio
    for(yv=[box_center_y-box_height_y/2+6, box_center_y+box_height_y/2-6])
        for(zv=[box_center_z-box_width_z/2+6, box_center_z+box_width_z/2-6])
            translate([box_x+31,yv,zv]) x_cyl(2.15,16,true);

    // V4.2: 2 fori M3 nel tetto per la staffa motore
    for(xv=mb_screw_x)
        translate([xv,box_center_y+box_height_y/2+1,mb_screw_z])
            rotate([90,0,0]) cylinder(d=3.4,h=12);

    // V4.2: 2 fori M3 nella parete sinistra per la piastra sensori
    for(a=hall_screw_a)
        translate([box_x-34, hinge_y+hall_screw_r*sin(a), hinge_z+hall_screw_r*cos(a)])
            x_cyl(1.7,9,true);
}

module housing(){ difference(){ body_raw(); body_cuts(); } }

module cover(){
    cover_x=box_x+box_depth_x/2+cover_t/2;
    right_face=box_x+box_depth_x/2+cover_t;
    difference(){
        union(){
            translate([cover_x,box_center_y,box_center_z])
                rounded_box_x(cover_t,box_height_y,box_width_z,corner_r);
            translate([box_x+box_depth_x/2,hinge_y,hinge_z]) x_cyl(13,10,true);
        }
        translate([right_face-0.7,hinge_y,hinge_z]) x_cyl(output_bearing_od/2,6.4,true);
        translate([box_x+box_depth_x/2-2,hinge_y,hinge_z]) x_cyl((output_shaft_d+0.35)/2,18,true);
        translate([cover_x,compound_y,hinge_z]) x_cyl(intermediate_shaft_d/2,cover_t+5,true);
        for(yv=[box_center_y-box_height_y/2+6, box_center_y+box_height_y/2-6])
            for(zv=[box_center_z-box_width_z/2+6, box_center_z+box_width_z/2-6])
                translate([cover_x,yv,zv]) x_cyl(1.75,cover_t+6,true);
    }
}

// ================= STAFFA MOTORE (NUOVA V4.2) =================
// Frame locale: origine = (mb_face_x, motor_y, hinge_z) in globale.
//   x locale -> X globale   (0 = faccia di appoggio orecchie motore)
//   y locale -> Y globale - motor_y
//   z locale -> Z globale - hinge_z
// Si autoallinea: faccia superiore contro il soffitto della cavita',
// fianco sinistro della flangia contro la parete sinistra, larghezza
// flangia incastrata fra i due boss superiori del coperchio.
mb_fit=0.4;             // gioco di montaggio contro soffitto e parete
mb_slot=2.0;            // semi-asola di registrazione interasse motore

module motor_bracket(){
    py0 = 232-motor_y;                      // -36  bordo inferiore piastra
    py1 = cav_top_y-motor_y-mb_fit;         // +37.6 (0,4 mm di gioco dal soffitto)
    fy0 = py1-mb_flange_t;
    fx0 = cav_left_x-mb_face_x+mb_fit;      // -51.6 (0,4 mm dalla parete sinistra)
    fx1 = 6;
    pz0 = -47-hinge_z;                      // -22
    pz1 = 0-hinge_z;                        // +25
    fz0 = -49-hinge_z;                      // -24
    fz1 = -1-hinge_z;                       // +24

    difference(){
        union(){
            // piastra motore (piano YZ)
            translate([-mb_plate_t,py0,pz0]) cube([mb_plate_t,py1-py0,pz1-pz0]);
            // flangia superiore contro il soffitto
            translate([fx0,fy0,fz0]) cube([fx1-fx0,mb_flange_t,fz1-fz0]);
            // fazzoletti di irrigidimento
            for(zv=[fz0+2.5, fz1-4.5])
                hull(){
                    translate([-3,fy0-1,zv+1.5]) cube([6,3,3],center=true);
                    translate([-27,fy0-1,zv+1.5]) cube([6,3,3],center=true);
                    translate([-3,py0+22,zv+1.5]) cube([6,3,3],center=true);
                }
        }
        // passaggio corpo 28BYJ-48 (Ø28) - asolato in Y per registrare l'interasse
        hull() for(yv=[-mb_slot,mb_slot])
            translate([-mb_plate_t-1,yv,0]) x_cyl(14.4,mb_plate_t+2,false);
        // fori viti motore M3, interasse 35 mm, asolati in Y come il corpo
        for(zv=[-17.5,17.5])
            hull() for(yv=[-mb_slot,mb_slot])
                translate([-mb_plate_t-1,yv,zv]) x_cyl(1.75,mb_plate_t+2,false);
        // luce per il mozzo centrale Ø8 dell'ingranaggio composto
        translate([-mb_plate_t-1,compound_y-motor_y,0]) x_cyl(5.0,mb_plate_t+2,false);
        // sedi inserti M3 nella flangia (dal soffitto verso il basso)
        for(xv=mb_screw_x)
            translate([xv-mb_face_x,py1+1,mb_screw_z-hinge_z])
                rotate([90,0,0]) cylinder(d=4.0,h=6);
    }
}

module motor_bracket_placed(){
    translate([mb_face_x,motor_y,hinge_z]) motor_bracket();
}

// ================= INGRANAGGI (invariati dalla V4.1) =================
module output_gear(){
    difference(){
        gear_x(final_teeth,output_shaft_d+0.2,gear_t,22,10);
        cylinder(d=2.7,h=30,center=true);
    }
}

module compound_gear(){
    difference(){
        union(){
            translate([-8,0,0]) gear_x(compound_small_teeth,0,gear_t,8.0,gear_t);
            translate([8,0,0]) gear_x(compound_big_teeth,0,gear_t,20,gear_t);
            x_cyl(4.0,22,true);
        }
        x_cyl(intermediate_shaft_d/2,24,true);
        translate([11.5,0,0]) x_cyl(compound_bearing_od/2,5.2,true);
    }
}

module motor_pinion(){
    gear_x(motor_teeth,motor_shaft_d,gear_t,8.2,7);
}

// ================= BANDIERINA MAGNETE =================
module magnet_flag(){
    difference(){
        union(){
            x_cyl(11,5,true);
            translate([0,0,magnet_r]) x_cyl(5,5,true);
        }
        x_cyl((output_shaft_d+0.2)/2,8,true);
        // tasca magnete aperta sulla faccia -X (verso i sensori)
        translate([-2.5,0,magnet_r]) x_cyl(magnet_d/2,magnet_depth,false);
        // grano M3: accorciato, in V4.1 sfondava nella tasca del magnete
        cylinder(d=2.7,h=20,center=true);
    }
}

// ================= PIASTRA SENSORI HALL (NUOVA V4.2) =================
// Disegnata piatta nel piano XY (orientamento di stampa).
//   x locale -> delta Y globale
//   y locale -> delta Z globale
//   z locale -> distanza dalla faccia interna della parete sinistra
// In assieme: rotate([90,0,90]) + translate([cav_left_x,hinge_y,hinge_z])
// Tasca A3144 ricavata nello spessore della piastra: la faccia sensibile
// risulta ortogonale all'asse X globale, cioe' affacciata al polo del
// magnete. Nella V4.1 era ruotata di 90 gradi e leggeva la componente
// sbagliata del campo.
module hall_pocket(){
    translate([0,0,hall_seat_h-1.1]) cube([4.7,3.7,2.3],center=true);       // corpo
    translate([0,-4.2,hall_seat_h-1.1]) cube([3.2,6,2.3],center=true);      // reofori
}

module hall_plate(){
    difference(){
        union(){
            // corpo della piastra, staccato dalla parete di hall_standoff
            translate([0,0,hall_standoff])
                linear_extrude(hall_plate_t)
                    polygon(concat(arcpts(hall_r_out,-25,115,28),
                                   arcpts(hall_r_in,115,-25,28)));
            // colonnine di appoggio alla parete, in corrispondenza delle viti
            for(ac=hall_screw_a)
                translate([hall_screw_r*sin(ac),hall_screw_r*cos(ac),0])
                    cylinder(d=11,h=hall_seat_h);
        }
        // sedi sensori: CLOSED a 0 gradi, OPEN a -open_angle
        for(a=[0,-open_angle])
            translate([magnet_r*sin(a),magnet_r*cos(a),0]) rotate([0,0,-a]) hall_pocket();
        // passaggio albero
        translate([0,0,-1]) cylinder(d=9,h=hall_seat_h+4);
        // asole ad arco: registrano l'istante di scatto di +/- 7 gradi
        for(ac=hall_screw_a)
            for(i=[0:12]) let(a=ac-7+14*i/12)
                translate([hall_screw_r*sin(a),hall_screw_r*cos(a),-1])
                    cylinder(d=3.4,h=hall_seat_h+2);
    }
}

module hall_plate_placed(){
    translate([cav_left_x,hinge_y,hinge_z]) rotate([90,0,90]) hall_plate();
}

// ================= MONOBRACCIO (RIDISEGNATO V4.2) =================
// Frame locale: origine sull'asse dell'albero di uscita.
//   x locale -> X globale - arm_x
//   z locale -> verso il cielo (normale al tappo)
// VINCOLO: nessun punto con x locale > 12 sotto z locale 28,
// altrimenti si entra nel volume della scatola durante la corsa.
foot_ang=atan2(arm_x,hinge_y);   // 18.28 gradi
function bolt_local(r,a)=[r*sin(a)-arm_x, r*cos(a)-hinge_y];
lid_bolts=[ bolt_local(176,foot_ang-10.5),
            bolt_local(176,foot_ang+10.5),
            bolt_local(158,foot_ang-8),
            bolt_local(158,foot_ang+8) ];
pad_top=arm_dz-lid_thickness/2;

module lid_pad(p,d=22){
    translate([p[0],p[1],pad_top-plate_h/2]) cylinder(d=d,h=plate_h,center=true);
}

module lid_plate_body(){
    hull(){ for(p=lid_bolts) lid_pad(p); }
}

module mono_arm(){
    difference(){
        union(){
            // mozzo a morsetto
            x_cyl(13,16,true);
            translate([0,9,0]) cube([16,12,26],center=true);
            // colonna: sale restando a Y~cerniera, cioe' sempre fuori dal tubo
            hull(){
                translate([0,-1,4]) cube([arm_w,24,12],center=true);
                translate([0,-6,pad_top-plate_h+3]) cube([arm_w,20,6],center=true);
            }
            // raccordo colonna -> lato sinistro della piastra
            hull(){
                translate([0,-6,pad_top-plate_h+3]) cube([arm_w,18,6],center=true);
                lid_pad(lid_bolts[0]);
                lid_pad(lid_bolts[2]);
            }
            lid_plate_body();
        }
        // foro albero
        x_cyl((output_shaft_d+0.2)/2,20,true);
        // taglio del morsetto
        translate([0,9,0]) cube([20,16,1.8],center=true);
        // vite morsetto M3 + sede testa + sede dado
        translate([0,9,0]) cylinder(d=3.3,h=34,center=true);
        translate([0,9,4]) cylinder(d=6.4,h=12);
        translate([0,9,-13.01]) cylinder(d=7.0,h=3.5,$fn=6);
        // fori tappo M4 + sedi dadi sotto le piazzole
        for(p=lid_bolts){
            translate([p[0],p[1],pad_top-plate_h-1]) cylinder(d=4.4,h=plate_h+4);
            translate([p[0],p[1],pad_top-plate_h-0.01]) cylinder(d=7.3/cos(30),h=3.6,$fn=6);
        }
    }
}

module lid_backplate(){
    difference(){
        linear_extrude(3) hull(){ for(p=lid_bolts) translate(p) circle(d=22); }
        for(p=lid_bolts) translate([p[0],p[1],-1]) cylinder(d=4.4,h=6);
    }
}

// ================= DUMMY DI ASSIEME =================
module ota_dummy(){
    color([0.12,0.12,0.15,0.30]) translate([0,0,-150]) cylinder(d=ota_d,h=150);
    color([0.08,0.08,0.1,0.45]) translate([0,0,-5]) difference(){
        cylinder(d=ota_d+8,h=8);
        translate([0,0,-1]) cylinder(d=ota_d-8,h=10);
    }
}

module lid_dummy(angle=0){
    color([0.08,0.28,0.08,0.50])
        translate([0,hinge_y,hinge_z])
        rotate([angle,0,0])
        translate([0,-hinge_y,arm_dz])
        cylinder(d=lid_d,h=lid_thickness,center=true);
}

module motor_dummy(){
    color([0.35,0.35,0.38,0.8]){
        // corpo Ø28 x 19, orecchie appoggiate alla faccia mb_face_x
        translate([mb_face_x-9.5,motor_y,hinge_z]) x_cyl(14,19,true);
        translate([mb_face_x+0.4,motor_y,hinge_z]) cube([0.8,43,9],center=true);
    }
}

module geartrain(){
    color([0.95,0.52,0.08,0.95]){
        translate([box_x+final_x,hinge_y,hinge_z]) output_gear();
        translate([box_x+(compound_small_x+compound_big_x)/2,compound_y,hinge_z]) compound_gear();
        translate([box_x+motor_pinion_x,motor_y,hinge_z]) motor_pinion();
    }
}

module arm_assembly(angle=0){
    color([0.80,0.12,0.10,0.95])
        translate([arm_x,hinge_y,hinge_z]) rotate([angle,0,0]) mono_arm();
}

module backplate_assembly(angle=0){
    color([0.55,0.10,0.08,0.95])
        translate([arm_x,hinge_y,hinge_z]) rotate([angle,0,0])
        translate([0,0,arm_dz+lid_thickness/2]) lid_backplate();
}

module shaft_dummy(){
    // V4.2: da X=61 a X=162 -> albero 6 x 100 mm (la BOM V4.1 diceva 95)
    color([0.72,0.72,0.76]) translate([61,hinge_y,hinge_z]) x_cyl(output_shaft_d/2,101,false);
}

module magnet_flag_assembly(angle=0){
    color([0.95,0.75,0.10,0.9])
        translate([flag_x,hinge_y,hinge_z]) rotate([angle,0,0]) magnet_flag();
}

module assembly(){
    if(show_ota) ota_dummy();
    if(show_lid) lid_dummy(lid_angle);
    if(show_housing) color([0.08,0.26,0.45,0.88]) housing();
    if(show_cover) color([0.10,0.32,0.55,0.35]) cover();
    if(show_bracket) color([0.20,0.55,0.30,0.95]) motor_bracket_placed();
    if(show_gears) geartrain();
    if(show_motor) motor_dummy();
    if(show_shaft) shaft_dummy();
    if(show_arm) arm_assembly(lid_angle);
    if(show_backplate) backplate_assembly(lid_angle);
    if(show_hall) color([0.85,0.85,0.90,0.95]) hall_plate_placed();
    if(show_flag) magnet_flag_assembly(lid_angle);
}

// ================= OUTPUT =================
if(part=="assembly") assembly();
else if(part=="housing") housing();
else if(part=="cover") cover();
else if(part=="motor_bracket") motor_bracket();
else if(part=="motor_pinion") motor_pinion();
else if(part=="compound_gear") compound_gear();
else if(part=="output_gear") output_gear();
else if(part=="mono_arm") mono_arm();
else if(part=="lid_backplate") lid_backplate();
else if(part=="hall_plate") hall_plate();
else if(part=="magnet_flag") magnet_flag();
