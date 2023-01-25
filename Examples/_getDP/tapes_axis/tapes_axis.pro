Include "tapes_axis_data.pro";
Include "../lib_tapes/commonInformation.pro";

Group {
    // Output choice
    DefineConstant[onelabInterface = {0, Choices{0,1}, Name "Input/3Problem/2Get solution during simulation? (not always stable, but always slower)"}]; // Set to 0 for launching in terminal (faster)
    realTimeInfo = 1;
    realTimeSolution = onelabInterface;
    // ------- PROBLEM DEFINITION -------
    // Test name - for output files
    name = "tapes_axis";
    // (directory name for .txt files, not .pos files)
    DefineConstant [testname = "tapes_axis_model"];
    // Dimension of the problem
    Dim = 2;
    // Axisymmetry of the problem, 0: no, 1: yes
    Axisymmetry = 1;

    // ------- WEAK FORMULATION -------
    // Choice of the formulation
    formulation = (preset==1) ? h_formulation : ((preset == 4) ? ta_formulation : a_formulation);


    // ------- Definition of the physical regions -------
    // Material type of region MATERIAL, 0: air, 1: super, 2: copper, 3: soft ferro
    MaterialType = 1;
    // Filling the regions
    Air = Region[ AIR ];
    Air += Region[ AIR_OUT ];
    If(MaterialType == 0)
        Air += Region[ MATERIAL ];
    ElseIf(MaterialType == 1 || MaterialType == 2)
        Cond = Region[ MATERIAL ];
        BndOmegaC += Region[ BND_MATERIAL ];
        BndOmegaC_side += Region[ BND_MATERIAL_SIDE ];
        Cuts = Region[ CUT ];
        If(MaterialType == 1)
            Super += Region[ MATERIAL ];
            IsThereSuper = 1;
        ElseIf(MaterialType == 2)
            Copper += Region[ MATERIAL ];
        EndIf
    ElseIf(MaterialType == 3)
        Ferro += Region[ MATERIAL ];
        IsThereFerro = 1;
    EndIf
    // Edges of the tape: to be used by the ta_formulation
    Edge1 = Region[ EDGE_1 ];
    Edge2 = Region[ EDGE_2 ];
    LateralEdges = Region[ {Edge1, Edge2} ];
    PositiveEdges = Region[ {Edge2} ];

    // Fill the regions for formulation
    MagnAnhyDomain = Region[ {Ferro} ];
    MagnLinDomain = Region[ {Air, Super, Copper} ];
    NonLinOmegaC = Region[ {Super} ];
    LinOmegaC = Region[ {Copper} ];
    OmegaC = Region[ {LinOmegaC, NonLinOmegaC} ];
    OmegaCC = Region[ {Air, Ferro} ];
    Omega = Region[ {OmegaC, OmegaCC} ];
    ArbitraryPoint = Region[ ARBITRARY_POINT ]; // To fix the potential

    // Boundaries for BC
    SurfOut = Region[ SURF_OUT ];
    SurfSym = Region[ SURF_SYM ];
    Gamma_h = Region[{}];
    Gamma_e = Region[{SurfOut, SurfSym}];
    GammaAll = Region[ {Gamma_h, Gamma_e} ];
}


