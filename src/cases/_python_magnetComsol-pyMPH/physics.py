import numpy as np
from typing import List
from methods import get_markers, get_materials_markers, json_get, feel_to_comsol_symbols


def create_physics(
    model,
    equations: List[str],
    data: dict,
    dim: int,
    selection_import: dict,
    unknowns: dict,
    args,
):
    ### Create the physic
    print("Info    : Creating Physics...")

    physics_method = {
        "magnetic": create_magnetic,
        "heat": create_heat,
        "elastic": create_elastic,
        "elastic1": create_elastic,
        "elastic2": create_nothing,
        "electric": create_electric,
    }

    ### Browse equations and create corresponding physic
    for eq in equations:
        physics_method[eq](
            model, equations, data, dim, selection_import, unknowns, args
        )

    print("Info    : Done creating Physics")


def create_magnetic(
    model,
    equations: List[str],
    data: dict,
    dim: int,
    selection_import: dict,
    unknowns: dict,
    args,
):
    if dim == 2:
        si_markers = "surface"
    elif dim == 3:
        si_markers = "volume"

    print("Info    : Creating Magnetic Physic")
    physics = model / "physics"
    geometry = (model / "geometries").children()[0]

    models = json_get(data, "Models", "magnetic", "models")
    if not models:
        models = [json_get(data, "Models", "magnetic")]

    materials = data["Materials"]

    part_electric = []
    for mod in models:
        if "f" in mod["setup"]["coefficients"]:
            part_electric.extend(get_materials_markers(mod, materials))

    # create A formulation
    print("Info    :    A formulation")
    Aform = physics.create("InductionCurrents", geometry, name="A formulation")

    al = Aform / "Ampère's Law 1"
    al.property("mur_mat", "userdef")
    al.property("sigma_mat", "userdef")
    al.property("sigma", "0")
    al.property("epsilonr_mat", "userdef")

    if dim == 2:
        J_Aform = Aform.create(
            "ExternalCurrentDensity", dim, name="External Current Density"
        )
        J_Aform.select(
            np.concatenate(
                [selection_import[si_markers][marker] for marker in part_electric]
            )
        )
        if args.axis:
            J_Aform.property("Je", ["0", "u", "0"])
        else:
            J_Aform.property("Je", ["0", "0", "u"])

        # create J formulation
        print("Info    :    J formulation")
        Jform = physics.create("CoefficientFormPDE", geometry, name="J formulation")
        Jform.select(
            np.concatenate(
                [selection_import[si_markers][marker] for marker in part_electric]
            )
        )
        # Jform.property("CustomDependentVariableUnit", "A/m^2")
        # Jform.property("CustomSourceTermUnit", "V/m")
        cf = Jform / "Coefficient Form PDE 1"
        magnetic_potential = "mf.Az"
        if args.axis:
            magnetic_potential = "mf.Aphi"
        cf.property("f", f"-d( {magnetic_potential},TIME)")
        cf.property("a", "rho")
        cf.property("c", "0")
        cf.property("da", "0")

        print("Info    :    Global Constraint")
        if args.mdata:
            for magnet in args.mdata:
                part_magnet = [marker for marker in part_electric if magnet in marker]

                for marker in part_magnet:
                    if args.debug:
                        print(f"Debug   :        Global Constraint {marker}")
                    model.java.component("component").cpl().create(
                        f"intop{marker}", "Integration"
                    )
                    model.java.component("component").cpl(
                        f"intop{marker}"
                    ).selection().geom(dim)
                    model.java.component("component").cpl(
                        f"intop{marker}"
                    ).selection().set(selection_import[si_markers][marker])

                    GC = Jform.create(
                        "GlobalConstraint", -1, name=f"Global Constraint {marker}"
                    )
                    GC.property(
                        "constraintExpression",
                        f"intop{marker}(u/N_{marker})-{magnet}_Imax",
                    )
        else:
            for marker in part_electric:
                if args.debug:
                    print(f"Debug   :        Global Constraint {marker}")
                model.java.component("component").cpl().create(
                    f"intop{marker}", "Integration"
                )
                model.java.component("component").cpl(
                    f"intop{marker}"
                ).selection().geom(dim)
                model.java.component("component").cpl(f"intop{marker}").selection().set(
                    selection_import[si_markers][marker]
                )

                GC = Jform.create(
                    "GlobalConstraint", -1, name=f"Global Constraint {marker}"
                )
                GC.property("constraintExpression", f"intop{marker}(u/N_{marker})-Imax")

        model.java.component("component").setGroupByType(True)
        model.java.component("component").physics(Jform.tag()).setGroupBySpaceDimension(
            True
        )
    elif dim == 3:
        for mod in models:
            if "f" in mod["setup"]["coefficients"]:
                J_Aform = Aform.create(
                    "ExternalCurrentDensity",
                    dim,
                    name=f"External Current Density {json_get(mod,'name')}",
                )
                J_Aform.select(
                    np.concatenate(
                        [
                            selection_import[si_markers][marker]
                            for marker in get_materials_markers(mod, materials)
                        ]
                    )
                )
                f_coef = (
                    mod["setup"]["coefficients"]["f"]
                    .replace("materials_", "")
                    .split(":")[0]
                )
                f_coef = feel_to_comsol_symbols(f_coef, unknowns)
                f_values = f_coef[f_coef.find("{") + 1 : f_coef.find("}")].split(",")
                J_Aform.property("Je", [f_values[0], f_values[1], f_values[2]])


