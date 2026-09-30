// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright (C) 2026 Johannes1979I
/*
 =============================================================================
  GP1 FlipCap V6
  Tappo motorizzato per telescopi newtoniani, comandato da INDI / Ekos.
  Un motore, un braccio, ribaltamento di 270 gradi: da aperto il tappo si
  appoggia sul tubo. Riduttore ed elettronica nella stessa scatola.
 =============================================================================

  COME SI USA
  - Apri il file in OpenSCAD e premi F5: compare l'assieme completo.
    La prima anteprima impiega qualche decina di secondi perche' i pezzi
    complessi vengono calcolati per intero (render()); poi restano in cache.
  - cap_angle muove il tappo: 0 = chiuso, -270 = parcheggiato sul tubo.
  - Gli interruttori show_* accendono e spengono i singoli pezzi.
  - logo=false toglie il logo dell'Osservatorio Jupiter inciso sulla scatola.
  - Per esportare un pezzo: imposta part (elenco sotto), premi F6 e poi
    File > Export > STL. Il pezzo esce gia' orientato per la stampa.
  - Da riga di comando:
        openscad -o stl/housing.stl -D 'part="housing"' gp1_flipcap_V6.scad

  SISTEMA DI RIFERIMENTO
    Z = asse ottico. Il tubo si estende verso Z negativo, la bocca e' a Z=0.
    Y = verso l'alto nel piano della bocca, dal lato in cui sta la scatola.
    X = di lato; la scatola sta a X positivo, il braccio fra tubo e scatola.
    L'albero di uscita, cioe' la cerniera del tappo, e' parallelo a X.

  LIBRERIE
    Serve MCAD (involute_gears.scad), inclusa nell'installazione di OpenSCAD.
    MCAD stampa in console alcuni avvisi "DEPRECATED" su assign() e child():
    vengono dalla libreria, non da questo file, e non hanno effetto.
*/

use <MCAD/involute_gears.scad>
$fn=72;

// =============================================================================
//  COSA MOSTRARE O ESPORTARE
// =============================================================================
part="assembly";
// assembly
// housing | cover | motor_bracket | hall_plate | spacers |
// bay_lid | bay_tray |
// output_gear | compound_gear | motor_pinion | magnet_flag |
// mono_arm | cap_backplate | cap_rest
// test_shaft | test_pin      (facoltativi: assi di prova in plastica, solo orient="print")

orient="print";   // print  = orientato per la stampa (e' quello che sta in stl/)
                  // placed = nella posizione di montaggio (per le verifiche)

cap_angle=0;      // 0 = chiuso, open_angle = parcheggiato

show_ota=true;      show_cap=true;      show_housing=true;   show_cover=true;
show_bay_lid=true;  show_bay_tray=true; show_boards=true;    show_bracket=true;
show_motor=true;    show_gears=true;    show_shaft=true;     show_spacers=true;
show_hall=true;     show_flag=true;     show_arm=true;       show_backplate=true;
show_rests=true;

// =============================================================================
//  TUBO E TAPPO
// =============================================================================
ota_d=362;            // diametro ESTERNO del tubo: circonferenza / pi greco
ota_clearance=1.2;    // gioco fra selle e tubo (lo riempie l'EVA)
cap_d=374;            // diametro del disco del tappo: ~12 mm piu' del tubo
cap_thickness=3;      // spessore del disco. Decide la quota delle piazzole
                      // del braccio: se lo cambi rigenera mono_arm e cap_rest
open_angle=-270;      // corsa del tappo

// =============================================================================
//  CERNIERA E BRACCIO
// =============================================================================
hinge_y=264;          // quota dell'albero di uscita dall'asse ottico. Da
                      // parcheggiato il piano del tappo sta a hinge_y-arm_dz
                      // = 222 mm, sopra la scatola dell'elettronica (213)
hinge_z=-25;          // l'albero sta 25 mm dietro la bocca del tubo
arm_x=68;             // posizione del mozzo del braccio sull'albero
arm_dz=42;            // piano medio del tappo rispetto all'albero (chiuso: Z=+17)
arm_w=16;             // larghezza della colonna del braccio
plate_h=10;           // spessore della piastra che regge il tappo
rest_z=[-215,-380];   // dove vanno gli appoggi del tappo, lungo il tubo. Il primo
                      // sta dietro la cinghia posteriore e fuori dalla contropiastra
rest_pad=2;           // EVA incollata sopra ogni appoggio

// =============================================================================
//  RIDUTTORE: 28BYJ-48 + treno stampato 14/42 x 14/70 = 15:1, modulo 0,8
// =============================================================================
gear_module=0.8;
pressure_angle=20;
backlash=0.22;
gear_t=6;
motor_teeth=14;
compound_big_teeth=42;
compound_small_teeth=14;
final_teeth=70;

stage1_center=(motor_teeth+compound_big_teeth)*gear_module/2;     // 22,4
stage2_center=(compound_small_teeth+final_teeth)*gear_module/2;   // 33,6

// Direzioni nel piano YZ, in gradi da "verso il basso" (-Y) ruotando verso
// la bocca del tubo (+Z). Scelte con una ricerca numerica per dare al 28BYJ
// reale (albero eccentrico) almeno 3,5 mm di luce da pareti e ingranaggi.
compound_angle=15;    // asse del composto visto dall'asse di uscita
motor_angle=-13;      // albero motore visto dall'asse del composto
function yz_dir(a)=[-cos(a),sin(a)];

hinge_yz=[hinge_y,hinge_z];
compound_yz=hinge_yz+stage2_center*yz_dir(compound_angle);
motor_yz=compound_yz+stage1_center*yz_dir(motor_angle);

final_x=5;            // posizioni lungo X delle ruote rispetto a box_x
compound_small_x=5;
compound_big_x=21;
motor_pinion_x=21;

// =============================================================================
//  MOTORE 28BYJ-48
//  L'albero NON e' al centro della carcassa: e' spostato di 8 mm, dalla parte
//  opposta al cappuccio azzurro da cui escono i fili. Le due orecchie stanno
//  sulla retta per il centro della carcassa, perpendicolare a quello spostamento.
// =============================================================================
byj_offset=8;
byj_can_d=28;
byj_can_h=19;
byj_hole_span=35;     // interasse dei fori delle orecchie
byj_ear_w=7;
byj_ear_t=1;
byj_can_angle=-56;    // direzione albero -> centro carcassa (verso il basso e il retro)
byj_face_x=139.3;     // faccia delle orecchie dal lato albero. Il collarino
                      // (1,5 mm) arriva a 140,8, il pignone parte da 141

