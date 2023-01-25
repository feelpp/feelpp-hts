// gmsh -2 -bin cylinder_2D_static.geo
// getdp -m cylinder_2D_static.msh cylinder_2D_static.pro -solve MagSta_a -pos MagSta

AIR = 1000;
BND = 25000;
SURF_OUT = 14000;
MATERIAL = 23000;

Group {
  // Physical regions:
  Air = Region[ AIR ];
  Conductor = Region[ MATERIAL ];

  OmegaC = Region[ {Conductor} ];
  OmegaCC = Region[ {Air} ];
  Omega = Region[ {OmegaC, OmegaCC} ];
  
  SurfOut = Region[ SURF_OUT ];
  BndOmegaC = Region[ BND ];
  Gamma_e = Region[{SurfOut}];
  GammaAll = Region[ { Gamma_e} ];
}


Function {
  NL_iter_max = 60;
  NL_Eps = 1e-8;
  NL_Relax = 0.2;
  NL_tol_abs = 1e-10;
  NL_tol_rel = 1e-6;
  
  mu0 = 4e-7 * Pi;
  DefineConstant [jc = {1e8, Name "Input/3Material Properties/2jc (Am⁻²)"}]; // Critical current density [A/m2]
  DefineConstant [n = {20, Name "Input/3Material Properties/1n (-)"}]; // Superconductor exponent (n) value [-]
  DefineConstant [Ar = {1e-7, Name "Input/3Material Properties/3Ar (Wb m^-1)"}]; 
  DefineConstant [bmax = {0.02, Name "Input/4Source/2Field amplitude (T)"}]; // Maximum applied magnetic induction [T]
  DefineConstant [theta_angle = 0];

  mu [ Air ]  =  mu0;
  mu [ Conductor ]  =  mu0;

  nu [ Air ]  = 1./ mu0;
  nu [ Conductor ]  = 1./ mu0;

  hmax[] = bmax;
  jfunc[] = jc * Erf[-CompZ[$1]/Ar]/((CompZ[$1] == 0) ? 1 : CompZ[$1]);
  jfunc2[] = jc * Erf[-CompZ[$1]/Ar];
  js_fct[ Conductor ] = jfunc[$1];
}

Constraint {
  { Name Dirichlet_a_Mag;
    Case {
      { Region Gamma_e ; Value -X[]*hmax[]; }
    }
  } 
  { Name Dirichlet_a_ini;
    Case {
      { Region Omega ; Value -X[]*hmax[]; Type Init; }
    }
  } 
}

Group {
  Omega_a_AndBnd  = Region[{Omega, GammaAll, BndOmegaC}];
}

FunctionSpace {
  { Name Hcurl_a_Mag_2D; Type Form1P; // Magnetic vector potential a
    BasisFunction {
      { Name se; NameOfCoef ae; Function BF_PerpendicularEdge;
        Support Omega ; Entity NodesOf[ All ]; }
    }
    Constraint {
      { NameOfCoef ae; EntityType NodesOf;
        NameOfConstraint Dirichlet_a_Mag; }
    }
  }
  /*
  { Name Hregion_j_Mag_2D; Type Vector; // Electric current density js
    BasisFunction {
      { Name sr; NameOfCoef jsr; Function BF_RegionZ;
        Support Vol_S_Mag; Entity Vol_S_Mag; }
    }
    Constraint {
      { NameOfCoef jsr; EntityType Region;
        NameOfConstraint SourceCurrentDensityZ; }
    }
  }*/

}

Jacobian {
  { Name Vol ;
        Case { 
          { Region All ; Jacobian Vol ; }
        }
  }
  { Name Sur ;
        Case {
          { Region All ; Jacobian Sur ; }
        }
    }
}

Integration {
  { Name Int ;
      Case {
          { Type Gauss ;
              Case {
                  { GeoElement Point ; NumberOfPoints 1 ; }
                  { GeoElement Line ; NumberOfPoints 3 ; }
                  { GeoElement Line2 ; NumberOfPoints 4 ; } // Second-order element
                  { GeoElement Triangle ; NumberOfPoints 3 ; }
                  { GeoElement Triangle2 ; NumberOfPoints 12 ; }
                  { GeoElement Quadrangle ; NumberOfPoints 4 ; }
                  { GeoElement Quadrangle2 ; NumberOfPoints 4 ; } // Second-order element
              }
          }
      }
  }
}


Formulation {
  { Name Magnetostatics_a_2D; Type FemEquation;
    Quantity {
      { Name a ; Type Local; NameOfSpace Hcurl_a_Mag_2D; }
      // { Name js; Type Local; NameOfSpace Hregion_j_Mag_2D; }
    }
    Equation {
      Integral { [  Dof{d a} , {d a} ];
        In Omega; Jacobian Vol; Integration Int; }
      Integral { [ -mu[] * js_fct[{a}]*Dof{a}, {a} ];
        In OmegaC; Jacobian Vol; Integration Int; }
      // Integral { [ -mu[] * jfunc[{a}], {a} ];
      //   In OmegaC; Jacobian Vol; Integration Int; }
    }
  }
}