Function{
    // ------- PARAMETERS -------
    // Superconductor parameters
    DefineConstant [jc = {3e10, Name "Input/3Material Properties/2jc (Am⁻²)"}]; // Critical current density [A/m2]
    DefineConstant [n = {40, Name "Input/3Material Properties/1n (-)"}]; // Superconductor exponent (n) value [-]
    // Ferromagnetic material parameters
    DefineConstant [mur0 = 1700.0]; // Relative permeability at low fields [-]
    DefineConstant [m0 = 1.04e6]; // Magnetic field at saturation [A/m]

    // Excitation
    DefineConstant [IFraction = {0.8, Name "Input/4Source/0Fraction of max. current intensity (-)"}];
    DefineConstant [Imax = IFraction*jc*W_tape*H_tape]; // Maximum imposed current intensity [A]
    DefineConstant [f = 50]; // Frequency of imposed current intensity [Hz]
    DefineConstant [timeStart = 0]; // Initial time [s]
    DefineConstant [timeFinal = 1/f]; // Final time for source definition [s]
    DefineConstant [timeFinalSimu = 1/f]; // Final time of simulation [s]

    // Numerical parameters
    DefineConstant [nbStepsPerPeriod = {(preset!=2) ? 400/meshMult : 8, Highlight "LightBlue",
        ReadOnly !expMode, Name "Input/5Method/Number of time step per period (-)"}]; // Number of time steps over one period [-]
    DefineConstant [dt = 1/(nbStepsPerPeriod*f)]; // Time step (initial if adaptive)[s]
    DefineConstant [writeInterval = dt]; // Time interval between two successive output file saves [s]
    DefineConstant [dt_max = dt]; // Maximum allowed time step [s]
    DefineConstant [iter_max = {(preset==1 || preset==4) ? 50 : 600, Highlight "LightBlue",
        ReadOnly !expMode, Name "Input/5Method/Max number of iteration (-)"}]; // Maximum number of nonlinear iterations
    DefineConstant [extrapolationOrder = 1]; // Extrapolation order
    DefineConstant [tol_energy = {(preset==1 || preset==4) ? 1e-6 : 1e-4, Highlight "LightBlue",
        ReadOnly !expMode, Name "Input/5Method/Relative tolerance (-)"}]; // Relative tolerance on the energy estimates
    // Control points
    controlPoint1 = {3e-2,0, 0}; // CP1
    controlPoint2 = {3e-2+39*(sep+W_tape), 0, 0}; // CP2
    controlPoint3 = {3e-2+0.1e-3,-H_tape/2, 0}; // CP3
    controlPoint4 = {3e-2+0.1e-3, H_tape/2, 0}; // CP4
    DefineConstant [savedPoints = 2000]; // Resolution of the line saving postprocessing

    // Sine source field
    controlTimeInstants = {timeFinalSimu, 1/(2*f), 1/f, 3/(2*f), 2*timeFinal};
    I[] = Imax * Sin[2.0 * Pi * f* $Time];

    // For the t-a-formulation
    thickness[Cond] = W_tape;
    thickness[Edge2] = W_tape;
    thickness[Air] = W_tape; // Fix me, doesn't make sense to define it here...
}

Function{
    hsVal[] = Sin[2*Pi*f*$Time];
}

Include "../lib_tapes/lawsAndFunctions.pro";

Constraint {
    { Name a ;
        Case {
            {Region Gamma_e ; Value /*-0.12*X[]^2*/ 0.0 ; TimeFunction hsVal[] ;}
        }
    }
    { Name phi ;
        Case {
            {Region ArbitraryPoint ; Value 0.0;} // If no surf sym (we could have put one here), fix it at one point
        }
    }
    { Name Current ; Type Assign;
        Case {
            If(formulation == h_formulation || formulation == coupled_formulation)
                // h-formulation and cuts
                { Region Cuts; Value 1.0; TimeFunction I[]; }
            Else
                // a-formulation and BF_RegionZ
                { Region Cond; Value 1.0; TimeFunction I[]; }
            ElseIf(formulation == ta_formulation)
                // t-a-formulation
                { Region Edge2; Value 1.0; TimeFunction I[]; } // t_tilde = w t
            EndIf
        }
    }
    { Name Voltage ; Case { } } // Nothing
}


Include "../lib_tapes/jac_int.pro";
Include "../lib_tapes/formulations.pro";
Include "../lib_tapes/resolution.pro";