can_yz=motor_yz+byj_offset*yz_dir(byj_can_angle);
byj_w=yz_dir(byj_can_angle);                 // verso il cappuccio dei fili
byj_u=[byj_w[1],-byj_w[0]];                  // direzione delle orecchie
byj_ears=[can_yz+byj_hole_span/2*byj_u, can_yz-byj_hole_span/2*byj_u];

// =============================================================================
//  SCATOLA DEL RIDUTTORE (estremi esterni)
// =============================================================================
box_x0=84;  box_x1=156;     // parete sinistra .. lato aperto (coperchio)
box_y0=177; box_y1=300;
box_z0=-60; box_z1=10;
wall=4;
corner_r=12;
cover_t=3.2;
box_x=(box_x0+box_x1)/2;    // 120, riferimento per le posizioni delle ruote

cav_x0=box_x0+wall;         // 88
cav_y0=box_y0+wall; cav_y1=box_y1-wall;
cav_z0=box_z0+wall; cav_z1=box_z1-wall;

// =============================================================================
//  ALBERI, CUSCINETTI, DISTANZIALI
//  I due 626ZZ entrano dall'INTERNO e battono su un labbro esterno. I
//  distanziali stampati li caricano verso l'esterno: l'albero resta
//  bloccato in entrambi i versi senza anelli elastici.
// =============================================================================
output_shaft_d=6;
shaft_len=100;              // albero 6 x 100 mm
bearing_od=19.2;            // 626ZZ, 19 mm nominali
bearing_w=6;
bearing_lip=2.5;            // labbro che trattiene il cuscinetto
bearing_lip_hole=13;        // tocca solo l'anello esterno
left_seat_x0=box_x0+bearing_lip;                 // 86,5
left_seat_x1=left_seat_x0+bearing_w+0.2;         // 92,7
cover_seat_x1=box_x1+cover_t-bearing_lip-2.5;    // 154,2
cover_seat_x0=cover_seat_x1-bearing_w-0.2;       // 148

intermediate_shaft_d=5.3;   // perno M5
compound_bearing_od=16.2;   // 625ZZ
motor_shaft_d=5.1;          // foro scorrevole: il pignone lo tiene il grano
ptfe_washer_t=1.0;          // rondella PTFE o nylon M5 fra distanziale e composto

spacer_od=8.5;              // distanziali sull'albero da 6
cspacer_od=8;               // distanziali sul perno M5

// =============================================================================
//  SENSORI HALL
// =============================================================================
magnet_d=6.2;               // magnete 6 x 3
magnet_depth=3.2;
magnet_r=14;                // raggio a cui gira il magnete
flag_x=101.2;               // centro della bandierina sull'albero
hall_plate_t=3;
hall_standoff=5.2;          // la piastra scavalca il boss del cuscinetto (92,7)
hall_seat_h=hall_standoff+hall_plate_t;
hall_r_in=6;
hall_r_out=27;
hall_hole_d=10.5;           // ci passa il distanziale dell'albero
hall_a0=-25;                // la piastra copre l'arco percorso dal magnete
hall_a1=295;
hall_screw_r=25;
hall_screw_a=[-18,108];     // viti; sensori a 0 (CLOSED) e 270 (OPEN)
// Cablaggio incassato: da ogni sede parte un canale che arriva fino al bordo
// della piastra, con accanto l'incavo del condensatore da 100 nF. Saldature,
// condensatore e fili stanno sotto il piano della piastra, dove la bandierina
// passa sopra senza toccarli, e i fili escono di lato dal bordo.
// Per avere la profondita' la corona esterna (oltre il boss del cuscinetto)
// scende verso la parete fino a hall_pad_z: la faccia dei sensori non si muove.
// I canali sono girati di 25 gradi per stare lontani dal dado della vite a -18
// (CLOSED) e dal perno M5 del composto (OPEN).
hall_leg_turn=[25,-25];     // direzione del canale rispetto al raggio: CLOSED, OPEN
hall_cap_side=[1,-1];       // lato dell'incavo del condensatore (+x o -x della sede)
hall_chan_w=3.6;            // tratto dei piedini: tre piedini a passo 1,27
hall_leg_depth=3.0;
hall_wire_u0=4.5;           // dal centro del sensore: qui il canale si allarga per i fili
hall_wire_w=6;
hall_wire_depth=3.8;
hall_cap_u=[3.5,10];        // incavo del condensatore: lungo il canale ...
hall_cap_v=[1.5,8.5];       // ... e di lato, dall'asse del canale
hall_pad_r=13.2;            // corona ingrossata: fuori dal boss del 626ZZ (12,5)
hall_pad_z=2.2;             // quanto scende verso la parete (luce che resta)

// =============================================================================
//  STAFFA MOTORE (avvitata al fondo della scatola, da sotto)
// =============================================================================
mb_plate_t=6;
mb_plate_x1=byj_face_x-byj_ear_t;           // 138,3: ci appoggiano le orecchie
mb_plate_x0=mb_plate_x1-mb_plate_t;         // 132,3
mb_ring_r=21;
mb_can_hole_r=15;                           // 1 mm di gioco per registrare
mb_foot_z=[-47,-9];
mb_foot_x1=152;
mb_foot_t=5;
mb_block_x0=143;                            // blocco piu' alto per gli inserti
mb_block_t=8;
mb_screws=[[147.5,-40],[147.5,-16]];        // X,Z: viti M3 dal fondo

// =============================================================================
//  SELLE E CINGHIE
//  Due selle corte, una davanti e una dietro al vano elettronica. Ogni
//  cinghia da 25 mm passa sopra la sua sella, fra due costole.
// =============================================================================
saddle_x0=box_x0;           // niente sotto la parete sinistra: si stampa in piano
saddle_x1=150;
saddle_thickness=9;
front_saddle_z=[-63,-30];   // la cinghia passa fra Z -60 e -33
rear_saddle_z=[-195,-161];  // la cinghia passa fra Z -191 e -164
strap_lip=4;

