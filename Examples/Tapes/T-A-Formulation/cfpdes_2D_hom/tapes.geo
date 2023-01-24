
// ---- Geometry parameters ----
R_inf = 0.06;
R_air = 0.04;
W_tape = 4e-3;
H_tape = 1e-6;
meshLayerWidthTape = 0.001;

// ---- Mesh parameters ----
meshMult = 3;
elementMult = 5;

numElementsTape = Floor[elementMult*0.1*400/meshMult];

// ---- Constant definition for regions ----
AIR = 1000;
AIR_OUT = 2000;
SURF_SHELL = 3000;
CUT = 9000;
ARBITRARY_POINT = 11000;
EDGE_1 = 11001;
EDGE_2 = 11002;
SURF_SYM = 13000;
SURF_SYM_MAT = 13500;
SURF_OUT = 14000;
MATERIAL = 23000;
BND_MATERIAL = 25000;
BND_MATERIAL_SIDE = 26000;


nb_Tapes = 15;


// Mesh size
cell=0.21e-3;
R = W_tape/2; // Radius
DefineConstant [LcTape = R/numElementsTape]; // Mesh size in cylinder [m]
DefineConstant [LcLayer = LcTape*2]; // Mesh size in the region close to the cylinder [m]
DefineConstant [LcAir = meshMult*0.001]; // Mesh size in air shell [m]
DefineConstant [LcInf = meshMult*0.001]; // Mesh size in external air shell [m]

Point(2) = {-7*W_tape, -9.5*(0.21*14)*1e-3, 0, LcInf};
Point(4) = {8*W_tape, -9.5*(0.21*14)*1e-3, 0, LcInf};
Point(6) = {8*W_tape, 10.5*(0.21*14)*1e-3, 0, LcInf};
Point(8) = {-7*W_tape, 10.5*(0.21*14)*1e-3, 0, LcInf};


Line(1) = {2, 8};
Line(2) = {8, 6};
Line(3) = {6, 4};
Line(4) = {4, 2};

Point(10 ) = {0, -cell/2, 0, LcTape};
Point(11) = {W_tape, -cell/2, 0, LcTape};
Line(10) = {10, 11};

Point(10 + 14*10) = {0, -cell/2+15*cell, 0, LcTape};
Point(11+ 14*10) = {W_tape, -cell/2+15*cell, 0, LcTape};
Line(10+ 14*10) = {10+ 14*10, 11+ 14*10};

Line(12) = {10,150};
Line(13) = {11,151};
// For k In {0:nb_Tapes-1:1}
//     // Printf("k = %f", k );
//     Point(10 + k*10) = {0, k*0.21*1e-3, 0, LcTape};
//     Point(11+ k*10) = {W_tape, k*0.21*1e-3, 0, LcTape};
//     Line(10+ k*10) = {10+ k*10, 11+ k*10};
//     Transfinite Line(10+ k*10) = 2*numElementsTape Using Progression 1;
// EndFor

Line Loop(1234) = {1, 2, 3, 4}; // Outer boundary
Line Loop(2345) = {10,13,-150,-12};
Plane Surface(2) = {1234,2345};
Plane Surface(3) = {2345};
// For k In {0:nb_Tapes-1:1}
//     Curve{10+ k*10} In Surface{2};
// EndFor

Physical Surface("Air", AIR) = {2};
Physical Surface("Conductor", MATERIAL) = {3};
Physical Line("Exterior_boundary", SURF_OUT) = {1, 2, 3, 4};
Physical Line("Sides", BND_MATERIAL) = {10,150};
Physical Line("Bottom", EDGE_1) = {12};
Physical Line("Top", EDGE_2) = {13};
// Physical Point("Arbitrary Point", ARBITRARY_POINT) = {1};
// Empty regions
// Physical Surface("Spherical shell", AIR_OUT) = {};
// Physical Line("Symmetry line", SURF_SYM) = {};
// Physical Line("Shells common line", SURF_SHELL) = {};
// Physical Line("Symmetry line material", SURF_SYM_MAT) = {};
// Physical Line("Cut", CUT) = {};
// Physical Line("Positive side of bnds", BND_MATERIAL_SIDE) = {};
