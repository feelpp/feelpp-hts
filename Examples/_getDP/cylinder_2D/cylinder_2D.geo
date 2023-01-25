h = 1e-3;
R=0.001;
ratio=1;
S=10*R*Sqrt(ratio);


//-----------------------------------------------------------------------------
// Definition of points

// Origin
Point(0) = {0,0,0,h};

// Conductor
Point(1) = {Sqrt(ratio)*R, 0, 0, 0.05*h};
Point(2) = {0, R/Sqrt(ratio), 0, 0.05*h};
Point(3) = {-Sqrt(ratio)*R, 0, 0, 0.05*h};
Point(4) = {0, -R/Sqrt(ratio), 0, 0.05*h};

// Air
Point(5) = {S, 0, 0, 0.5*h};
Point(6) = {-S, 0, 0, 0.5*h};

//-----------------------------------------------------------------------------
// Definition of line

// Conductor
Ellipse(1) = {1, 0, 5, 2};
Ellipse(2) = {2, 0, 5, 3};
Ellipse(3) = {3, 0, 5, 4};
Ellipse(4) = {4, 0, 5, 1};

// Air
Circle(5) = {5, 0, 6};
Circle(6) = {6, 0, 5};


//-----------------------------------------------------------------------------
// Definition of surface

// Conductor
Curve Loop(1) = {1, 2, 3, 4};
Plane Surface(1) = {1};

// // Air
Curve Loop(2) = {5,6};
Plane Surface(2) = {2,1};

//-----------------------------------------------------------------------------
// Definition of physical groups

// Conductor
Physical Curve("Bound_super",25000) = {1,2,3,4};
Physical Surface("Conductor",23000) = {1};

// Air
Physical Curve("Infty",14000) = {5,6};
Physical Surface("Air",1000) = {2};