// =============================================================================
//  VANO ELETTRONICA (aperto verso +X, chiuso da bay_lid)
// =============================================================================
bay_x0=box_x0; bay_x1=box_x1;
bay_y0=165;  bay_y1=213;    // 7,5 mm sotto il tappo parcheggiato
bay_z0=-164; bay_z1=box_z0;
bay_wall=3;
bay_lid_t=3;
bay_boss_d=8;
bay_bosses=[[206.5,-157.5],[206.5,-66.5],[161.5,-157.5],[161.5,-66.5]];   // Y,Z: viti del coperchio
                            // (i bossoli entrano 0,5 mm nelle pareti: niente contatti tangenti)
tray_t=3;
tray_ledge_y=[tray_t+0.2,tray_t+3];          // sopra il vassoio, dal fondo del vano

// Schede. Interassi dei fori NOMINALI: misura le tue e correggi qui, poi
// rigenera solo bay_tray. Posizione = centro della scheda, in X e Z globali.
nano_size=[43.2,18.5];  nano_holes=[40.64,15.24]; nano_pos=[129.6,-142];
nano_standoff_h=10;     nano_pilot=1.3;           // viti autofilettanti da 1,7 mm (o M1,6)
buck_size=[43,21];      buck_holes=[30,16];       buck_pos=[131.5,-116.5];
uln_size=[35,32];       uln_holes=[30.5,26.5];    uln_pos=[110,-84];
board_standoff_h=4;     board_pilot=2.5;          // viti M3 autofilettanti

usb_hole=[-149,-135,173,191];   // Z0,Z1,Y0,Y1 sul coperchio del vano
jack_yz=[200,-116.5];           // presa DC 5,5 x 2,1 da pannello (foro 8 mm)
jack_d=8.2;
cable_slot=[92,130,190,202];    // X0,X1,Y0,Y1: passaggio cavi riduttore -> vano

// =============================================================================
//  LOGO DELL'OSSERVATORIO JUPITER
//  Inciso sulla faccia anteriore della scatola del riduttore (Z = box_z1), che
//  nessun pezzo copre in tutta la corsa: Giove con le bande e la Grande Macchia
//  Rossa, i quattro satelliti medicei scoperti da Galileo nel 1610 e il nome
//  dell'osservatorio. In stampa quella faccia e' una parete verticale: il
//  logo viene nitido, senza supporti. logo=false per la scatola liscia.
// =============================================================================
logo=true;
logo_depth=1.0;                             // profondita' dell'incisione
logo_font="Liberation Sans:style=Bold";     // inclusa in OpenSCAD: lo stesso STL su ogni PC
logo_top=268;                               // Y del bordo alto del disco di Giove
jup_r=17;                                   // raggio del disco di Giove

// =============================================================================
//  FUNZIONI DI SERVIZIO
// =============================================================================
module x_cyl(r,h,center=true){ rotate([0,90,0]) cylinder(r=r,h=h,center=center); }
module y_cyl(d,h){ rotate([-90,0,0]) cylinder(d=d,h=h); }        // da Y a Y+h
module at_yz(p,x=0){ translate([x,p[0],p[1]]) children(); }

// scatola con spigoli arrotondati attorno a X, dati gli estremi
module rbox_x(x0,x1,y0,y1,z0,z1,r){
    hull() for(y=[y0+r,y1-r]) for(z=[z0+r,z1-r])
        translate([x0,y,z]) rotate([0,90,0]) cylinder(r=r,h=x1-x0);
}

function arcpts(r,a0,a1,n)=[for(i=[0:n]) let(a=a0+(a1-a0)*i/n) [r*sin(a),r*cos(a)]];

module gear_x(teeth,bore,th=gear_t,hub_d=16,hub_t=gear_t){
    rotate([0,90,0])
        gear(number_of_teeth=teeth,
             circular_pitch=180*gear_module,
             pressure_angle=pressure_angle,
             clearance=0.18,
             gear_thickness=th, rim_thickness=th, rim_width=3,
             hub_thickness=hub_t, hub_diameter=hub_d,
             bore_diameter=bore, backlash=backlash, involute_facets=8);
}

// guscio cilindrico attorno al tubo, fra due X e due Z
module tube_shell(r0,r1,x0,x1,z0,z1){
    intersection(){
        difference(){
            translate([0,0,z0]) cylinder(r=r1,h=z1-z0,$fn=240);
            translate([0,0,z0-1]) cylinder(r=r0,h=z1-z0+2,$fn=240);
        }
        translate([x0,0,z0-1]) cube([x1-x0,r1+1,z1-z0+2]);
    }
}

// logo in 2D: x sulla faccia a partire da box_x, y = Y globale.
// Le parti disegnate sono quelle incise.
module jupiter_grs(r){ translate([0.30*r,-0.43*r]) scale([1,0.6]) circle(r=0.18*r); }

module jupiter_2d(r){
    difference(){ circle(r=r); circle(r=r-1.2); }                  // bordo del disco
    intersection(){
        circle(r=r-0.6);
        difference(){
            // bande scure, da sud a nord, in frazioni del raggio
            for(b=[[-0.62,-0.52],[-0.40,-0.14],[0.12,0.34],[0.46,0.54]])
                translate([-r,b[0]*r]) square([2*r,(b[1]-b[0])*r]);
            offset(r=1) jupiter_grs(r);                            // la baia della Macchia
        }
    }
    jupiter_grs(r);                                                // Grande Macchia Rossa
}

module logo_2d(){
    k=0.935;                                   // Giove e' schiacciato ai poli
    translate([0,logo_top-jup_r*k]){
        scale([1,k]) jupiter_2d(jup_r);
        // Io, Ganimede, Europa, Callisto allineati sull'equatore, come li disegnava Galileo
        for(m=[[-1.28,1.5],[-1.68,1.8],[1.25,1.35],[1.70,1.65]])
            translate([m[0]*jup_r,0]) circle(r=m[1]);
    }
    y0=logo_top-2*jup_r*k;                     // bordo basso del disco
    translate([0,y0-11])
        text("OSSERVATORIO",size=5.2,font=logo_font,halign="center",spacing=1.08);
    translate([0,y0-26.5])
        text("JUPITER",size=10,font=logo_font,halign="center",spacing=1.04);
}

