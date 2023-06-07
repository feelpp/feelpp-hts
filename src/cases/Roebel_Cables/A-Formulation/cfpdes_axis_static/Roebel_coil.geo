h=5e-3;
LcTapes=h*0.1;
LcAir=h*3;
LcInf=h*5;

s=0; 
Jc0=3.5e10; 
Bc=35e-3; 
b=0.6; 
k=0.25;             // Jc(B) parameters
ns=10;
ny=ns/2;                        // ns=number of strands in cable

th=1e-6; //tape thickness
sw=5.5e-3; // strand width
rg=1e-3; // roebel gap
sg=0.5e-4; // Roebel inter-strand gap
sf=4.3e-2;
wg=4e-3;   // winding gap

n=21; 
tolAz=1e-9; 
tolp=1e-9;

I0=Jc0*th*sw; 
y0=-sw-rg/2; 
x0=sf;
E=0;

R_air=15e-2;
H_air=5e-2;


//-----------------------------------------------------------------------------
// Definition of points

// // Origin
p0 = newp; Point(p0) = {0, 0, 0, LcTapes};
b1 = newp; Point(b1) = {0, H_air, 0, LcAir};
b2 = newp; Point(b2) = {R_air, H_air, 0, LcInf};
b3 = newp; Point(b3) = {R_air, -H_air, 0, LcInf};
b4 = newp; Point(b4) = {0, -H_air, 0, LcAir};

b1b2 = newl; Line(b1b2) = {b1, b2};
b2b3 = newl; Line(b2b3) = {b2, b3};
b3b4 = newl; Line(b3b4) = {b3, b4};
b4p0 = newl; Line(b4p0) = {b4, p0};
p0b1 = newl; Line(p0b1) = {p0, b1};
ll123 = newll; Line Loop(ll123)= {b1b2,b2b3,b3b4,b4p0,p0b1};

ll0={0,0,0,0,0,0,0,0,0,0};
tapes0={0,0,0,0,0,0,0,0,0,0};
// Conductor
For i In {0:ns-1}
    XC=x0+(sg+th)*(Floor(i/2)); 
    YC=y0+(rg+sw)*(i%2);
    p1 = newp; Point(p1) = {XC,    YC+sw, 0, LcTapes};
    p2 = newp; Point(p2) = {XC+th, YC+sw, 0, LcTapes};
    p3 = newp; Point(p3) = {XC+th, YC,    0, LcTapes};
    p4 = newp; Point(p4) = {XC,    YC,    0, LcTapes};
    
    p1p2 = newl; Line(p1p2) = {p1, p2};
    p2p3 = newl; Line(p2p3) = {p2, p3};
    p3p4 = newl; Line(p3p4) = {p3, p4};
    p4p1 = newl; Line(p4p1) = {p4, p1};
    lll = news; Line Loop(lll) = {p1p2, p2p3, p3p4, p4p1};
    s = news; Plane Surface(s) = {lll};

    ll0[i] = lll;
    tapes0[i]=s;
EndFor
Physical Surface("tape_00") = {tapes0[0]};
Physical Surface("tape_01") = {tapes0[1]};
Physical Surface("tape_02") = {tapes0[2]};
Physical Surface("tape_03") = {tapes0[3]};
Physical Surface("tape_04") = {tapes0[4]};
Physical Surface("tape_05") = {tapes0[5]};
Physical Surface("tape_06") = {tapes0[6]};
Physical Surface("tape_07") = {tapes0[7]};
Physical Surface("tape_08") = {tapes0[8]};
Physical Surface("tape_09") = {tapes0[9]};

ll1={0,0,0,0,0,0,0,0,0,0};
tapes1={0,0,0,0,0,0,0,0,0,0};
// Conductor
For i In {0:ns-1}
    XC=x0+(wg+(sg+th)*Floor(9/2))+(sg+th)*(Floor(i/2)); 
    YC=y0+(rg+sw)*(i%2);
    p1 = newp; Point(p1) = {XC,    YC+sw, 0, LcTapes};
    p2 = newp; Point(p2) = {XC+th, YC+sw, 0, LcTapes};
    p3 = newp; Point(p3) = {XC+th, YC,    0, LcTapes};
    p4 = newp; Point(p4) = {XC,    YC,    0, LcTapes};
    
    p1p2 = newl; Line(p1p2) = {p1, p2};
    p2p3 = newl; Line(p2p3) = {p2, p3};
    p3p4 = newl; Line(p3p4) = {p3, p4};
    p4p1 = newl; Line(p4p1) = {p4, p1};
    lll = news; Line Loop(lll) = {p1p2, p2p3, p3p4, p4p1};
    s = news; Plane Surface(s) = {lll};

    ll1[i] = lll;
    tapes1[i]=s;
