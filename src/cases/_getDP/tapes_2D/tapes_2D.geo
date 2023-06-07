Include "tapes_2D_data.pro";

nb_Tapes = 15;


// Mesh size
R = W_tape/2; // Radius
DefineConstant [LcTape = R/numElementsTape]; // Mesh size in cylinder [m]
DefineConstant [LcLayer = LcTape*2]; // Mesh size in the region close to the cylinder [m]
DefineConstant [LcAir = meshMult*0.001]; // Mesh size in air shell [m]
DefineConstant [LcInf = meshMult*0.001]; // Mesh size in external air shell [m]

Point(2) = {-7*W_tape, -9.5*(0.21*14)*1e-3, 0, LcInf};
Point(4) = {8*W_tape, -9.5*(0.21*14)*1e-3, 0, LcInf};
Point(6) = {8*W_tape, 10.5*(0.21*14)*1e-3, 0, LcInf};
Point(8) = {-7*W_tape, 10.5*(0.21*14)*1e-3, 0, LcInf};

Point(1) = {0.5*W_tape, -9.5*(0.21*14)*1e-3, 0, LcInf};

Line(1) = {2, 8};
Line(2) = {8, 6};
Line(3) = {6, 4};
Line(4) = {4, 2};

For k In {0:nb_Tapes-1:1}
    // Printf("k = %f", k );
    Point(10 + k*10) = {0, k*0.21*1e-3, 0, LcTape};
    Point(11+ k*10) = {W_tape, k*0.21*1e-3, 0, LcTape};
    Line(10+ k*10) = {10+ k*10, 11+ k*10};
    Transfinite Line(10+ k*10) = 2*numElementsTape Using Progression 1;
EndFor

Line Loop(1234) = {1, 2, 3, 4}; // Outer boundary
Plane Surface(2) = {1234};
For k In {0:nb_Tapes-1:1}
    Curve{10+ k*10} In Surface{2};
EndFor

Physical Surface("Air", AIR) = {2};
Physical Line("Exterior boundary", SURF_OUT) = {1, 2, 3, 4};
Physical Line("Conducting domain", MATERIAL) = {10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150};
Physical Line("Conducting domain boundary", BND_MATERIAL) = {10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150};
Physical Point("Left edge", EDGE_1) = {10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150};
Physical Point("Right edge", EDGE_2) = {11, 21, 31, 41, 51, 61, 71, 81, 91, 101, 111, 121, 131, 141, 151};
Physical Point("Arbitrary Point", ARBITRARY_POINT) = {1};
// Empty regions
Physical Surface("Spherical shell", AIR_OUT) = {};
Physical Line("Symmetry line", SURF_SYM) = {};
Physical Line("Shells common line", SURF_SHELL) = {};
Physical Line("Symmetry line material", SURF_SYM_MAT) = {};
Physical Line("Cut", CUT) = {};
Physical Line("Positive side of bnds", BND_MATERIAL_SIDE) = {};