// =============================================================================
//  HOUSING: riduttore + vano elettronica + selle, un unico pezzo.
//  Si stampa con la parete sinistra sul piatto: tutto il resto sale in
//  verticale e le due cavita' sono aperte verso l'alto.
// =============================================================================
ota_r=ota_d/2+ota_clearance;

function cover_screw_pts()=[for(y=[box_y0+6,box_y1-6]) for(z=[box_z0+6,box_z1-6]) [y,z]];

module gearbox_body(){
    difference(){
        rbox_x(box_x0,box_x1,box_y0,box_y1,box_z0,box_z1,corner_r);
        rbox_x(cav_x0,box_x1+1,cav_y0,cav_y1,cav_z0,cav_z1,corner_r-2);
    }
    for(p=cover_screw_pts()) at_yz(p,cav_x0-1) x_cyl(5.5,box_x1-cav_x0+1,false);
    at_yz(hinge_yz,cav_x0-1) x_cyl(12.5,left_seat_x1-cav_x0+1,false);    // boss del 626ZZ
}

module saddles(){
    // gusci d'appoggio
    tube_shell(ota_r,ota_r+saddle_thickness,saddle_x0,saddle_x1,front_saddle_z[0],front_saddle_z[1]);
    tube_shell(ota_r,ota_r+saddle_thickness,saddle_x0,saddle_x1,rear_saddle_z[0],rear_saddle_z[1]);
    // costole: dal guscio fino al fondo del vano o del riduttore
    for(r=[[front_saddle_z[0],bay_z1,bay_y0+1],
           [front_saddle_z[1]-3,front_saddle_z[1],box_y0+1],
           [bay_z0,rear_saddle_z[1],bay_y0+1]])
        translate([saddle_x0,90,r[0]]) cube([saddle_x1-saddle_x0,r[2]-90,r[1]-r[0]]);
    // labbro in fondo alla sella posteriore: la cinghia non scivola via
    tube_shell(ota_r,ota_r+saddle_thickness+strap_lip,saddle_x0,saddle_x1,
               rear_saddle_z[0],rear_saddle_z[0]+strap_lip);
}

module bay_body(){
    difference(){
        translate([bay_x0,bay_y0,bay_z0]) cube([bay_x1-bay_x0,bay_y1-bay_y0,bay_z1-bay_z0]);
        translate([bay_x0+bay_wall,bay_y0+bay_wall,bay_z0+bay_wall])
            cube([bay_x1-bay_x0,bay_y1-bay_y0-2*bay_wall,bay_z1-bay_z0-2*bay_wall]);
    }
    // bossoli per le viti del coperchio: due dentro in alto, due fuori sotto il fondo
    for(p=bay_bosses)
        if(p[0]>bay_y0) at_yz(p,bay_x0) x_cyl(bay_boss_d/2,bay_x1-bay_x0,false);
        else hull(){
            at_yz(p,bay_x1-10) x_cyl(bay_boss_d/2,10,false);
            translate([bay_x1-18,bay_y0-0.5,p[1]-bay_boss_d/2]) cube([1,1,bay_boss_d]);
        }
    // listello che trattiene il lato interno del vassoio
    translate([bay_x0+bay_wall,bay_y0+bay_wall+tray_ledge_y[0],bay_z0+bay_wall])
        cube([3,tray_ledge_y[1]-tray_ledge_y[0],bay_z1-bay_z0-2*bay_wall]);
}

module housing_cuts(){
    // il tubo
    translate([0,0,-200]) cylinder(r=ota_r,h=230,$fn=240);
    // 626ZZ di sinistra: sede aperta verso l'interno, labbro verso l'esterno
    at_yz(hinge_yz,left_seat_x0) x_cyl(bearing_od/2,left_seat_x1-left_seat_x0+1,false);
    at_yz(hinge_yz,box_x0-1) x_cyl(bearing_lip_hole/2,bearing_lip+2,false);
    // perno M5 del composto
    at_yz(compound_yz,box_x0-1) x_cyl(intermediate_shaft_d/2,wall+2,false);
    // inserti M3 del coperchio del riduttore
    for(p=cover_screw_pts()) at_yz(p,box_x1-6.5) x_cyl(2.0,7,false);
    // viti M3 della piastra sensori, dalla parete sinistra
    for(a=hall_screw_a)
        at_yz(hinge_yz+hall_screw_r*[sin(a),cos(a)],box_x0-1) x_cyl(1.7,wall+2,false);
    // viti M3 della staffa motore, dal fondo
    for(s=mb_screws) translate([s[0],box_y0-1,s[1]]) y_cyl(3.4,wall+2);
    // passaggio cavi fra riduttore e vano (attraversa le due pareti)
    translate([cable_slot[0],cable_slot[2],bay_z1-bay_wall-1])
        cube([cable_slot[1]-cable_slot[0],cable_slot[3]-cable_slot[2],bay_wall+wall+2]);
    // inserti M3 del coperchio del vano
    for(p=bay_bosses) at_yz(p,bay_x1-6.5) x_cyl(2.0,7,false);
    // sfiati sulla parete posteriore del vano
    for(y=[176,184,192,200]) translate([96,y,bay_z0-1]) cube([44,3,bay_wall+2]);
    // logo sulla faccia anteriore del riduttore
    if(logo) translate([box_x,0,box_z1-logo_depth]) linear_extrude(logo_depth+1) logo_2d();
}

module housing(){
    difference(){
        union(){ gearbox_body(); bay_body(); saddles(); }
        housing_cuts();
    }
}

// =============================================================================
//  COPERCHIO DEL RIDUTTORE
//  Faccia esterna piana: si stampa appoggiato su quella.
// =============================================================================
module cover(){
    difference(){
        union(){
            rbox_x(box_x1,box_x1+cover_t,box_y0,box_y1,box_z0,box_z1,corner_r);
            at_yz(hinge_yz,cover_seat_x0) x_cyl(13,box_x1-cover_seat_x0+0.01,false);   // boss 626ZZ
        }
        at_yz(hinge_yz,cover_seat_x0-1) x_cyl(bearing_od/2,cover_seat_x1-cover_seat_x0+1,false);
        at_yz(hinge_yz,cover_seat_x1-1) x_cyl(bearing_lip_hole/2,10,false);
        at_yz(compound_yz,box_x1-1) x_cyl(intermediate_shaft_d/2,cover_t+2,false);
        for(p=cover_screw_pts()) at_yz(p,box_x1-1) x_cyl(1.7,cover_t+2,false);
    }
}