EndFor
Physical Surface("tape_10") = {tapes1[0]};
Physical Surface("tape_11") = {tapes1[1]};
Physical Surface("tape_12") = {tapes1[2]};
Physical Surface("tape_13") = {tapes1[3]};
Physical Surface("tape_14") = {tapes1[4]};
Physical Surface("tape_15") = {tapes1[5]};
Physical Surface("tape_16") = {tapes1[6]};
Physical Surface("tape_17") = {tapes1[7]};
Physical Surface("tape_18") = {tapes1[8]};
Physical Surface("tape_19") = {tapes1[9]};

ll2={0,0,0,0,0,0,0,0,0,0};
tapes2={0,0,0,0,0,0,0,0,0,0};
// Conductor
For i In {0:ns-1}
    XC=x0+2*(wg+(sg+th)*Floor(9/2))+(sg+th)*(Floor(i/2)); 
    YC=y0+(rg+sw)*(i%2);
    p1 = newp; Point(p1) = {XC,    YC+sw, 0, LcTapes};
    p2 = newp; Point(p2) = {XC+th, YC+sw, 0, LcTapes};
    p3 = newp; Point(p3) = {XC+th, YC,    0, LcTapes};
    p4 = newp; Point(p4) = {XC,    YC,    0, LcTapes};
    
    p1p2 = newl; Line(p1p2) = {p1, p2};
    p2p3 = newl; Line(p2p3) = {p2, p3};
    p3p4 = newl; Line(p3p4) = {p3, p4};
    p4p1 = newl; Line(p4p1) = {p4, p1};
    lll = news; Line Loop(lll) = {p1p2, p2p3, p3p4, p4p1};
    s = news; Plane Surface(s) = {lll};

    ll2[i] = lll;
    tapes2[i]=s;
EndFor
Physical Surface("tape_20") = {tapes2[0]};
Physical Surface("tape_21") = {tapes2[1]};
Physical Surface("tape_22") = {tapes2[2]};
Physical Surface("tape_23") = {tapes2[3]};
Physical Surface("tape_24") = {tapes2[4]};
Physical Surface("tape_25") = {tapes2[5]};
Physical Surface("tape_26") = {tapes2[6]};
Physical Surface("tape_27") = {tapes2[7]};
Physical Surface("tape_28") = {tapes2[8]};
Physical Surface("tape_29") = {tapes2[9]};

ll3={0,0,0,0,0,0,0,0,0,0};
tapes3={0,0,0,0,0,0,0,0,0,0};
// Conductor
For i In {0:ns-1}
    XC=x0+3*(wg+(sg+th)*Floor(9/2))+(sg+th)*(Floor(i/2)); 
    YC=y0+(rg+sw)*(i%2);
    p1 = newp; Point(p1) = {XC,    YC+sw, 0, LcTapes};
    p2 = newp; Point(p2) = {XC+th, YC+sw, 0, LcTapes};
    p3 = newp; Point(p3) = {XC+th, YC,    0, LcTapes};
    p4 = newp; Point(p4) = {XC,    YC,    0, LcTapes};
    
    p1p2 = newl; Line(p1p2) = {p1, p2};
    p2p3 = newl; Line(p2p3) = {p2, p3};
    p3p4 = newl; Line(p3p4) = {p3, p4};
    p4p1 = newl; Line(p4p1) = {p4, p1};
    lll = news; Line Loop(lll) = {p1p2, p2p3, p3p4, p4p1};
    s = news; Plane Surface(s) = {lll};

    ll3[i] = lll;
    tapes3[i]=s;
