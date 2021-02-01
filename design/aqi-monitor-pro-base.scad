   
difference() {
    union() {
            cube_center([105,180,1.5]);
        difference() {
            cube_center([105,180,3]);
            cube_center([105-3,180-3, 6]);
            
        }
        for(s=[-1,1]) for(t=[-1,0,1])
            translate([s*97/2,t*172/2])
            cube_center([8,8,15]);
    }
    for(s=[-1,1]) for(t=[-1,0,1]) {
        translate([s*97/2,t*172/2]) {
            cylinder(d=6,h=3.5,$fn=32);
            cylinder(d=3.5,h=50,$fn=32);
        }
    }
}

translate([17.5,27,1.5]) {
    translate([31,4,0]) usbport();
    
    translate([0,4,0])
    feathers2();
    translate([-48,0,0])
    qwiicstar();
    
    //bno085(); // imu
    
    translate([-44,-26,0])
    bno085();
    translate([-44,-47,0])
    bme680(); // temperature, humidity, pressure, voc
    translate([-44,-66,0])
    sgp30(); // voc
    translate([-44,-85,0])
    tsl2591(); // voc
    
    translate([0,-69.75,0])
    pmsa003i(); // pm2.5
    
    translate([13,-28.5,0])
    rotate([0,0,90])
    sen0321();
    
    translate([-7,39,0])
    scd30();
    
    translate([-47,39,0])
    mcgasv2();
    
    //translate([16,-70,0])
    //tc6713();
    
    translate([-17.5,-105,0])
    gamma();
    
    translate([-17.5,-27,0])
    
    translate([(9-6.5)/2,(7.5-2.5)/2,0])
    rotate([0,0,90])
    display();
    
}



module usbport() {
    difference() {
    cube_center([8,18,13]);
    translate([-6,0,1+1.5+4])
    rotate([0,0,90])
    rotate([90,0,0])
        usbplugshape(Q=12.5,R=7.75);
    }
}

module usbplugshape(Q=12,R=7) {
    translate([-Q/2+R/2,0,0])
    cylinder(d=R,h=20,$fn=64);
    translate([Q/2-R/2,0,0])
    cylinder(d=R,h=20,$fn=64);
    cube_center([Q-R,R,20]);
}

module tc6713() {
    difference() {
        cube_center([15+3,31+3,9.5]);
        translate([0,0,2.5])
        cube_center([15.3,31.3,8]);
        cube_center([13.3,31.3,8]);
        translate([0,11.15,0])
        cube_center([50,9,10]);
        translate([0,-11.15,0])
        cube_center([50,9,10]);
        cube_center([8,100,10]);
        translate([0,28,5])
        cube_center([30,30,10]);
        translate([0,-28,5])
        cube_center([30,30,10]);
    }
    translate([-20/2,0,0])
    standoff(sh=9.5);
    translate([20/2,0,0])
    standoff(sh=9.5);
}

module gamma() {
    
    
    difference() {
        cube_center([88,21,0.15]);
        cube_center([88-1,21-1,0.3]);
    }
    linear_extrude(height = 0.15) text("RADSENS", font = "Liberation Sans:style=Bold", valign="center", halign="center",size=4);
    
    translate([83/2,21/2-8,0])
    standoff(sh=4,screw=2.5);
    translate([-83/2,21/2-8,0])
    standoff(sh=4,screw=2.5);
}

module mcgasv2() {
    translate([20/2,-40/2+10,0]) standoff(sh=4,d=6,screw=2);
    translate([-20/2,-40/2+10,0]) standoff(sh=4,d=6,screw=2);
    translate([20/2,40/2-10,0]) standoff(sh=4,d=6,screw=2);
    translate([-20/2,40/2-10,0]) standoff(sh=4,d=6,screw=2);
    translate([0,40/2,0]) standoff(sh=4,d=6,screw=2);
    translate([0,-40/2,0]) standoff(sh=4,d=6,screw=2);
    difference() {
        cube_center([20,40,0.15]);
        cube_center([20-1,40-1,0.3]);
    }
    rotate([0,0,90])
    linear_extrude(height = 0.15) text("MCGASV2", font = "Liberation Sans:style=Bold", valign="center", halign="center",size=4);
}

