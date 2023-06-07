// ---- Geometry parameters ----
DefineConstant[
changeGeometry = {0, Choices{0,1}, Name "Input/1Geometry/1Show geometry?"},
R_inf = {0.01, Visible changeGeometry, Name "Input/1Geometry/Outer radius (m)"}, // Outer shell radius [m]
R_air = {0.007, Max R_inf, Visible changeGeometry, Name "Input/1Geometry/Inner radius (m)"}, // Inner shell radius [m]
W = {0.002, Max R_air/2, Visible changeGeometry, Name "Input/1Geometry/Cylinder diameter (m)"}, // Diameter of the cylinder [m]
H_cylinder = {0.002, Max R_air/2, Visible changeGeometry, Name "Input/1Geometry/Cylinder height (m)"}, // Height of the cylinder [m]
meshLayerWidth = {0.005} // Width of the control mesh layer around the cylinder
];
// ---- Mesh parameters ----
DefineConstant [meshMult = {6, Name "Input/2Mesh/1Mesh size multiplier (-)"}]; // Multiplier [-] of a default mesh size distribution

// ---- Formulation definitions (dummy values) ----
h_formulation = 2;
a_formulation = 6;
coupled_formulation = 5;

// ---- Constant definition for regions ----
AIR = 1000;
// AIR_OUT = 2000;
SURF_SHELL = 3000;
CUT = 9000;
ARBITRARY_POINT = 11000;
// SURF_SYM = 13000;
// SURF_SYM_MAT = 13500;
SURF_OUT = 14000;
MATERIAL = 23000;
BND_MATERIAL = 25000;
BND_MATERIAL_SIDE = 26000;


Include "../lib_cylinder/commonInformation.pro";

Group {
    // Preset choice of formulation (for onelab interface)
    DefineConstant[preset = {2, Highlight "Blue",
      Choices{
        1="h-formulation",
        2="a-formulation (large steps)",
        3="a-formulation (small steps)"},
      Name "Input/5Method/0Preset formulation" },
      expMode = {0, Choices{0,1}, Name "Input/5Method/1Allow changes?"}];
    // Output choice
    DefineConstant[onelabInterface = {0, Choices{0,1}, Name "Input/3Problem/2Get solution during simulation?"}]; // Set to 0 for launching in terminal (faster)
    realTimeInfo = 1;
    realTimeSolution = onelabInterface;

    // ------- PROBLEM DEFINITION -------
    // Test name - for output files
    name = "cylinder_2D";
    // (directory name for .txt files, not .pos files)
    testname = "cylinder_2D_model";
    // Dimension of the problem
    Dim = 2;
    // Axisymmetry of the problem, 0: no, 1: yes
    Axisymmetry = 0;

    // ------- WEAK FORMULATION -------
    // Choice of the formulation
    formulation = (preset==1) ? h_formulation : a_formulation;

    // ------- Definition of the physical regions -------
    // Material type of region MATERIAL, 0: air, 1: super, 2: copper, 3: soft ferro
    MaterialType = 1;
    // Filling the regions (see commonInformation.pro for the region list)
    Air = Region[ AIR ];
    // Air += Region[ AIR_OUT ];
    If(MaterialType == 0)
        Air += Region[ MATERIAL ];
    ElseIf(MaterialType == 1)
        Super += Region[ MATERIAL ];
        BndOmegaC += Region[ BND_MATERIAL ];
        IsThereSuper = 1; // For convergence criterion to know it
    ElseIf(MaterialType == 2)
        Copper += Region[ MATERIAL ];
        BndOmegaC += Region[ BND_MATERIAL ];
    ElseIf(MaterialType == 3)
        Ferro += Region[ MATERIAL ];
        IsThereFerro = 1; // For convergence criterion to know it
    EndIf

    // Fill the regions for formulation
    MagnAnhyDomain = Region[ {Ferro} ];
    MagnLinDomain = Region[ {Air, Super, Copper} ];
    NonLinOmegaC = Region[ {Super} ];
    LinOmegaC = Region[ {Copper} ];
    OmegaC = Region[ {LinOmegaC, NonLinOmegaC} ];
    OmegaCC = Region[ {Air, Ferro} ];
    Omega = Region[ {OmegaC, OmegaCC} ];

    // Boundaries for BC
    SurfOut = Region[ SURF_OUT ];
    // SurfSym = Region[ SURF_SYM ];
    If(formulation == h_formulation)
        Gamma_h = Region[{SurfOut}]; // Essential BC
        Gamma_e = Region[{}]; // Natural BC
    ElseIf(formulation == a_formulation)
        Gamma_h = Region[{}]; // Natural BC
        Gamma_e = Region[{SurfOut}]; // Essential BC
    EndIf
    GammaAll = Region[ {Gamma_h, Gamma_e} ];
}