EndFor
Physical Surface("tape_30") = {tapes3[0]};
Physical Surface("tape_31") = {tapes3[1]};
Physical Surface("tape_32") = {tapes3[2]};
Physical Surface("tape_33") = {tapes3[3]};
Physical Surface("tape_34") = {tapes3[4]};
Physical Surface("tape_35") = {tapes3[5]};
Physical Surface("tape_36") = {tapes3[6]};
Physical Surface("tape_37") = {tapes3[7]};
Physical Surface("tape_38") = {tapes3[8]};
Physical Surface("tape_39") = {tapes3[9]};

ll4={0,0,0,0,0,0,0,0,0,0};
tapes4={0,0,0,0,0,0,0,0,0,0};
// Conductor
For i In {0:ns-1}
    XC=x0+4*(wg+(sg+th)*Floor(9/2))+(sg+th)*(Floor(i/2)); 
    YC=y0+(rg+sw)*(i%2);
    p1 = newp; Point(p1) = {XC,    YC+sw, 0, LcTapes};
    p2 = newp; Point(p2) = {XC+th, YC+sw, 0, LcTapes};
    p3 = newp; Point(p3) = {XC+th, YC,    0, LcTapes};
    p4 = newp; Point(p4) = {XC,    YC,    0, LcTapes};
    
    p1p2 = newl; Line(p1p2) = {p1, p2};
    p2p3 = newl; Line(p2p3) = {p2, p3};
    p3p4 = newl; Line(p3p4) = {p3, p4};
    p4p1 = newl; Line(p4p1) = {p4, p1};
    lll = news; Line Loop(lll) = {p1p2, p2p3, p3p4, p4p1};
    s = news; Plane Surface(s) = {lll};

    ll4[i] = lll;
    tapes4[i]=s;
EndFor
Physical Surface("tape_40") = {tapes4[0]};
Physical Surface("tape_41") = {tapes4[1]};
Physical Surface("tape_42") = {tapes4[2]};
Physical Surface("tape_43") = {tapes4[3]};
Physical Surface("tape_44") = {tapes4[4]};
Physical Surface("tape_45") = {tapes4[5]};
Physical Surface("tape_46") = {tapes4[6]};
Physical Surface("tape_47") = {tapes4[7]};
Physical Surface("tape_48") = {tapes4[8]};
Physical Surface("tape_49") = {tapes4[9]};

ll5={0,0,0,0,0,0,0,0,0,0};
tapes5={0,0,0,0,0,0,0,0,0,0};
// Conductor
For i In {0:ns-1}
    XC=x0+5*(wg+(sg+th)*Floor(9/2))+(sg+th)*(Floor(i/2)); 
    YC=y0+(rg+sw)*(i%2);
    p1 = newp; Point(p1) = {XC,    YC+sw, 0, LcTapes};
    p2 = newp; Point(p2) = {XC+th, YC+sw, 0, LcTapes};
    p3 = newp; Point(p3) = {XC+th, YC,    0, LcTapes};
    p4 = newp; Point(p4) = {XC,    YC,    0, LcTapes};
    
    p1p2 = newl; Line(p1p2) = {p1, p2};
    p2p3 = newl; Line(p2p3) = {p2, p3};
    p3p4 = newl; Line(p3p4) = {p3, p4};
    p4p1 = newl; Line(p4p1) = {p4, p1};
    lll = news; Line Loop(lll) = {p1p2, p2p3, p3p4, p4p1};
    s = news; Plane Surface(s) = {lll};

    ll5[i] = lll;
    tapes5[i]=s;
EndFor
Physical Surface("tape_50") = {tapes5[0]};
Physical Surface("tape_51") = {tapes5[1]};
Physical Surface("tape_52") = {tapes5[2]};
Physical Surface("tape_53") = {tapes5[3]};
Physical Surface("tape_54") = {tapes5[4]};
Physical Surface("tape_55") = {tapes5[5]};
Physical Surface("tape_56") = {tapes5[6]};
Physical Surface("tape_57") = {tapes5[7]};
Physical Surface("tape_58") = {tapes5[8]};
Physical Surface("tape_59") = {tapes5[9]};

