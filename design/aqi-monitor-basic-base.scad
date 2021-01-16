include<aqi-common.scad>;

/*
// fit testing
translate([0,0,23])
rotate([0,180,180])
import("aqi-monitor-basic-cover.stl");
*/

// width and height of board
W=138;
H=68;

// how much the whole board layout is offset from origin
TX=34;
TY=-23;

// how much the display is offset from center
DX=-51;
DY=11;

difference() {
    union() {
            cube_center([W,H,1.5]);
        difference() {
            cube_center([W,H,3]);
            cube_center([W-3,H-3, 6]);
            
        }
        for(s=[-1,1]) for(t=[-1,1])
            translate([s*(W-8)/2,t*(H-8)/2])
            cube_center([8,8,15]);
    }
    for(s=[-1,1]) for(t=[-1,1]) {
        translate([s*(W-8)/2,t*(H-8)/2]) {
            cylinder(d=6,h=3.5,$fn=32);
            cylinder(d=3.3,h=50,$fn=32);
        }
    }
}

translate([TX,TY,1.5]) {
    translate([31,4,0]) usbport();
    
    translate([0,4,0])
    feathers2();
    
    translate([-83,5,0])
    rotate([0,0,90])
    bme680();
    
    translate([0,35,0])
    pmsa003i();
    
    translate([-50,23,0])
    rotate([0,0,90])
    scd30();
    
    translate([DX,DY,0])
    translate([-TX,-TY,0])
    translate([(9-6.5)/2,(7.5-2.5)/2,0])
    rotate([0,0,90])
    display();
}