// Preset choice of formulation
DefineConstant[preset = {4, Highlight "Blue",
  Choices{
    1="h-formulation",
    2="a-formulation (large steps)",
    3="a-formulation (small steps)",
    4="t-a-formulation"},
  Name "Input/5Method/0Preset formulation" },
  expMode = {0, Choices{0,1}, Name "Input/5Method/1Allow changes?"}];

// ---- Geometry parameters ----
DefineConstant[
changeGeometry = {0, Choices{0,1}, Name "Input/1Geometry/1Show geometry?"},
R_inf = {0.08, Visible changeGeometry, Name "Input/1Geometry/Outer radius (m)"}, // Outer shell radius [m]
R_air = {0.06, Max R_inf, Visible changeGeometry, Name "Input/1Geometry/Inner radius (m)"}, // Inner shell radius [m]
H_tape = {4e-3, Max R_air/2, Visible changeGeometry, Name "Input/1Geometry/Tapes height(m)"}, // Width of the tape [m]
W_tape = {1e-6, Max R_air/2, Visible changeGeometry, Name "Input/1Geometry/Tapes Width(m)"}, // Height of the tape [m]
W = {W_tape}, // Width of the tape [m]
sep = {0.15e-3, Visible changeGeometry, Name "Input/1Geometry/separation between tapes(m)"}, 
meshLayerWidthTape = {0.001} // Width of the control mesh layer around the cylinder
];

// ---- Mesh parameters ----
DefineConstant [meshMult = {3, Name "Input/2Mesh/1Mesh size multiplier (-)"}]; // Multiplier [-] of a default mesh size distribution
DefineConstant [elementMult = 5];

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