def create_heat(
    model,
    equations: List[str],
    data: dict,
    dim: int,
    selection_import: dict,
    unknowns: dict,
    args,
):
    if dim == 2:
        si_markers = "surface"
        si_bound = "curve"
    elif dim == 3:
        si_markers = "volume"
        si_bound = "surface"

    print("Info    : Creating Heat Physic")
    physics = model / "physics"
    geometry = (model / "geometries").children()[0]

    models = json_get(data, "Models", "heat", "models")
    if not models:
        models = [json_get(data, "Models", "heat")]

    materials = data["Materials"]
    boundaries = json_get(data, "BoundaryConditions", "heat", "Robin")

    part_thermic = []
    part_electric = []
    for mod in models:
        part_thermic.extend(get_materials_markers(mod, materials))

        if "f" in json_get(mod, "setup", "coefficients"):
            part_electric.extend(get_materials_markers(mod, materials))

    # create heat formulation
    print("Info    :    Heat Transfer")
    heat = physics.create("HeatTransfer", geometry, name="Heat Transfer")
    heat.select(
        np.concatenate(
            [selection_import[si_markers][marker] for marker in part_thermic]
        )
    )

    initial = json_get(data, "InitialConditions", "heat", "temperature", "Expression")
    initial_file = json_get(data, "InitialConditions", "heat", "temperature", "File")
    print("Info    :    Initial Conditions")
    if initial:
        for init in initial:
            ic = heat.create("init", dim, name=f"Initial Values {init}")
            markers = get_markers(init, initial)
            ic.select(
                np.concatenate(
                    [selection_import[si_markers][marker] for marker in markers]
                )
            )
            ic.property("Tinit", initial[init]["expr"].split(":")[0])
    elif initial_file:
        pass
    else:
        ini = heat / "Initial Values 1"
        ini.property("Tinit", 293)

    sd = heat / "Solid 1"
    sd.property("k_mat", "userdef")
    sd.property("rho_mat", "userdef")
    sd.property("Cp_mat", "userdef")
    sd.property("k", "k")
    if args.timedep:
        sd.property("rho", "rho")
        sd.property("Cp", "Cp")

    print("Info    :    Heat Source")
    if dim == 2 and "magnetic" in equations:
        HeatSource = heat.create("HeatSource", dim, name="Heat Source")
        HeatSource.select(
            np.concatenate(
                [selection_import[si_markers][marker] for marker in part_electric]
            )
        )
        HeatSource.property("Q0", "u*u/sigma")
    else:
        for mod in models:
            if "f" in mod["setup"]["coefficients"]:
                f_coef = (
                    mod["setup"]["coefficients"]["f"]
                    .replace("materials_", "")
                    .split(":")[0]
                )
                f_coef = feel_to_comsol_symbols(f_coef, unknowns)

                HeatSource = heat.create(
                    "HeatSource", dim, name=f"Heat Source {json_get(mod,'name')}"
                )
                HeatSource.select(
                    np.concatenate(
                        [
                            selection_import[si_markers][marker]
                            for marker in get_materials_markers(mod, materials)
                        ]
                    )
                )
                HeatSource.property("Q0", f_coef)

    if boundaries:
        print("Info    :    Robin Boundary Conditions")
        for bound in boundaries:
            markers_bound = get_markers(bound, boundaries)

            parts = boundaries[bound]["expr2"].split(":")
            hvar = None
            Tvar = None
            for part in parts:
                if part.startswith("hw"):
                    hvar = part
                elif "(" in part and ")" in part:
                    Tvar = part[part.find("(") + 1 : part.rfind(")")]
            Heatflux = heat.create(
                "HeatFluxBoundary", dim - 1, name=f"Heat Flux Boundary {bound}"
            )
            Heatflux.select(
                np.concatenate(
                    [selection_import[si_bound][marker] for marker in markers_bound]
                )
            )
            Heatflux.property("HeatFluxType", "ConvectiveHeatFlux")
            Heatflux.property("h", hvar)
            Heatflux.property("Text", Tvar)