Function{
    // ------- PARAMETERS -------
    // Superconductor parameters
    DefineConstant [jc = {1e8, Name "Input/3Material Properties/2jc (Am⁻²)"}]; // Critical current density [A/m2]
    DefineConstant [n = {20, Name "Input/3Material Properties/1n (-)"}]; // Superconductor exponent (n) value [-]
    // Ferromagnetic material parameters
    DefineConstant [mur0 = 1700.0]; // Relative permeability at low fields [-]
    DefineConstant [m0 = 1.04e6]; // Magnetic field at saturation [A/m]
    DefineConstant [theta_angle = 0]; // Magnetic field at saturation [A/m]
    // Excitation - Source field or imposed current intensty
    // 0: sine, 1: triangle, 2: up-down-pause, 3: step, 4: up-pause-down
    DefineConstant [Flag_Source = {4, Highlight "yellow", Choices{
        0="Sine",
        1="Triangle",
        4="pause"}, Name "Input/4Source/0Source field type" }];
    DefineConstant [f = {0.1, Visible (Flag_Source ==0), Name "Input/4Source/1Frequency (Hz)"}]; // Frequency of imposed current intensity [Hz]
    DefineConstant [bmax = {0.02, Name "Input/4Source/2Field amplitude (T)"}]; // Maximum applied magnetic induction [T]
    DefineConstant [partLength = {5, Visible (Flag_Source != 0), Name "Input/4Source/1Ramp duration (s)"}];
    DefineConstant [timeStart = 0]; // Initial time [s]
    DefineConstant [timeFinal = 5]; // Final time for source definition [s]
    DefineConstant [timeFinalSimu = timeFinal]; // Final time of simulation [s]

    // ------- NUMERICAL PARAMETERS -------
    DefineConstant [dt = {0.1, Highlight "LightBlue",
        ReadOnly !expMode, Name "Input/5Method/Time step (s)"}]; // Time step (initial if adaptive)[s]
    DefineConstant [writeInterval = dt]; // Time interval between two successive output file saves [s]
    DefineConstant [dt_max = dt]; // Maximum allowed time step [s]
    DefineConstant [tol_energy = {(preset == 1) ? 1e-6 : 1e-4, Highlight "LightBlue",
        ReadOnly !expMode, Name "Input/5Method/Relative tolerance (-)"}]; // Relative tolerance on the energy estimates
    DefineConstant [iter_max = {(preset==1) ? 50 : 600, Highlight "LightBlue",
        ReadOnly !expMode, Name "Input/5Method/Max number of iteration (-)"}]; // Maximum number of nonlinear iterations
    DefineConstant [extrapolationOrder = (preset==1) ? 1 : 2]; // Extrapolation order

    // Control points for outputs on lines
    controlPoint1 = {1e-5,0, 0}; // CP1
    controlPoint2 = {W/2-1e-5, 0, 0}; // CP2
    controlPoint3 = {0, H_cylinder/2+2e-3, 0}; // CP3
    controlPoint4 = {W/2, H_cylinder/2+2e-3, 0}; // CP4
    savedPoints = 2000; // Resolution of the line saving postprocessing
}

Include "../lib_cylinder/lawsAndFunctions.pro";

Function{
    // Direction of applied field
    directionApplied[] = Vector[0., 1., 0.]; // Only choice for axi
    hmax[] = bmax;
    If(Flag_Source == 0)
        // Sine source field
        controlTimeInstants = {timeFinalSimu, 1/(2*f), 1/f, 3/(2*f), 2*timeFinal};
        hsVal[] = hmax * Sin[2.0 * Pi * f * $Time];
    ElseIf(Flag_Source == 1)
        // Triangle source field (5/4 of a complete cycle)
        controlTimeInstants = {timeFinal, timeFinal/5.0, 3.0*timeFinal/5.0, timeFinal};
        rate = hmax * 5.0 / timeFinal;
        hsVal[] = (($Time < timeFinal/5.0) ? $Time * rate :
                    ($Time >= timeFinal/5.0 && $Time < 3.0*timeFinal/5.0) ?
                    hmax - ($Time - timeFinal/5.0) * rate :
                    - hmax + ($Time - 3.0*timeFinal/5.0) * rate);
    ElseIf(Flag_Source == 4)
        // Up-pause-down
        controlTimeInstants = {timeFinal/3.0, 2.0*timeFinal/3.0, timeFinal};
        //rate = hmax * 3.0 / timeFinal;
        hsVal[] = 1;
    EndIf

}

