include<aqi-common.scad>;

W=138;
H=68;
TX=34;
TY=-23;
DX=-51;
DY=11;

{
  difference() {
      union() {
    cube_center([W+3,H+3,23],r=2.5);
          
      }
  translate([0,0,1.5])
  difference() {
      cube_center([W+.3,H+.3,23]);
      
      translate([DX,-DY,0])
      cube_center([11,29,0.5+2.5]);
  }
  difference() {
      for(x=[-63:6:63]) for(y=[-30:6:30])
      translate([x,y,0])
      cube_center([3.5,3.5,3]);
      
      translate([DX,-DY,0])
      cube_center([17,43,100]);
  }
  
  //translate([-60,27+4,23-8])
  translate([31+TX,-(   4+TY),23-8]) 
  //cube_center([100,16,11]);
  rotate([90,0,90]) {
        usbplugshape(Q=12.5+2,R=7.75+2);
    }
  
  translate([DX,-DY,0])
  cube_center([8,26,100]);
         
}

difference() {
              for(s=[-1,1]) for(t=[-1,1])
            translate([s*(W-8)/2,t*(H-8)/2])
            cube_center([8,8,8-0.15]);
          
  for(s=[-1,1]) for(t=[-1,1]) {
        translate([s*(W-8)/2,t*(H-8)/2,3]) {
            cylinder(d=4.7,h=5,$fn=32);
        }
    }
}

}