def create_elastic(
    model,
    equations: List[str],
    data: dict,
    dim: int,
    selection_import: dict,
    unknowns: dict,
    args,
):
    if dim == 2:
        si_markers = "surface"
        si_bound = "curve"
    elif dim == 3:
        si_markers = "volume"
        si_bound = "surface"

    print("Info    : Creating Elastic Physic")
    physics = model / "physics"
    multiphysics = model / "multiphysics"
    geometry = (model / "geometries").children()[0]

    elas = "elastic"
    if args.timedep:
        elas = "elastic1"
        models2 = json_get(data, "Models", "elastic2", "models")
        if not models2:
            models2 = [json_get(data, "Models", "elastic2")]

    models = json_get(data, "Models", elas, "models")
    if not models:
        models = [json_get(data, "Models", elas)]
    materials = data["Materials"]
    boundaries = json_get(data, "BoundaryConditions", elas, "Dirichlet")

    part_elastic = []
    part_electric = []
    for mod in models:
        part_elastic.extend(get_materials_markers(mod, materials))

        if "bool_laplace" in json_get(mod, "setup", "coefficients", "f"):
            part_electric.extend(get_materials_markers(mod, materials))

    if args.timedep:
        for mod in models2:
            if "bool_laplace" in json_get(mod, "setup", "coefficients", "f"):
                part_electric.extend(get_materials_markers(mod, materials))

    # create A formulation
    print("Info    :    Solid Mechanics")
    elastic = physics.create("SolidMechanics", geometry, name="Solid Mechanics")
    elastic.select(
        np.concatenate(
            [selection_import[si_markers][marker] for marker in part_elastic]
        )
    )

    lem = elastic / "Linear Elastic Material 1"
    lem.property("E_mat", "userdef")
    lem.property("nu_mat", "userdef")
    lem.property("rho_mat", "userdef")
    lem.property("E", "E")
    lem.property("nu", "nu")
    if args.timedep:
        lem.property("rho", "rho")

    if boundaries:
        print("Info    :    Dirichlet Boundary Conditions")
        component = {"x": ["1", "0", "0"], "y": ["0", "1", "0"], "z": ["0", "0", "1"]}
        for bound in boundaries:
            markers_bound = get_markers(bound, boundaries)
            if "component" in boundaries[bound]:
                Fixed = elastic.create(
                    f"Displacement{dim - 1}", dim - 1, name=f"Fixed Constraint {bound}"
                )
                Fixed.property("Direction", component[boundaries[bound]["component"]])
            else:
                Fixed = elastic.create(
                    "Fixed", dim - 1, name=f"Fixed Constraint {bound}"
                )
            Fixed.select(
                np.concatenate(
                    [selection_import[si_bound][marker] for marker in markers_bound]
                )
            )

    print("Info    :    Body Load")
    if dim == 2 and "magnetic" in equations:
        BodyLoad = elastic.create("BodyLoad", dim, name="Body Load")
        BodyLoad.select(
            np.concatenate(
                [selection_import[si_markers][marker] for marker in part_electric]
            )
        )
        if args.axis:
            BodyLoad.property("FperVol", ["u*mf.Bz", "0", "-u*mf.Br"])
        else:
            BodyLoad.property("FperVol", ["-u*mf.By", "-u*mf.Bx", "0"])
    else:
        for mod in models:
            if "f" in mod["setup"]["coefficients"]:
                BodyLoad = elastic.create(
                    "BodyLoad", dim, name=f"Body Load {json_get(mod,'name')}"
                )
                BodyLoad.select(
                    np.concatenate(
                        [
                            selection_import[si_markers][marker]
                            for marker in get_materials_markers(mod, materials)
                        ]
                    )
                )
                f_coef = (
                    mod["setup"]["coefficients"]["f"]
                    .replace("materials_", "")
                    .split(":")[0]
                )
                f_coef = feel_to_comsol_symbols(f_coef, unknowns)
                f_values = f_coef[f_coef.find("{") + 1 : f_coef.find("}")].split(",")
                if args.axis:
                    BodyLoad.property("FperVol", [f_values[0], "0", f_values[1]])
                elif dim == 2:
                    BodyLoad.property("FperVol", [f_values[0], f_values[1], "0"])
                elif dim == 3:
                    BodyLoad.property(
                        "FperVol", [f_values[0], f_values[1], f_values[2]]
                    )

    if "heat" in equations:
        print("Info    :    Thermal Expansion")
        thel = multiphysics.create(
            "ThermalExpansion", geometry, name="Thermal Expansion"
        )
        thel.select(
            np.concatenate(
                [selection_import[si_markers][marker] for marker in part_elastic]
            )
        )
        thel.property("alpha_mat", "userdef")
        thel.property("alpha", "alphaT")