// Only external field is implemented
Constraint {
    { Name a ;
        Case {
            // Square because axisymmetry and circulation on perpendicular edge
            {Region Gamma_e ; Value -X[]*hmax[]*Cos[theta_angle] + Y[]*hmax[]*Sin[theta_angle] ; TimeFunction hsVal[] ;}
        }
    }
    { Name phi ;
        Case {
            {Region Gamma_h ; Value XYZ[]*directionApplied[] ; TimeFunction hsVal[] ;}
        }
    }
    { Name Voltage ;
        Case {
            If(formulation == h_formulation || formulation == coupled_formulation)
                // No cut is defined in this geometry (no applied current) -> No associated constraint
            Else
                // a-formulation and BF_RegionZ
                { Region OmegaC; Value 0.0; } // The grad v term is zero (axisymmetry)
            EndIf
        }
    }
}

Include "../lib_cylinder/jac_int.pro";
Include "../lib_cylinder/formulations.pro";
Include "../lib_cylinder/resolution.pro";

PostOperation {
    // Runtime output for graph plot
    { Name Info;
        If(formulation == h_formulation)
            NameOfPostProcessing MagDyn_htot ;
        ElseIf(formulation == a_formulation)
            NameOfPostProcessing MagDyn_avtot ;
        ElseIf(formulation == coupled_formulation)
            NameOfPostProcessing MagDyn_coupled ;
        EndIf
        Operation{
            Print[ time[OmegaC], OnRegion OmegaC, LastTimeStepOnly, Format Table, SendToServer "Output/0Time [s]"] ;
            Print[ bsVal[OmegaC], OnRegion OmegaC, LastTimeStepOnly, Format Table, SendToServer "Output/1Applied field [T]"] ;
            Print[ m_avg_y_tesla[OmegaC], OnGlobal, LastTimeStepOnly, Format Table, SendToServer "Output/2Avg. magnetization [T]"] ;
            Print[ dissPower[OmegaC], OnGlobal, LastTimeStepOnly, Format Table, SendToServer "Output/2Joule loss [W]"] ;
        }
    }
    { Name MagDyn; LastTimeStepOnly realTimeSolution ;
        If(formulation == h_formulation)
            NameOfPostProcessing MagDyn_htot;
        ElseIf(formulation == a_formulation)
            NameOfPostProcessing MagDyn_avtot;
        ElseIf(formulation == coupled_formulation)
            NameOfPostProcessing MagDyn_coupled;
        EndIf
        Operation {
            If(economPos == 0)
                If(formulation == h_formulation)
                    Print[ phi, OnElementsOf OmegaCC , File "res/phi.pos", Name "phi [A]" ];
                ElseIf(formulation == a_formulation)
                    Print[ a, OnElementsOf Omega , File "res/a.pos", Name "a [Tm]" ];
                    Print[ az, OnElementsOf Omega , File "res/az.pos", Name "az [Tm]" ];
                    Print[ ur, OnElementsOf OmegaC , File "res/ur.pos", Name "ur [V/m]" ];
                EndIf
                Print[ j, OnElementsOf OmegaC , File "res/j.pos", Name "j [A/m2]" ];
                Print[ jz, OnElementsOf OmegaC , File "res/jz.pos", Name "jz [A/m2]" ];
                Print[ e, OnElementsOf OmegaC , File "res/e.pos", Name "e [V/m]" ];
                Print[ h, OnElementsOf Omega , File "res/h.pos", Name "h [A/m]" ];
                Print[ b, OnElementsOf Omega , File "res/b.pos", Name "b [T]" ];
                // Print[ bnorm, OnElementsOf Omega , File "res/bnorm.pos", Name "bnorm [T]" ];
            EndIf
            Print[ m_avg[OmegaC], OnRegion OmegaC, Format TimeTable, File outputMagnetization];
            // Print[ acloss[OmegaC], OnRegion OmegaC, Format TimeTable, File outputacloss];
            Print[ j, OnLine{{List[controlPoint1]}{List[controlPoint2]}} {savedPoints},
                Format TimeTable, File outputCurrent];
            Print[ j, OnPoint{List[{0.0008,0,0}]}, Format TimeTable, File outputPoint];
            // Print[ a, OnPoint{List[{0.0008,0,0}]}, Format TimeTable, File outputPoint2];
            Print[ b, OnLine{{List[controlPoint1]}{List[controlPoint2]}} {savedPoints},
                Format TimeTable, File outputMagInduction1];
            Print[ b, OnLine{{List[controlPoint3]}{List[controlPoint4]}} {savedPoints},
                Format TimeTable, File outputMagInduction2];
            Print[ hsVal[Omega], OnRegion Omega, Format TimeTable, File outputAppliedField];
        }
    }
}

DefineConstant[
  R_ = {"MagDyn", Name "GetDP/1ResolutionChoices", Visible 0},
  C_ = {"-solve -pos -bin -v 3 -v2", Name "GetDP/9ComputeCommand", Visible 0},
  P_ = { "MagDyn", Name "GetDP/2PostOperationChoices", Visible 0}
];