// =============================================================================
//  STAFFA MOTORE (in coordinate globali)
//  Piastra verticale con il foro per la carcassa e un intaglio per il
//  cappuccio dei fili; piede sul fondo con due inserti M3 avvitati da sotto.
//  Le orecchie si fissano con due M3x8 direttamente nella plastica; i fori
//  da 4,2 delle orecchie danno circa 0,6 mm di registrazione.
// =============================================================================
module motor_bracket(){
    difference(){
        union(){
            // piastra
            // rotate([90,0,90]) porta il piano 2D (Y,Z) sul piano YZ globale
            translate([mb_plate_x0,0,0]) rotate([90,0,90])
                linear_extrude(mb_plate_t) hull(){
                    translate(can_yz) circle(r=mb_ring_r);
                    for(e=byj_ears) translate(e) circle(r=6);
                    translate([cav_y0,mb_foot_z[0]]) square([mb_foot_t,mb_foot_z[1]-mb_foot_z[0]]);
                }
            // piede
            translate([mb_plate_x0,cav_y0,mb_foot_z[0]])
                cube([mb_foot_x1-mb_plate_x0,mb_foot_t,mb_foot_z[1]-mb_foot_z[0]]);
            translate([mb_block_x0,cav_y0,mb_foot_z[0]])
                cube([mb_foot_x1-mb_block_x0,mb_block_t,mb_foot_z[1]-mb_foot_z[0]]);
        }
        // carcassa
        at_yz(can_yz,mb_plate_x0-1) x_cyl(mb_can_hole_r,mb_plate_t+2,false);
        // cappuccio dei fili: intaglio aperto verso il bordo
        at_yz(can_yz,mb_plate_x0-1)
            rotate([atan2(byj_w[1],byj_w[0]),0,0])      // porta +Y locale su byj_w
                translate([0,11,-9.5]) cube([mb_plate_t+2,14,19]);
        // viti delle orecchie
        for(e=byj_ears) at_yz(e,mb_plate_x0-1) x_cyl(1.25,mb_plate_t+2,false);
        // inserti M3 dal fondo
        for(s=mb_screws) translate([s[0],cav_y0-1,s[1]]) y_cyl(4.0,6.5+1);
    }
}

// =============================================================================
//  INGRANAGGI (modulo 0,8). Identici alla V4.1 tranne il foro del grano
//  dell'ingranaggio di uscita, che ora sta nel mozzo.
// =============================================================================
module output_gear(){
    difference(){
        gear_x(final_teeth,output_shaft_d+0.2,gear_t,22,10);
        translate([8,0,0]) cylinder(d=2.7,h=30,center=true);    // grano M3 nel mozzo
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
        translate([11.5,0,0]) x_cyl(compound_bearing_od/2,5.2,true);    // sede 625ZZ
    }
}
// Pignone con grano M3: denti larghi 5 mm (bastano per il primo stadio), mozzo
// lungo dal lato del coperchio. Il grano sta oltre la faccia del 42T (X 147) e
// sopra l'ultimo tratto dell'albero, dove il 28BYJ ha i due piani. Il mozzo
// (raggio 4,3) passa sotto la punta dei denti del 42T, che arriva a 4,8 mm.
pinion_face=5;
pinion_hub_d=8.6;
pinion_len=9.5;             // da X 141 a 150,5: l'albero finisce a 149,3
pinion_grub_x=7.5;          // centro del foro del grano, dalla faccia verso il motore
module motor_pinion(){
    difference(){
        gear_x(motor_teeth,motor_shaft_d,pinion_face,pinion_hub_d,pinion_len);
        translate([pinion_grub_x,0,0]) cylinder(d=2.7,h=10);    // grano M3, da un lato
    }
}

// =============================================================================
//  BANDIERINA DEL MAGNETE (sagoma della V4.1, tasca del magnete aperta verso i sensori)
// =============================================================================
module magnet_flag(){
    difference(){
        union(){ x_cyl(11,5,true); translate([0,0,magnet_r]) x_cyl(5,5,true); }
        x_cyl((output_shaft_d+0.2)/2,8,true);
        translate([-2.5,0,magnet_r]) x_cyl(magnet_d/2,magnet_depth,false);  // tasca verso i sensori
        translate([0,0,-12]) cylinder(d=2.7,h=17);                         // grano M3, dal lato opposto
    }
}

// =============================================================================
//  PIASTRA SENSORI HALL
//  Disegnata piatta: x -> dY, y -> dZ, z -> distanza dalla parete sinistra.
//  Le sedi tengono gli A3144 con la faccia marcata verso il magnete; i
//  piedini vanno verso l'esterno nel canale (+y della sede), che prosegue
//  fino al bordo. s = lato dell'incavo del condensatore.
// =============================================================================
module hall_pocket(s=1){
    top=hall_seat_h;
    translate([0,0,top-1.1]) cube([4.7,3.7,2.3],center=true);                          // corpo
    translate([-hall_chan_w/2,1,top-hall_leg_depth]) cube([hall_chan_w,hall_wire_u0-0.99,hall_leg_depth+0.1]);
    translate([-hall_wire_w/2,hall_wire_u0,top-hall_wire_depth]) cube([hall_wire_w,25,hall_wire_depth+0.1]);
    translate([s>0?hall_cap_v[0]:-hall_cap_v[1],hall_cap_u[0],top-hall_wire_depth])  // condensatore
        cube([hall_cap_v[1]-hall_cap_v[0],hall_cap_u[1]-hall_cap_u[0],hall_wire_depth+0.1]);
}
hall_names=["C","O"];       // incise vicino alle sedi: CLOSED e OPEN
module hall_plate(){
    sens=[0,-open_angle];
    difference(){
        union(){
            translate([0,0,hall_standoff]) linear_extrude(hall_plate_t)
                polygon(concat(arcpts(hall_r_out,hall_a0,hall_a1,72),arcpts(hall_r_in,hall_a1,hall_a0,72)));
            translate([0,0,hall_pad_z]) linear_extrude(hall_standoff-hall_pad_z+0.01)
                polygon(concat(arcpts(hall_r_out,hall_a0,hall_a1,72),arcpts(hall_pad_r,hall_a1,hall_a0,72)));
            for(ac=hall_screw_a) translate([hall_screw_r*sin(ac),hall_screw_r*cos(ac),0]) cylinder(d=9,h=hall_seat_h);
        }
        for(i=[0:1]) let(a=sens[i]){
            translate([magnet_r*sin(a),magnet_r*cos(a),0]) rotate([0,0,-(a+hall_leg_turn[i])]) hall_pocket(hall_cap_side[i]);
            translate([9*sin(a),9*cos(a),hall_seat_h-0.4]) rotate([0,0,-a])
                linear_extrude(1) text(hall_names[i],size=3.5,font=logo_font,halign="center",valign="center");
        }
        translate([0,0,-1]) cylinder(d=hall_hole_d,h=hall_seat_h+4);
        for(ac=hall_screw_a) for(i=[0:12]) let(a=ac-7+14*i/12)
            translate([hall_screw_r*sin(a),hall_screw_r*cos(a),-1]) cylinder(d=3.4,h=hall_seat_h+2);
    }
}