def create_electric(
    model,
    equations: List[str],
    data: dict,
    dim: int,
    selection_import: dict,
    unknowns: dict,
    args,
):
    if dim == 2:
        si_markers = "surface"
        si_bound = "curve"
    elif dim == 3:
        si_markers = "volume"
        si_bound = "surface"

    print("Info    : Creating Electric Physic")
    physics = model / "physics"
    geometry = (model / "geometries").children()[0]

    models = json_get(data, "Models", "electric", "models")
    if not models:
        models = [json_get(data, "Models", "electric")]

    materials = data["Materials"]
    boundaries = json_get(data, "BoundaryConditions", "electric", "Dirichlet")

    part_electric = []
    for mod in models:
        part_electric.extend(get_materials_markers(mod, materials))

    # create A formulation
    electric = physics.create("ConductiveMedia", geometry, name="Electric Current")
    electric.select(
        np.concatenate(
            [selection_import[si_markers][marker] for marker in part_electric]
        )
    )

    cucn1 = electric / "Current Conservation 1"
    cucn1.property("sigma_mat", "userdef")
    cucn1.property("sigma", "sigma")

    if boundaries:
        print("Info    :    Dirichlet Boundary Conditions")
        for bound in boundaries:
            markers_bound = get_markers(bound, boundaries)

            expr = boundaries[bound]["expr"]
            if type(expr) == str:
                expr = expr.split(":")[0]

            ElecPot = electric.create(
                "ElectricPotential", dim - 1, name=f"Electric Potential {bound}"
            )
            ElecPot.select(
                np.concatenate(
                    [selection_import[si_bound][marker] for marker in markers_bound]
                )
            )
            ElecPot.property("V0", expr)


def create_nothing(
    model,
    equations: List[str],
    data: dict,
    dim: int,
    selection_import: dict,
    unknowns: dict,
    args,
):
    pass