PostOperation {
    // Runtime output for graph plot
    { Name Info;
        If(formulation == h_formulation)
            NameOfPostProcessing MagDyn_htot ;
        ElseIf(formulation == a_formulation)
            NameOfPostProcessing MagDyn_avtot ;
        ElseIf(formulation == coupled_formulation)
            NameOfPostProcessing MagDyn_coupled ;
        ElseIf(formulation == ta_formulation)
            NameOfPostProcessing MagDyn_ta ;
        EndIf
        Operation{
            Print[ time[OmegaC], OnRegion OmegaC, LastTimeStepOnly, Format Table, SendToServer "Output/0Time [s]"] ;
            If(formulation == h_formulation)
                Print[ I, OnRegion Cuts, LastTimeStepOnly, Format Table, SendToServer "Output/1Applied current [A]"] ;
                Print[ V, OnRegion Cuts, LastTimeStepOnly, Format Table, SendToServer "Output/2Tension [Vm^-1]"] ;
            ElseIf(formulation == a_formulation)
                Print[ I, OnRegion OmegaC, LastTimeStepOnly, Format Table, SendToServer "Output/1Applied current [A]"] ;
                Print[ U, OnRegion OmegaC, LastTimeStepOnly, Format Table, SendToServer "Output/2Tension [Vm^-1]"] ;
            ElseIf(formulation == ta_formulation)
                Print[ I, OnRegion PositiveEdges, LastTimeStepOnly, Format Table, SendToServer "Output/1Applied current [A]"] ;
                Print[ V, OnRegion PositiveEdges, LastTimeStepOnly, Format Table, SendToServer "Output/2Tension [Vm^-1]"] ;
            EndIf
            Print[ dissPower[OmegaC], OnGlobal, LastTimeStepOnly, Format Table, SendToServer "Output/3Joule loss [W]"] ;
        }
    }
    { Name MagDyn;LastTimeStepOnly realTimeSolution ;
        If(formulation == h_formulation)
            NameOfPostProcessing MagDyn_htot;
        ElseIf(formulation == a_formulation)
            NameOfPostProcessing MagDyn_avtot;
        ElseIf(formulation == coupled_formulation)
            NameOfPostProcessing MagDyn_coupled;
        ElseIf(formulation == ta_formulation)
            NameOfPostProcessing MagDyn_ta ;
        EndIf
        Operation {
            If(economPos == 0)
                If(formulation == h_formulation)
                    Print[ phi, OnElementsOf OmegaCC , File "res/phi.pos", Name "phi [A]" ];
                ElseIf(formulation == a_formulation)
                    Print[ compz_a, OnElementsOf Omega , File "res/a.pos", Name "a [Tm]" ];
                    Print[ ur, OnElementsOf OmegaC , File "res/ur.pos", Name "ur [V/m]" ];
                ElseIf(formulation == ta_formulation)
                    Print[ compz_a, OnElementsOf Omega , File "res/a.pos", Name "a [Tm]" ];
                    Print[ t, OnElementsOf OmegaC , File "res/t.pos", Name "t [Am]" ];
                    Print[ t, OnLine{{List[controlPoint1]}{List[controlPoint2]}} {savedPoints},
                        Format TimeTable, File "res/tLine.txt"];
                EndIf
                Print[ j, OnElementsOf OmegaC , File "res/j.pos", Name "j [A/m2]" ];
                Print[ jz, OnElementsOf OmegaC , File "res/jz.pos", Name "jz [A/m2]" ];
                If(formulation != ta_formulation)
                    Print[ jz, OnElementsOf OmegaC , File "res/jz.pos", Name "jz [A/m2]" ];
                EndIf
                Print[ e, OnElementsOf OmegaC , File "res/e.pos", Name "e [V/m]" ];
                // Print[ h, OnElementsOf Omega , File "res/h.pos", Name "h [A/m]" ];
                If(formulation == ta_formulation)
                    Print[ norm_b, OnElementsOf OmegaCC , File "res/b.pos", Name "normB [T]" ];
                    Print[ br, OnElementsOf OmegaCC , File "res/br.pos", Name "Br [T]" ];
                    Print[ bz, OnElementsOf OmegaCC , File "res/bz.pos", Name "Bz [T]" ];
                Else
                    Print[ b, OnElementsOf Omega , File "res/b.pos", Name "b [T]" ];
                EndIf
            EndIf
            Print[ j, OnLine{{List[{3e-2+20*(0.15e-3+1e-6), -H_tape/2,0}]}{List[{3e-2+20*(0.15e-3+1e-6), H_tape/2,0}]}} {savedPoints},
                Format TimeTable, File outputCurrent];
            Print[ b, OnLine{{List[{3e-2+19.5*0.15e-3, -H_tape/2,0}]}{List[{3e-2+19.5*0.15e-3, H_tape/2,0}]}} {savedPoints},
                Format TimeTable, File outputMagInduction1];
            Print[ b, OnLine{{List[controlPoint3]}{List[controlPoint4]}} {savedPoints},
                Format TimeTable, File outputMagInduction2];
        }
    }
}

DefineConstant[
  R_ = {"MagDyn", Name "GetDP/1ResolutionChoices", Visible 0},
  C_ = {"-solve -pos -bin -v 3 -v2", Name "GetDP/9ComputeCommand", Visible 0},
  P_ = { "MagDyn", Name "GetDP/2PostOperationChoices", Visible 0}
];
