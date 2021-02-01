{
  difference() {
      union() {
    cube_center([105+3,180+3,23],r=2.5);
          
      }
  translate([0,0,1.5])
  difference() {
    cube_center([105.3,180.3,23]);
      cube_center([11,29,0.5+2.5]);
  }
  difference() {
    for(x=[-48:6:48]) for(y=[-84:6:84])
      translate([x,y,0])
      cube_center([3.5,3.5,3]);
    
      cube_center([17,41,100]);
  }
  
  translate([-60,27+4,23-8])
  //cube_center([100,16,11]);
  rotate([90,0,90]) {
        usbplugshape(Q=12.5+2,R=7.75+2);
    }
    
  cube_center([8,26,100]);
         
}
  
  
    
    
  difference() {
              for(s=[-1,1]) for(t=[-1,0,1])
            translate([s*97/2,t*172/2])
            cube_center([8.3,8.3,8-0.15]);
          
  for(s=[-1,1]) for(t=[-1,0,1]) {
        translate([s*97/2,t*172/2,1.5]) {
            cylinder(d=5.4,h=15,$fn=64);
        }
    }
}

}



module usbplugshape(Q=12,R=7) {
    translate([-Q/2+R/2,0,0])
    cylinder(d=R,h=20,$fn=64);
    translate([Q/2-R/2,0,0])
    cylinder(d=R,h=20,$fn=64);
    cube_center([Q-R,R,20]);
}
    

module cube_center(dims,r=0,$fn=64) {
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