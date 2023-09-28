//-----------------------------------------------------------------------------
// Parameters

h = 1e-2;
rint = 75e-3;  // m
rext = 100.2e-3; // m 
z1 = 25e-3;  // m

rinfty = 5*(rext+rint); // m

//-----------------------------------------------------------------------------
// Definition of points

// Origin
Point(0) = {0,0,0,h};

// Conductor
Point(1) = {rint, -z1, 0, 0.5*h};
Point(2) = {rext, -z1, 0, 0.5*h};
Point(3) = {rext, z1, 0, 0.5*h};
Point(4) = {rint, z1, 0, 0.5*h};

// Air
Point(5) = {0, -rinfty, 0, 20*h};
Point(6) = {0, -3*z1, 0, 0.5*h};
Point(7) = {0, 3*z1, 0, 0.5*h};
Point(8) = {0, rinfty, 0, 20*h};

Point(9) = {0, -1.1*rinfty, 0, 30*h};
Point(10) = {0, 1.1*rinfty, 0, 30*h};

//-----------------------------------------------------------------------------
// Definition of line

// Conductor
Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};

// Air
Circle(5) = {5, 0, 8};
Line(6) = {8, 7};
Line(7) = {7, 6};
Line(8) = {6, 5};

Circle(9) = {9, 0, 10};
Line(10) = {8, 10};
Line(11) = {5, 9};

//-----------------------------------------------------------------------------
// Definition of surface

// Conductor
Curve Loop(1) = {1, 2, 3, 4};
Plane Surface(30) = {1};

// Air
Curve Loop(2) = {5, 6, 7, 8};
Plane Surface(20) = {2, 1};

Curve Loop(3) = {9, -10, -5, 11};
Plane Surface(21) = {3};

//-----------------------------------------------------------------------------
// Definition of physical groups

// Conductor
Physical Curve("Bottom") = {1};
Physical Curve("Rigth") = {2};
Physical Curve("Upper") = {3};
Physical Curve("Left") = {4};
Physical Surface("Conductor") = {30};

// Air
Physical Curve("Infty") = {5};
Physical Curve("ZAxis") = {-11, 6, 7, 8, 10};
Physical Surface("Air") = {20};
Physical Surface("Air_out") = {21};