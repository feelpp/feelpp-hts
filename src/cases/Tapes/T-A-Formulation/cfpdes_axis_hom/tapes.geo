h=1e-3;
LcTapes=h*0.1;
LcAir=h*10;
LcInf=h*20;
// ---- Geometry parameters ----
DefineConstant[
    changeGeometry = {0, Choices{0,1}, Name "Input/1Geometry/1Show geometry?"},
    R_inf = {40e-2, Visible changeGeometry, Name "Input/1Geometry/Outer radius (m)"}, // Outer shell radius [m]
    R_air = {0.9*R_inf, Max R_inf, Visible changeGeometry, Name "Input/1Geometry/Inner radius (m)"}, // Inner shell radius [m]
    W_tapes = {1e-6, Max R_air/2, Visible changeGeometry, Name "Input/1Geometry/Tapes width (m)"}, 
    H_tapes = {12e-3, Max R_air/2, Visible changeGeometry, Name "Input/1Geometry/Tapes height (m)"}, 
    cel_w = {250e-6}, 
    n_tape = {20}
];


// ---- Constant definition for regions ----
AIR = 1000;
AIR_OUT = 2000;
SURF_SHELL = 3000;
CUT = 9000;
ARBITRARY_POINT = 11000;
SURF_SYM = 13000;
SURF_SYM_MAT = 13500;
SURF_OUT = 14000;
MATERIAL = 23000;
BND_MATERIAL_BOT = 24000;
BND_MATERIAL_TOP = 25000;
BND_MATERIAL_SIDE = 26000;
        
    



Point(123) = {0, 0, 0, LcAir};
Point(1) = {0, -R_air, 0, LcAir};
Point(2) = {0, -R_inf, 0, LcInf};
Point(3) = {R_air, 0, 0, LcAir};
Point(4) = {R_inf, 0, 0, LcInf};
Point(5) = {0, R_air, 0, LcAir};
Point(6) = {0, R_inf, 0, LcInf};

Circle(1) = {1, 123, 3};
Circle(2) = {2, 123, 4};
Circle(3) = {3, 123, 5};
Circle(4) = {4, 123, 6};
Line(5) = {5, 6};
Line(6) = {1, 2};
Line(7) = {1, 123};
Line(8) = {123,5};

Point(10) = {10e-2-cel_w/2, -H_tapes/2, 0, LcTapes};
Point(11) = {10e-2-cel_w/2, H_tapes/2, 0, LcTapes};
// Point(20) = {10e-2+cel_w/2, -H_tapes/2, 0, LcTapes};
// Point(21) = {10e-2+cel_w/2, H_tapes/2, 0, LcTapes};
// Point(30) = {10e-2+3*cel_w/2, -H_tapes/2, 0, LcTapes};
// Point(31) = {10e-2+3*cel_w/2, H_tapes/2, 0, LcTapes};
// Point(40) = {10e-2+7*cel_w/2, -H_tapes/2, 0, LcTapes};
// Point(41) = {10e-2+7*cel_w/2, H_tapes/2, 0, LcTapes};
// Point(50) = {10e-2+15*cel_w/2, -H_tapes/2, 0, LcTapes};
// Point(51) = {10e-2+15*cel_w/2, H_tapes/2, 0, LcTapes};
// Point(60) = {10e-2+23*cel_w/2, -H_tapes/2, 0, LcTapes};
// Point(61) = {10e-2+23*cel_w/2, H_tapes/2, 0, LcTapes};
// Point(70) = {10e-2+31*cel_w/2, -H_tapes/2, 0, LcTapes};
// Point(71) = {10e-2+31*cel_w/2, H_tapes/2, 0, LcTapes};
// Point(80) = {10e-2+35*cel_w/2, -H_tapes/2, 0, LcTapes};
// Point(81) = {10e-2+35*cel_w/2, H_tapes/2, 0, LcTapes};
// Point(90) = {10e-2+37*cel_w/2, -H_tapes/2, 0, LcTapes};
// Point(91) = {10e-2+37*cel_w/2, H_tapes/2, 0, LcTapes};
Point(100) = {10e-2+39*cel_w/2, -H_tapes/2, 0, LcTapes};
Point(101) = {10e-2+39*cel_w/2, H_tapes/2, 0, LcTapes};

Line(10) = {10,11};
// Line(11) = {10,20};
// Line(12) = {11,21};
// Line(20) = {20,21};
// Line(21) = {20,30};
// Line(22) = {21,31};
// Line(30) = {30,31};
// Line(31) = {30,40};
// Line(32) = {31,41};
// Line(40) = {40,41};
// Line(41) = {40,50};
// Line(42) = {41,51};
// Line(50) = {50,51};
// Line(51) = {50,60};
// Line(52) = {51,61};
// Line(60) = {60,61};
// Line(61) = {60,70};
// Line(62) = {61,71};
// Line(70) = {70,71};
// Line(71) = {70,80};
// Line(72) = {71,81};
// Line(80) = {80,81};
// Line(81) = {80,90};
// Line(82) = {81,91};
// Line(90) = {90,91};
// Line(91) = {90,100};
// Line(92) = {91,101};
Line(100) = {100,101};

Line(101)={10,100};
Line(102)={11,101};


Line Loop(300) = {6, 2, 4, -5, -3, -1}; // Outer shell
Plane Surface(400) = {300};
Line Loop(301) = {1, 3, -8, -7}; // Air
// Plane Surface(401) = {301};

// Line Loop(500) = {10,12,22,32,42,52,62,72,82,92,-100,-91,-81,-71,-61,-51,-41,-31,-21,-11};
Line Loop(500) = {10,102,-100,-101};

Plane Surface(401) = {301,500};
Plane Surface(501) = {500};

// Line Loop(510) = {10,12,-20,-11};
// Plane Surface(500) = {510};
// Line Loop(520) = {20,22,-30,-21};
// Plane Surface(501) = {520};
// Line Loop(530) = {30,32,-40,-31};
// Plane Surface(502) = {530};
// Line Loop(540) = {40,42,-50,-41};
// Plane Surface(503) = {540};
// Line Loop(550) = {50,52,-60,-51};
// Plane Surface(504) = {550};
// Line Loop(560) = {60,62,-70,-61};
// Plane Surface(505) = {560};
// Line Loop(570) = {70,72,-80,-71};
// Plane Surface(506) = {570};
// Line Loop(580) = {80,82,-90,-81};
// Plane Surface(507) = {580};
// Line Loop(590) = {90,92,-100,-91};
// Plane Surface(508) = {590};

// Plane Surface(401) = {301,510,520,530,540,550,560,570,580,590};

Physical Surface("Air", AIR) = {401};
Physical Surface("Spherical_shell", AIR_OUT) = {400};
Physical Surface("Bulks", MATERIAL) = {501};
// Physical Surface("Bulks", MATERIAL) = {500,501,502,503,504,505,506,507,508};
Physical Line("Exterior_boundary", SURF_OUT) = {2, 4};
Physical Line("Symmetry_line", SURF_SYM) = {-6, 7, 8, 5};
Physical Line("Sides", BND_MATERIAL_SIDE) = {10,100};
Physical Line("Top", BND_MATERIAL_TOP) = {102};
Physical Line("Bottom", BND_MATERIAL_BOT) = {101};
// Physical Line("Top", BND_MATERIAL_TOP) = {12,22,32,42,52,62,72,82,92};
// Physical Line("Bottom", BND_MATERIAL_BOT) = {11,21,31,41,51,61,71,81,91};