Resolution {
  { Name MagSta_a;
    System {
      { Name Sys_Mag; NameOfFormulation Magnetostatics_a_2D; }
    }
    Operation {
      // InitSolution[Sys_Mag]; 
      // IterativeLoop[600, 1e-6, 1] {
      //       GenerateJac[Sys_Mag]    ; SolveJac[Sys_Mag]; 
      // }
      // SaveSolution[Sys_Mag];
      // InitSolution[Sys_Mag] ; SaveSolution[Sys_Mag] ;
      
      // IterativeLoop {
      //   NbrMaxIteration NL_iter_max ; Criterion NL_Eps;
      //   RelaxationFactor NL_Relax ;
      //   Operation { 
      //     GenerateJac Sys_Mag    ; SolveJac Sys_Mag; 
      //   }
      // }
      // SaveSolution[Sys_Mag];
      // Generate[Sys_Mag]; Solve[Sys_Mag];

      InitSolution[Sys_Mag];
  
      Generate[Sys_Mag]; GetResidual[Sys_Mag, $res0];
      Evaluate[ $res = $res0, $iter = 0 ];
      
      Print[{$iter, $res, $res / $res0},
        Format "Residual %03g: abs %14.12e rel %14.12e"];
      While[$res > NL_tol_abs && $res / $res0 > NL_tol_rel &&
            $res / $res0 <= 1 && $iter < NL_iter_max]{
        
        CopySolution[Sys_Mag,'x_Prev'];
        
        // Get the increment Delta_x
        Generate[Sys_Mag]; GetResidual[Sys_Mag, $res];
        Solve[Sys_Mag]; 
        CopySolution[Sys_Mag,'x_New'];
        AddVector[Sys_Mag, 1, 'x_New', -1, 'x_Prev', 'Delta_x'];

        AddVector[Sys_Mag, 1, 'x_New', NL_Relax, 'x_Prev', 'Delta_x'];
        CopySolution['x_New', Sys_Mag];
        Generate[Sys_Mag]; GetResidual[Sys_Mag, $res];
         
        Evaluate[ $iter = $iter + 1 ];
        Print[{$iter, $res, $res / $res0},
          Format "Residual %03g: abs %14.12e rel %14.12e"];
      }
      
      SaveSolution[Sys_Mag];

    }
  }
}

PostProcessing {
  { Name MagSta; NameOfFormulation Magnetostatics_a_2D;
    Quantity {
      { Name a;
        Value {
          Term { [ {a} ]; In Omega; Jacobian Vol; }
        }
      }
      { Name az;
        Value {
          Term { [ CompZ[{a}] ]; In Omega; Jacobian Vol; }
        }
      }
      // { Name az;
      //   Value {
      //     Term { [ Erf[-CompZ[{a}]/Ar] ]; In Omega; Jacobian Vol; }
      //   }
      // }
      { Name anorm;
        Value {
          Term { [ Norm[{a}] ]; In Omega; Jacobian Vol; }
        }
      }
      { Name bz;
        Value {
          Term { [ CompY[{d a}] ]; In Omega; Jacobian Vol; }
        }
      }
      { Name bnorm;
        Value {
          Term { [ Norm[{d a}] ]; In Omega; Jacobian Vol; }
        }
      }
      { Name h;
        Value {
          Term { [ nu[] * {d a} ]; In Omega; Jacobian Vol; }
        }
      }
      { Name j;
        Value {
          Term { [ jfunc2[{a}]/**CompZ[{a}]*/ ]; In OmegaC; Jacobian Vol; }
        }
      }
    }
  }
}


PostOperation {
  { Name MagSta; NameOfPostProcessing MagSta;
    Operation {
    //   Echo[ Str["l=PostProcessing.NbViews-1;",
		// "View[l].IntervalsType = 1;",
		// "View[l].NbIso = 40;"],
	  //   File "tmp.geo", LastTimeStepOnly] ;
      Print[ a, OnElementsOf Omega, File "a.pos" ];
      Print[ j, OnElementsOf OmegaC, File "js.pos" ];
      Print[ az, OnElementsOf Omega, File "az.pos" ];
      Print[ anorm, OnElementsOf Omega, File "anorm.pos" ];
      Print[ bz, OnElementsOf Omega, File "bz.pos" ];
      Print[ bnorm, OnElementsOf Omega, File "bnorm.pos" ];
      //Print[ b, OnLine{{List[p1]}{List[p2]}} {50}, File "by.pos" ];
      Print[ j, OnLine{{List[{-0.001, 0,0}]}{List[{0.001, 0,0}]}} {2000},
                Format TimeTable, File "jline.txt"];
    }
  }
}