ll6={0,0,0,0,0,0,0,0,0,0};
tapes6={0,0,0,0,0,0,0,0,0,0};
// Conductor
For i In {0:ns-1}
    XC=x0+6*(wg+(sg+th)*Floor(9/2))+(sg+th)*(Floor(i/2)); 
    YC=y0+(rg+sw)*(i%2);
    p1 = newp; Point(p1) = {XC,    YC+sw, 0, LcTapes};
    p2 = newp; Point(p2) = {XC+th, YC+sw, 0, LcTapes};
    p3 = newp; Point(p3) = {XC+th, YC,    0, LcTapes};
    p4 = newp; Point(p4) = {XC,    YC,    0, LcTapes};
    
    p1p2 = newl; Line(p1p2) = {p1, p2};
    p2p3 = newl; Line(p2p3) = {p2, p3};
    p3p4 = newl; Line(p3p4) = {p3, p4};
    p4p1 = newl; Line(p4p1) = {p4, p1};
    lll = news; Line Loop(lll) = {p1p2, p2p3, p3p4, p4p1};
    s = news; Plane Surface(s) = {lll};

    ll6[i] = lll;
    tapes6[i]=s;
EndFor
Physical Surface("tape_60") = {tapes6[0]};
Physical Surface("tape_61") = {tapes6[1]};
Physical Surface("tape_62") = {tapes6[2]};
Physical Surface("tape_63") = {tapes6[3]};
Physical Surface("tape_64") = {tapes6[4]};
Physical Surface("tape_65") = {tapes6[5]};
Physical Surface("tape_66") = {tapes6[6]};
Physical Surface("tape_67") = {tapes6[7]};
Physical Surface("tape_68") = {tapes6[8]};
Physical Surface("tape_69") = {tapes6[9]};


ll7={0,0,0,0,0,0,0,0,0,0};
tapes7={0,0,0,0,0,0,0,0,0,0};
// Conductor
For i In {0:ns-1}
    XC=x0+7*(wg+(sg+th)*Floor(9/2))+(sg+th)*(Floor(i/2)); 
    YC=y0+(rg+sw)*(i%2);
    p1 = newp; Point(p1) = {XC,    YC+sw, 0, LcTapes};
    p2 = newp; Point(p2) = {XC+th, YC+sw, 0, LcTapes};
    p3 = newp; Point(p3) = {XC+th, YC,    0, LcTapes};
    p4 = newp; Point(p4) = {XC,    YC,    0, LcTapes};
    
    p1p2 = newl; Line(p1p2) = {p1, p2};
    p2p3 = newl; Line(p2p3) = {p2, p3};
    p3p4 = newl; Line(p3p4) = {p3, p4};
    p4p1 = newl; Line(p4p1) = {p4, p1};
    lll = news; Line Loop(lll) = {p1p2, p2p3, p3p4, p4p1};
    s = news; Plane Surface(s) = {lll};

    ll7[i] = lll;
    tapes7[i]=s;
EndFor
Physical Surface("tape_70") = {tapes7[0]};
Physical Surface("tape_71") = {tapes7[1]};
Physical Surface("tape_72") = {tapes7[2]};
Physical Surface("tape_73") = {tapes7[3]};
Physical Surface("tape_74") = {tapes7[4]};
Physical Surface("tape_75") = {tapes7[5]};
Physical Surface("tape_76") = {tapes7[6]};
Physical Surface("tape_77") = {tapes7[7]};
Physical Surface("tape_78") = {tapes7[8]};
Physical Surface("tape_79") = {tapes7[9]};

ll8={0,0,0,0,0,0,0,0,0,0};
tapes8={0,0,0,0,0,0,0,0,0,0};
// Conductor
For i In {0:ns-1}
    XC=x0+8*(wg+(sg+th)*Floor(9/2))+(sg+th)*(Floor(i/2)); 
    YC=y0+(rg+sw)*(i%2);
    p1 = newp; Point(p1) = {XC,    YC+sw, 0, LcTapes};
    p2 = newp; Point(p2) = {XC+th, YC+sw, 0, LcTapes};
    p3 = newp; Point(p3) = {XC+th, YC,    0, LcTapes};
    p4 = newp; Point(p4) = {XC,    YC,    0, LcTapes};
    
    p1p2 = newl; Line(p1p2) = {p1, p2};
    p2p3 = newl; Line(p2p3) = {p2, p3};
    p3p4 = newl; Line(p3p4) = {p3, p4};
    p4p1 = newl; Line(p4p1) = {p4, p1};
    lll = news; Line Loop(lll) = {p1p2, p2p3, p3p4, p4p1};
    s = news; Plane Surface(s) = {lll};

    ll8[i] = lll;
    tapes8[i]=s;
