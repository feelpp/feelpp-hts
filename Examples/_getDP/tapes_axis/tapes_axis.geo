// Include cross data
Include "tapes_axis_data.pro";

// Interactive settings
R = H_tape/2; // Radius
// Mesh size
DefineConstant [meshFactor = {10, Name "Input/2Mesh/2Coarsening factor at infinity (-)"}];
DefineConstant [LcTape = R/numElementsTape]; // Mesh size in cylinder [m]
DefineConstant [LcLayer = LcTape]; // Mesh size in the region close to the cylinder [m]
DefineConstant [LcAir = 10*meshFactor*LcTape]; // Mesh size in air shell [m]
DefineConstant [LcInf = 15*meshFactor*LcTape]; // Mesh size in external air shell [m]
DefineConstant [transfiniteQuadrangular = {0, Choices{0,1}, Name "Input/2Mesh/3Use regular quadrangular mesh?"}];
// Shells definition
Point(1234) = {0, 0, 0, LcAir};
Point(1) = {0, -R_air, 0, LcAir};
Point(2) = {0, -R_inf, 0, LcInf};
Point(3) = {R_air, 0, 0, LcAir};
Point(4) = {R_inf, 0, 0, LcInf};
Point(5) = {0, R_air, 0, LcAir};
Point(6) = {0, R_inf, 0, LcInf};

Circle(1) = {1, 1234, 3};
Circle(2) = {2, 1234, 4};
Circle(3) = {3, 1234, 5};
Circle(4) = {4, 1234, 6};
Line(5) = {5, 6};
Line(6) = {1, 2};
Line(7) = {1, 5};

// Point(100) = {3e-2, -H_tape/2, 0, LcTape};
// Point(101) = {3e-2, H_tape/2, 0, LcTape};
// Line(100) = {100, 101};
// Transfinite Line(100) = 2*numElementsTape Using Progression 1;
For k In {0:39:1}
    Printf("k = %f", k );
    Point(100+ k*100) = {3e-2+k*(sep+W_tape), -H_tape/2, 0, LcTape};
    Point(101+ k*100) = {3e-2+k*(sep+W_tape), H_tape/2, 0, LcTape};
    Line(100+ k*100) = {100+ k*100, 101+ k*100};
    Transfinite Line(100+ k*100) = 2*numElementsTape Using Progression 1;
EndFor


// Physical entities
Line Loop(30) = {6, 2, 4, -5, -3, -1}; // Outer shell
Plane Surface(40) = {30};
Line Loop(31) = {1,3,-7}; // Air
Plane Surface(41) = {31};
// Curve{100} In Surface{41};

For k In {0:40-1:1}
    Curve{100+ k*100} In Surface{41};
EndFor

Physical Surface("Air", AIR) = {41};
Physical Surface("Spherical shell", AIR_OUT) = {40};
Physical Line("Conducting domain", MATERIAL) = {100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2100,2200,2300,2400,2500,2600,2700,2800,2900,3000,3100,3200,3300,3400,3500,3600,3700,3800,3900,4000};
Physical Line("Conducting domain boundary", BND_MATERIAL) ={100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2100,2200,2300,2400,2500,2600,2700,2800,2900,3000,3100,3200,3300,3400,3500,3600,3700,3800,3900,4000};
Physical Point("Lower edge", EDGE_1) = {100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2100,2200,2300,2400,2500,2600,2700,2800,2900,3000,3100,3200,3300,3400,3500,3600,3700,3800,3900,4000};
Physical Point("Upper edge", EDGE_2) = {101,201,301,401,501,601,701,801,901,1001,1101,1201,1301,1401,1501,1601,1701,1801,1901,2001,2101,2201,2301,2401,2501,2601,2701,2801,2901,3001,3101,3201,3301,3401,3501,3601,3701,3801,3901,4001};
// Physical Line("Conducting domain", MATERIAL) = {100};
// Physical Line("Conducting domain boundary", BND_MATERIAL) ={100};
// Physical Point("Lower edge", EDGE_1) = {100};
// Physical Point("Upper edge", EDGE_2) = {101};
Physical Line("Exterior boundary", SURF_OUT) = {2, 4};
Physical Line("Symmetry line", SURF_SYM) = {-6,7,5};
Physical Line("Shells common line", SURF_SHELL) = {1, 3};
Physical Point("Arbitrary Point", ARBITRARY_POINT) = {4};

// Empty regions
Physical Point("Symmetry line material", SURF_SYM_MAT) = {};
Physical Line("Cut", CUT) = {};
Physical Line("Positive side of bnds", BND_MATERIAL_SIDE) = {};