// =============================================================================
//  DISTANZIALI (in coordinate globali: X0, X1, diametro esterno, foro)
//  s1..s3 sull'albero di uscita, c1..c2 sul perno M5 del composto.
// =============================================================================
compound_x=box_x+(compound_small_x+compound_big_x)/2;     // 133
compound_x0=compound_x-11;                                 // estremo sinistro del mozzo
compound_bearing_x1=compound_x+13.9;                       // faccia esterna del 625ZZ
spacer_list=[
    ["s1",left_seat_x1,flag_x-2.5,spacer_od,output_shaft_d+0.3],
    ["s2",box_x+final_x+10,cover_seat_x0-0.3,spacer_od,output_shaft_d+0.3],
    ["s3",flag_x+2.5,box_x+final_x,spacer_od,output_shaft_d+0.3],
    ["c1",cav_x0,compound_x0-ptfe_washer_t-0.2,cspacer_od,intermediate_shaft_d+0.1],
    ["c2",compound_bearing_x1,box_x1-0.2,7.5,intermediate_shaft_d+0.1]];

module spacer_placed(s){
    yz=(s[0][0]=="s")?hinge_yz:compound_yz;
    at_yz(yz,s[1]) difference(){
        x_cyl(s[3]/2,s[2]-s[1],false);
        translate([-1,0,0]) x_cyl(s[4]/2,s[2]-s[1]+2,false);
    }
}
module spacers_placed(){ for(s=spacer_list) spacer_placed(s); }
module spacers_print(){
    for(i=[0:len(spacer_list)-1]) let(s=spacer_list[i])
        translate([i*14,0,0]) difference(){
            cylinder(d=s[3],h=s[2]-s[1]);
            translate([0,0,-1]) cylinder(d=s[4],h=s[2]-s[1]+2);
        }
}

// =============================================================================
//  MONOBRACCIO E CONTROPIASTRA
//  Sistema locale: origine sull'asse dell'albero, z verso il cielo a tappo
//  chiuso. Quattro viti M4 fissano il tappo su un quadrilatero fuori dal tubo.
// =============================================================================
foot_ang=atan2(arm_x,hinge_y);
function bolt_local(r,a)=[r*sin(a)-arm_x,r*cos(a)-hinge_y];
cap_bolts=[bolt_local(176,foot_ang-14),bolt_local(176,foot_ang+6),
           bolt_local(158,foot_ang-11),bolt_local(158,foot_ang+9)];
pad_top=arm_dz-cap_thickness/2;

module cap_pad(p,d=22){ translate([p[0],p[1],pad_top-plate_h/2]) cylinder(d=d,h=plate_h,center=true); }

module mono_arm(){
    difference(){
        union(){
            x_cyl(13,16,true);                                          // mozzo a morsetto
            translate([0,9,0]) cube([16,12,26],center=true);
            hull(){                                                    // colonna
                translate([0,-1,4]) cube([arm_w,24,12],center=true);
                translate([0,-6,pad_top-plate_h+3]) cube([arm_w,20,6],center=true);
            }
            hull(){                                                    // raccordo
                translate([0,-6,pad_top-plate_h+3]) cube([arm_w,18,6],center=true);
                cap_pad(cap_bolts[0]); cap_pad(cap_bolts[2]);
            }
            hull(){ for(p=cap_bolts) cap_pad(p); }                     // piastra del tappo
        }
        x_cyl((output_shaft_d+0.2)/2,20,true);
        translate([0,9,0]) cube([20,16,1.8],center=true);             // taglio del morsetto
        translate([0,9,0]) cylinder(d=3.3,h=34,center=true);          // vite M3
        translate([0,9,4]) cylinder(d=6.4,h=12);                      // testa
        translate([0,9,-13.01]) cylinder(d=7.0,h=3.5,$fn=6);          // dado
        for(p=cap_bolts){
            translate([p[0],p[1],pad_top-plate_h-1]) cylinder(d=4.4,h=plate_h+4);
            translate([p[0],p[1],pad_top-plate_h-0.01]) cylinder(d=7.3/cos(30),h=3.6,$fn=6);  // dadi M4
        }
    }
}

module cap_backplate(){
    difference(){
        linear_extrude(3) hull(){ for(p=cap_bolts) translate(p) circle(d=22); }
        for(p=cap_bolts) translate([p[0],p[1],-1]) cylinder(d=4.4,h=6);
    }
}

// =============================================================================
//  APPOGGIO DEL TAPPO (stampare due pezzi)
//  Si fissa al tubo con una fascetta velcro; il tappo parcheggiato ci si posa.
// =============================================================================
module cap_rest(){
    top=hinge_y-arm_dz-cap_thickness/2-rest_pad;
    difference(){
        hull(){
            translate([-30,top-6,-20]) cube([60,6,40]);
            translate([-30,ota_r-8,-12]) cube([60,6,24]);
        }
        translate([0,0,-24]) cylinder(r=ota_r,h=48,$fn=240);
        translate([-31,ota_r+3,-13]) cube([62,7,26]);            // asola per il velcro
    }
}