module scd30() {
        difference() {
            union() {
    for(q=[-20:20:20]) for(r=[-20,20])
    translate([q,r,0]) standoff(sh=4,d=6,screw=2);
    for(q=[-30,30]) for(r=[-10,10])
    translate([q,r,0]) standoff(sh=4,d=6,screw=2);
    
    quadboard(W=2.0*25.4,H=1.0*25.4,w=1.8*25.4,h=.8*25.4,screw=2.5, text="SCD30");
        //cube_center([60,40,0.15]);
}
    }
    
}

module display() {
    quadboard(W=1.35*25.4,w=1.10*25.4,H=0.86*25.4,h=0.65*25.4, text = "DISPLAY",screw=2.5,sh=14,d=6);
}

module feathers2() {
    quadboard(W=50.5,w=45.75,H=22.5,h=17.75, text = "FEATHERS2",screw=2.5);
}

module pmsa003i() {
    quadboard(W=2.00*25.4,w=1.8*25.4,H=1.4*25.4,h=1.2*25.4, text="PMSA003I", screw=2.5);
}

module sen0321() {
    quadboard(W=37,w=30,H=27,h=20,sh=6.5,screw=3,d=6, text="SEN0321");
}

module bme680() {
    quadboard(W=1.0*25.4,w=0.8*25.4,H=0.70*25.4,h=0.5*25.4, text="BME680", screw=2.5);
}

module tsl2591() {
    quadboard(W=1.0*25.4,w=0.8*25.4,H=0.70*25.4,h=0.5*25.4, screw=2.5, text="?");
}

module sgp30() {
    quadboard(W=1.0*25.4,w=0.8*25.4,H=0.70*25.4,h=0.5*25.4, text="SGP30", screw=2.5);
}

module bno085() {
    quadboard(W=1.0*25.4,w=0.8*25.4,H=0.90*25.4,h=0.7*25.4, text="BNO085", screw=2.5);
}

module qwiicstar() {
    translate([-7.5/2,-7.5/2,0]) standoff(sh=4,d=6,screw=3);
    translate([7.5/2,7.5/2,0]) standoff(sh=4,d=6,screw=3);
    difference() {
        cube_center([26,26,0.15]);
        cube_center([26-1,26-1,0.3]);
    }
}

module quadboard(W=25,w=20.25,H=18,h=13,sh=4,screw=2.5,d=5, text = "") {
    translate([-w/2,-h/2,0]) standoff(sh=sh,screw=screw,d=d);
    translate([-w/2,h/2,0]) standoff(sh=sh,screw=screw,d=d);
    translate([w/2,-h/2,0]) standoff(sh=sh,screw=screw,d=d);
    translate([w/2,h/2,0]) standoff(sh=sh,screw=screw,d=d);
    difference() {
        cube_center([W,H,0.15]);
        cube_center([W-1,H-1,0.3]);
    }
    linear_extrude(height = 0.15) text(text, font = "Liberation Sans:style=Bold", valign="center", halign="center",size=4);
}

module standoff(d=5,screw=1.5,sh=4) {
    difference() {
        cylinder(d1=d+0.5,d2=d-1,h=sh,$fn=32);
        cylinder(d=screw-0.3,h=sh+1,$fn=32);
        translate([0,0,sh-0.999])
        cylinder(d2=screw+0.3,d1=screw-0.3,h=1,$fn=32);
    }
}

module cube_center(dims,r=0,$fn=16) {
    if(r==0) {
        translate([-dims[0]/2, -dims[1]/2, 0])
        cube(dims);
    } else {
        minkowski() {
            translate([-(dims[0]-2*r)/2, -(dims[1]-2*r)/2, 0])
            cube([dims[0]-2*r,dims[1]-2*r,dims[2]]);
            cylinder(r=r,$fn=$fn,h=0.0001);
        }
    }
}