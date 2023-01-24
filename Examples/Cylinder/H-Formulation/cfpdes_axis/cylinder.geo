// ---- Geometry parameters ----
DefineConstant[
    changeGeometry = {0, Choices{0,1}, Name "Input/1Geometry/1Show geometry?"},
    R_inf = {0.1, Visible changeGeometry, Name "Input/1Geometry/Outer radius (m)"}, // Outer shell radius [m]
    R_air = {0.07, Max R_inf, Visible changeGeometry, Name "Input/1Geometry/Inner radius (m)"}, // Inner shell radius [m]
    W = {0.025, Max R_air/2, Visible changeGeometry, Name "Input/1Geometry/Cylinder diameter (m)"}, // Diameter of the cylinder [m]
    H_cylinder = {0.01, Max R_air/2, Visible changeGeometry, Name "Input/1Geometry/Cylinder height (m)"}, // Height of the cylinder [m]
    meshLayerWidth = {0.005} // Width of the control mesh layer around the cylinder
    ];
    // ---- Mesh parameters ----
    DefineConstant [meshMult = {0.6, Name "Input/2Mesh/1Mesh size multiplier (-)"}]; // Multiplier [-] of a default mesh size distribution
    
    // ---- Formulation definitions (dummy values) ----
    h_formulation = 2;
    a_formulation = 6;
    coupled_formulation = 5;
    
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
    BND_MATERIAL = 25000;
    BND_MATERIAL_SIDE = 26000;
        
    
    // Interactive settings
    R = W/2; // Radius
    // Mesh size
    DefineConstant [meshFactor = {10, Name "Input/2Mesh/2Coarsening factor at infinity (-)"}];
    DefineConstant [LcCyl = meshMult*0.0003]; // Mesh size in cylinder [m]
    DefineConstant [LcLayer = LcCyl]; // Mesh size in the region close to the cylinder [m]
    DefineConstant [LcAir = meshFactor*LcCyl]; // Mesh size in air shell [m]
    DefineConstant [LcInf = meshFactor*LcCyl]; // Mesh size in external air shell [m]
    DefineConstant [transfiniteQuadrangular = {0, Choices{0,1}, Name "Input/2Mesh/3Regular quadrangular mesh?"}];
    // Shells definition
    Point(100) = {0, 0, 0, LcCyl};
    Point(1) = {0, -R_air, 0, LcAir};
    Point(2) = {0, -R_inf, 0, LcInf};
    Point(3) = {R_air, 0, 0, LcAir};
    Point(4) = {R_inf, 0, 0, LcInf};
    Point(5) = {0, R_air, 0, LcAir};
    Point(6) = {0, R_inf, 0, LcInf};
    
    Circle(1) = {1, 100, 3};
    Circle(2) = {2, 100, 4};
    Circle(3) = {3, 100, 5};
    Circle(4) = {4, 100, 6};
    Line(5) = {5, 6};
    Line(6) = {1, 2};
    
    // Cylinder definition
    Point(11) = {0, -H_cylinder/2, 0, LcCyl};
    Point(12) = {R, -H_cylinder/2, 0, LcCyl};
    Point(13) = {R, H_cylinder/2, 0, LcCyl};
    Point(14) = {0, H_cylinder/2, 0, LcCyl};
    
    Point(15) = {0, -H_cylinder/2-meshLayerWidth, 0, LcLayer};
    Point(16) = {R+meshLayerWidth, -H_cylinder/2-meshLayerWidth, 0, LcLayer};
    Point(17) = {R+meshLayerWidth, H_cylinder/2+meshLayerWidth, 0, LcLayer};
    Point(18) = {0, H_cylinder/2+meshLayerWidth, 0, LcLayer};
    
    Point(50) = {R, -H_cylinder/2-meshLayerWidth, 0, LcLayer};
    Point(51) = {R+meshLayerWidth, -H_cylinder/2, 0, LcLayer};
    Point(52) = {R+meshLayerWidth, H_cylinder/2, 0, LcLayer};
    Point(53) = {R, H_cylinder/2+meshLayerWidth, 0, LcLayer};
    
    
    
    Line(7) = {18, 5};
    Line(8) = {14, 18};
    Line(9) = {14, 100};
    Line(10) = {100, 11};
    Line(11) = {11, 15};
    Line(12) = {15, 1};
    Line(13) = {11, 12};
    Line(14) = {12, 13};
    Line(15) = {13, 14};
    
    Line(100) = {15, 50};
    Line(101) = {50, 16};
    Line(102) = {16, 51};
    Line(103) = {51, 52};
    Line(104) = {52, 17};
    Line(105) = {17, 53};
    Line(106) = {53, 18};
    Line(107) = {53, 13};
    Line(108) = {13, 52};
    Line(109) = {51, 12};
    Line(110) = {12, 50};
    
    
    Line(8765) = {14, 11};
    
    // Physical entities
    Line Loop(30) = {6, 2, 4, -5, -3, -1}; // Outer shell
    Plane Surface(40) = {30};
    Line Loop(31) = {12, 1, 3, -7, -106, -105, -104, -103, -102, -101, -100}; // Air
    Plane Surface(41) = {31};
    
    Line Loop(61) = {11, 100, -110, -13};
    Line Loop(62) = {110, 101, 102, 109};
    Line Loop(63) = {103, -108, -14, -109};
    Line Loop(64) = {108, 104, 105, 107};
    Line Loop(65) = {106, -8, -15, -107}; // Refined zone close to cylinder
    Plane Surface(52) = {61};
    Plane Surface(53) = {62};
    Plane Surface(54) = {63};
    Plane Surface(55) = {64};
    Plane Surface(56) = {65};
    Line Loop(33) = {8765, 13, 14, 15}; // Cylinder
    Plane Surface(43) = {33};
    
    If(transfiniteQuadrangular)
        Transfinite Surface(52);
        Recombine Surface(52);
        Transfinite Surface(53);
        Recombine Surface(53);
        Transfinite Surface(54);
        Recombine Surface(54);
        Transfinite Surface(55);
        Recombine Surface(55);
        Transfinite Surface(56);
        Recombine Surface(56);
    
        Transfinite Surface(43);
        Recombine Surface(43);
    EndIf
    
    Physical Surface("Air", AIR) = {41, 52, 53, 54, 55, 56};
    Physical Surface("Spherical_shell", AIR_OUT) = {40};
    Physical Surface("Cylinder", MATERIAL) = {43};
    Physical Line("Exterior_boundary", SURF_OUT) = {2, 4};
    Physical Line("Symmetry_line", SURF_SYM) = {-5, -7, -8, 8765, 11, 12, 6};
    // Physical Line("Conducting_domain_boundary", BND_MATERIAL) = {13, 14, 15};
    // Physical Line("Shells_common_line", SURF_SHELL) = {1, 3};
    // Physical Line("Symmetry_line_material", SURF_SYM_MAT) = {8765};
    // Physical Line("Cut", CUT) = {8, 7, 5};
    // Physical Line("Positive_side_of_bnds", BND_MATERIAL_SIDE) = {15};
    
    
    // Some colors
    Color SkyBlue {Surface{40, 41, 52, 53, 54, 55, 56};} // Air + Air inf
    Color Purple {Surface{43};} // Cylinder
    
    linair[]  = CombinedBoundary{Surface{41, 52, 53, 54, 55, 56, 40};};
    lincyl[]  = CombinedBoundary{Surface{43};};
    
    Hide { Point{ Point '*' }; }
    Hide { Line{ Line '*' }; }
    Show { Line{ linair[] }; }
    Show { Line{ lincyl[] }; }
    
    
    // End
    //+
Hide "*";
//+
Show {
  Curve{2}; Curve{4}; Curve{5}; Curve{6}; Curve{7}; Curve{8}; Curve{11}; Curve{12}; Curve{13}; Curve{14}; Curve{15}; Curve{8765}; Surface{40}; Surface{41}; Surface{43}; Surface{52}; Surface{53}; Surface{54}; Surface{55}; Surface{56}; 
}