// =============================================================================
//  COPERCHIO E VASSOIO DEL VANO ELETTRONICA (in coordinate globali)
//  Il vassoio entra di taglio e resta fermo fra il listello della parete
//  sinistra e quello del coperchio: niente viti.
// =============================================================================
module bay_lid(){
    difference(){
        union(){
            translate([bay_x1,bay_y0-bay_boss_d,bay_z0]) cube([bay_lid_t,bay_y1-bay_y0+bay_boss_d,bay_z1-bay_z0]);
            // listello che tiene giu' il vassoio
            difference(){
                translate([bay_x1-3,bay_y0+bay_wall+tray_ledge_y[0],bay_z0+bay_wall+0.5])
                    cube([3.01,tray_ledge_y[1]-tray_ledge_y[0],bay_z1-bay_z0-2*bay_wall-1]);
                translate([bay_x1-4,usb_hole[2]-1,usb_hole[0]-1]) cube([6,usb_hole[3]-usb_hole[2]+2,usb_hole[1]-usb_hole[0]+2]);
            }
        }
        for(p=bay_bosses){                                      // M3 a testa svasata
            at_yz(p,bay_x1-1) x_cyl(1.7,bay_lid_t+2,false);
            at_yz(p,bay_x1+bay_lid_t-1.9) rotate([0,90,0]) cylinder(d1=3.4,d2=6.6,h=1.91);
        }
        translate([bay_x1-5,usb_hole[2],usb_hole[0]]) cube([bay_lid_t+6,usb_hole[3]-usb_hole[2],usb_hole[1]-usb_hole[0]]);
        at_yz(jack_yz,bay_x1-1) x_cyl(jack_d/2,bay_lid_t+2,false);
    }
}

module standoffs(pos,holes,h,d,pilot){
    for(sx=[-1,1]) for(sz=[-1,1])
        translate([pos[0]+sx*holes[0]/2,bay_y0+bay_wall+tray_t-0.01,pos[1]+sz*holes[1]/2])
            difference(){ y_cyl(d,h+0.01); translate([0,max(h-6,-1),0]) y_cyl(pilot,8); }
}

module bay_tray(){
    tx0=bay_x0+bay_wall+0.5;  tx1=bay_x1-0.5;
    tz0=bay_z0+bay_wall+0.5;  tz1=bay_z1-bay_wall-0.5;
    union(){
        translate([tx0,bay_y0+bay_wall,tz0]) cube([tx1-tx0,tray_t,tz1-tz0]);
        standoffs(nano_pos,nano_holes,nano_standoff_h,5,nano_pilot);
        standoffs(buck_pos,buck_holes,board_standoff_h,6.5,board_pilot);
        standoffs(uln_pos,uln_holes,board_standoff_h,6.5,board_pilot);
    }
}

// =============================================================================
//  ASSI DI PROVA IN PLASTICA (facoltativi)
//  Servono a provare montaggio, ingranamento e sensori prima di tagliare
//  l'albero d'acciaio e di comprare la vite M5. Si stampano sdraiati: il
//  piano per tutta la lunghezza li tiene sul piatto e fa da sede ai grani.
//  Diametri un decimo sotto il nominale: entrano nei cuscinetti senza forzare.
//  Non vanno sul telescopio: sotto i grani e nel morsetto del braccio il PLA
//  cede con il tempo.
// =============================================================================
test_shaft_d=5.9;     // albero di prova (l'acciaio e' 6)
test_pin_d=4.9;       // perno di prova del composto (al posto della vite M5)
test_flat=0.6;        // profondita' del piano
test_pin_len=box_x1+cover_t-box_x0+7;    // parete, riduttore, coperchio e ghiera

// tondo lungo Z con smussi di 0,5 mm alle due estremita'
module rod_z(d,l,c=0.5){
    rotate_extrude($fn=96) polygon([[0,0],[d/2-c,0],[d/2,c],[d/2,l-c],[d/2-c,l],[0,l]]);
}

// tutto quello che sta sotto il piano, per un pezzo sdraiato lungo X di raggio r
module below_flat(r,l){ translate([-1,-r-6,-r-6]) cube([l+2,2*r+12,6+test_flat]); }

module test_shaft(){
    r=test_shaft_d/2;
    translate([0,0,r-test_flat]) difference(){
        rotate([0,90,0]) rod_z(test_shaft_d,shaft_len);
        below_flat(r,shaft_len);
    }
}

module test_pin(){
    r=test_pin_d/2;
    translate([0,0,r-test_flat]) difference(){
        rotate([0,90,0]) union(){
            cylinder(d=9,h=3,$fn=72);                              // testa, fuori dalla parete
            translate([0,0,3]) rod_z(test_pin_d,test_pin_len);
        }
        below_flat(r,test_pin_len+3);
    }
    // ghiera elastica: si infila sul perno fuori dal coperchio
    translate([test_pin_len/2,14,0]) difference(){
        cylinder(d=10,h=5,$fn=72);
        translate([0,0,-1]) cylinder(d=test_pin_d-0.2,h=7,$fn=48);
        translate([0,-0.6,-1]) cube([6,1.2,7]);                    // taglio: fa molla
    }
}

