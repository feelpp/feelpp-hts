h=1e-4;
LcTapes=h*0.1;
LcAir=h*10;
LcInf=h*20;

s=0; 
Jc0=4.75e10; 
Bc=35e-3; 
b=0.6; 
k=0.25;             // Jc(B) parameters
ns=10;
ny=ns/2;                        // ns=number of strands in cable

th=1e-6; //tape thickness
sw=1.8e-3; // strand width
rg=4e-4; // roebel gap
sg=1e-4; // Roebel inter-strand gap
n=21; 
tolAz=1e-9; 
tolp=1e-9;

I0=Jc0*th*sw; 
x0=-sw-rg/2; 
y0=-((th+sg)*ny-sg)/2; 
E=0;

R_air=10*(sw+rg/2);


//-----------------------------------------------------------------------------
// Definition of points

// Origin
p0 = newp; Point(p0) = {0, 0, 0, LcAir};
a1 = newp; Point(a1) = {R_air, 0, 0, LcAir};
a2 = newp; Point(a2) = {-R_air, 0, 0, LcAir};

c1 = newl; Circle(c1) = {a1, p0, a2};
c2 = newl; Circle(c2) = {a2, p0, a1};
ll0 = newll; Line Loop(ll0)= {c1,c2};

ll={0,0,0,0,0,0,0,0,0,0};
tapes={0,0,0,0,0,0,0,0,0,0};
// Conductor
For i In {0:ns-1}
    XC=x0+(rg+sw)*(i%2); 
    YC=y0+(sg+th)*(i%ny);
    p1 = newp; Point(p1) = {XC,    YC+th, 0, LcTapes};
    p2 = newp; Point(p2) = {XC+sw, YC+th, 0, LcTapes};
    p3 = newp; Point(p3) = {XC+sw, YC,    0, LcTapes};
    p4 = newp; Point(p4) = {XC,    YC,    0, LcTapes};
    
    p1p2 = newl; Line(p1p2) = {p1, p2};
    p2p3 = newl; Line(p2p3) = {p2, p3};
    p3p4 = newl; Line(p3p4) = {p3, p4};
    p4p1 = newl; Line(p4p1) = {p4, p1};
    ll1 = news; Line Loop(ll1) = {p1p2, p2p3, p3p4, p4p1};
    s = news; Plane Surface(s) = {ll1};

    ll[i] = ll1;
    tapes[i]=s;
EndFor


AIR = news; Plane Surface(AIR) = {ll0,-ll[]};



Physical Surface("Air") = {AIR};
Physical Surface("tape_0") = {tapes[0]};
Physical Surface("tape_1") = {tapes[1]};
Physical Surface("tape_2") = {tapes[2]};
Physical Surface("tape_3") = {tapes[3]};
Physical Surface("tape_4") = {tapes[4]};
Physical Surface("tape_5") = {tapes[5]};
Physical Surface("tape_6") = {tapes[6]};
Physical Surface("tape_7") = {tapes[7]};
Physical Surface("tape_8") = {tapes[8]};
Physical Surface("tape_9") = {tapes[9]};

Physical Line("Exterior_boundary") = {c1,c2};