EndFor
Physical Surface("tape_80") = {tapes8[0]};
Physical Surface("tape_81") = {tapes8[1]};
Physical Surface("tape_82") = {tapes8[2]};
Physical Surface("tape_83") = {tapes8[3]};
Physical Surface("tape_84") = {tapes8[4]};
Physical Surface("tape_85") = {tapes8[5]};
Physical Surface("tape_86") = {tapes8[6]};
Physical Surface("tape_87") = {tapes8[7]};
Physical Surface("tape_88") = {tapes8[8]};
Physical Surface("tape_89") = {tapes8[9]};

// ll9={0,0,0,0,0,0,0,0,0,0};
// tapes9={0,0,0,0,0,0,0,0,0,0};
// // Conductor
// For i In {0:ns-1}
//     XC=x0+9*(wg+(sg+th)*Floor(9/2))+(sg+th)*(Floor(i/2)); 
//     YC=y0+(rg+sw)*(i%2);
//     p1 = newp; Point(p1) = {XC,    YC+sw, 0, LcTapes};
//     p2 = newp; Point(p2) = {XC+th, YC+sw, 0, LcTapes};
//     p3 = newp; Point(p3) = {XC+th, YC,    0, LcTapes};
//     p4 = newp; Point(p4) = {XC,    YC,    0, LcTapes};
    
//     p1p2 = newl; Line(p1p2) = {p1, p2};
//     p2p3 = newl; Line(p2p3) = {p2, p3};
//     p3p4 = newl; Line(p3p4) = {p3, p4};
//     p4p1 = newl; Line(p4p1) = {p4, p1};
//     lll = news; Line Loop(lll) = {p1p2, p2p3, p3p4, p4p1};
//     s = news; Plane Surface(s) = {lll};

//     ll9[i] = lll;
//     tapes9[i]=s;
// EndFor
// Physical Surface("tape_90") = {tapes9[0]};
// Physical Surface("tape_91") = {tapes9[1]};
// Physical Surface("tape_92") = {tapes9[2]};
// Physical Surface("tape_93") = {tapes9[3]};
// Physical Surface("tape_94") = {tapes9[4]};
// Physical Surface("tape_95") = {tapes9[5]};
// Physical Surface("tape_96") = {tapes9[6]};
// Physical Surface("tape_97") = {tapes9[7]};
// Physical Surface("tape_98") = {tapes9[8]};
// Physical Surface("tape_99") = {tapes9[9]};

AIR = news; Plane Surface(AIR) = {ll123,-ll0[],-ll1[],-ll2[],-ll3[],-ll4[],-ll5[],-ll6[],-ll7[],-ll8[]};



Physical Surface("Air") = {AIR};
// Physical Surface("tape_0") = {tapes[0]};
// Physical Surface("tape_1") = {tapes[1]};
// Physical Surface("tape_2") = {tapes[2]};
// Physical Surface("tape_3") = {tapes[3]};
// Physical Surface("tape_4") = {tapes[4]};
// Physical Surface("tape_5") = {tapes[5]};
// Physical Surface("tape_6") = {tapes[6]};
// Physical Surface("tape_7") = {tapes[7]};
// Physical Surface("tape_8") = {tapes[8]};
// Physical Surface("tape_9") = {tapes[9]};
// Physical Surface("tape_10") = {tapes[10]};
// Physical Surface("tape_11") = {tapes[11]};
// Physical Surface("tape_12") = {tapes[12]};
// Physical Surface("tape_13") = {tapes[13]};
// Physical Surface("tape_14") = {tapes[14]};
// Physical Surface("tape_15") = {tapes[15]};
// Physical Surface("tape_16") = {tapes[16]};
// Physical Surface("tape_17") = {tapes[17]};
// Physical Surface("tape_18") = {tapes[18]};
// Physical Surface("tape_19") = {tapes[19]};

Physical Line("Exterior_boundary") = {b1b2,b2b3,b3b4};
Physical Line("ZAxis") = {b4p0,p0b1};