// =============================================================================
//  SAGOME PER L'ASSIEME (non si stampano)
// =============================================================================
ota_len=650;
module ota_dummy(){
    color([0.12,0.12,0.15,0.30]) translate([0,0,-ota_len]) cylinder(d=ota_d,h=ota_len,$fn=180);
    color([0.08,0.08,0.10,0.45]) translate([0,0,-5])
        difference(){ cylinder(d=ota_d+8,h=8,$fn=180); translate([0,0,-1]) cylinder(d=ota_d-8,h=10,$fn=180); }
}
module cap_dummy(a){
    color([0.10,0.35,0.12,0.55]) translate([0,hinge_y,hinge_z]) rotate([a,0,0])
        translate([0,-hinge_y,arm_dz]) cylinder(d=cap_d,h=cap_thickness,center=true,$fn=180);
}
module motor_dummy(){
    // 28BYJ-48: carcassa eccentrica, orecchie, cappuccio dei fili, collarino
    ang=atan2(byj_w[1],byj_w[0]);
    at_yz(can_yz,byj_face_x-byj_can_h) x_cyl(byj_can_d/2,byj_can_h,false);
    at_yz(can_yz,byj_face_x-byj_ear_t) rotate([ang,0,0])
        hull() for(s=[-1,1]) translate([0,0,s*byj_hole_span/2]) x_cyl(byj_ear_w/2,byj_ear_t,false);
    at_yz(can_yz,byj_face_x-byj_can_h+1) rotate([ang,0,0])
        translate([0,12,-8.75]) cube([byj_can_h-2,5,17.5]);
    at_yz(motor_yz,byj_face_x) x_cyl(4.5,1.5,false);
    at_yz(motor_yz,byj_face_x) x_cyl(2.5,10,false);
}
module boards_dummy(){
    for(b=[[nano_pos,nano_size,nano_standoff_h],[buck_pos,buck_size,board_standoff_h],
           [uln_pos,uln_size,board_standoff_h]])
        translate([b[0][0]-b[1][0]/2,bay_y0+bay_wall+tray_t+b[2],b[0][1]-b[1][1]/2])
            cube([b[1][0],1.6,b[1][1]]);
}
module shaft_dummy(){ at_yz(hinge_yz,arm_x-8) x_cyl(output_shaft_d/2,shaft_len,false); }

// =============================================================================
//  POSIZIONI
// =============================================================================
module arm_frame(a)  { translate([arm_x,hinge_y,hinge_z]) rotate([a,0,0]) children(); }

module part_placed(p,a=0){
    if(p=="housing") housing();
    else if(p=="cover") cover();
    else if(p=="motor_bracket") motor_bracket();
    else if(p=="hall_plate") translate([cav_x0,hinge_y,hinge_z]) rotate([90,0,90]) hall_plate();
    else if(p=="spacers") spacers_placed();
    else if(p=="bay_lid") bay_lid();
    else if(p=="bay_tray") bay_tray();
    else if(p=="output_gear") at_yz(hinge_yz,box_x+final_x) output_gear();
    else if(p=="compound_gear") at_yz(compound_yz,compound_x) compound_gear();
    else if(p=="motor_pinion") at_yz(motor_yz,box_x+motor_pinion_x) motor_pinion();
    else if(p=="magnet_flag") translate([flag_x,hinge_y,hinge_z]) rotate([a,0,0]) magnet_flag();
    else if(p=="mono_arm") arm_frame(a) mono_arm();
    else if(p=="cap_backplate") arm_frame(a) translate([0,0,arm_dz+cap_thickness/2]) cap_backplate();
    else if(p=="cap_rest") translate([0,0,rest_z[0]]) cap_rest();
    else if(p=="motor_dummy") motor_dummy();
    else echo(str("PEZZO SCONOSCIUTO: ",p));
}

// Orientamento di stampa: faccia piu' grande e piana sul piatto.
module part_print(p){
    if(p=="housing") translate([0,0,-box_x0]) rotate([0,-90,0]) housing();
    else if(p=="cover") translate([0,0,box_x1+cover_t]) rotate([0,90,0]) cover();
    else if(p=="motor_bracket") translate([0,0,-mb_plate_x0]) rotate([0,-90,0]) motor_bracket();
    else if(p=="hall_plate") translate([0,0,hall_seat_h]) rotate([180,0,0]) hall_plate();
    else if(p=="spacers") spacers_print();
    else if(p=="bay_lid") translate([0,0,bay_x1+bay_lid_t]) rotate([0,90,0]) bay_lid();
    else if(p=="bay_tray") translate([0,0,-(bay_y0+bay_wall)]) rotate([90,0,0]) bay_tray();
    else if(p=="output_gear") rotate([0,-90,0]) output_gear();
    else if(p=="compound_gear") translate([0,0,14]) rotate([0,90,0]) compound_gear();
    else if(p=="motor_pinion") rotate([0,-90,0]) motor_pinion();
    else if(p=="magnet_flag") translate([0,0,2.5]) rotate([0,90,0]) magnet_flag();
    else if(p=="mono_arm") translate([0,0,8]) rotate([0,90,0]) mono_arm();
    else if(p=="cap_backplate") cap_backplate();
    else if(p=="cap_rest") translate([0,0,hinge_y-arm_dz-cap_thickness/2-rest_pad]) rotate([-90,0,0]) cap_rest();
    else if(p=="test_shaft") test_shaft();
    else if(p=="test_pin") test_pin();
    else echo(str("PEZZO SCONOSCIUTO: ",p));
}

module assembly(){
    a=cap_angle;
    if(show_ota) ota_dummy();
    if(show_cap) cap_dummy(a);
    if(show_housing) color([0.08,0.26,0.45,0.90]) render() part_placed("housing");
    if(show_cover) color([0.10,0.32,0.55,0.35]) render() part_placed("cover");
    if(show_bay_lid) color([0.30,0.20,0.55,0.40]) render() part_placed("bay_lid");
    if(show_bay_tray) color([0.85,0.85,0.88]) render() part_placed("bay_tray");
    if(show_boards) color([0.10,0.45,0.25]) boards_dummy();
    if(show_bracket) color([0.20,0.55,0.30]) render() part_placed("motor_bracket");
    if(show_motor) color([0.40,0.40,0.45]) motor_dummy();
    if(show_gears) color([0.95,0.52,0.08]){
        render() part_placed("output_gear");
        render() part_placed("compound_gear");
        render() part_placed("motor_pinion");
    }
    if(show_shaft) color([0.72,0.72,0.76]) shaft_dummy();
    if(show_spacers) color([0.95,0.95,0.95]) render() part_placed("spacers");
    if(show_hall) color([0.85,0.85,0.90]) render() part_placed("hall_plate");
    if(show_flag) color([0.95,0.75,0.10]) render() part_placed("magnet_flag",a);
    if(show_arm) color([0.80,0.12,0.10]) render() part_placed("mono_arm",a);
    if(show_backplate) color([0.55,0.10,0.08]) render() part_placed("cap_backplate",a);
    if(show_rests) color([0.90,0.60,0.15]) for(z=rest_z) translate([0,0,z]) render() cap_rest();
}

// =============================================================================
//  USCITA
// =============================================================================
if(part=="assembly") assembly();
else if(orient=="print") part_print(part);
else part_placed(part,cap_angle);
