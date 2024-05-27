"""
Creates Comsol mph file from a cfpdes cfg, json & geo/msh

The code below uses the higher-level Python layer as much as possible
and falls back to the Java layer when functionality is (still) missing.

Requires Comsol 5.4 or newer.
"""

import os
import sys
import gmsh
import mph
import json
import argparse
import configparser
import re
import time


from physics import create_physics
from mesh import meshing_nastran, import_mesh, creating_selection
from parameters import parameters_and_functions, material_variables, import_fields
from methods import dict_unknown, json_get
from postproc import postprocessing


def main():

    start_time = time.time()

    parser = argparse.ArgumentParser()
    parser.add_argument("cfgfile", help="input cfg file", type=str)
    parser.add_argument(
        "--I", help="give current intensity", type=float, default=31000.0
    )
    parser.add_argument("--mdata", help="specify current data", type=json.loads)
    parser.add_argument(
        "--axis", help="is the model in axisymmetric coord", action="store_true"
    )
    # parser.add_argument("--nonlin", help="is the model non linear", action='store_true')
    parser.add_argument("--timedep", help="is the model timedep", action="store_true")
    parser.add_argument("--solveit", help="solve the model ?", action="store_true")
    parser.add_argument("--openit", help="open with comsol ?", action="store_true")
    parser.add_argument("--debug", help="add to print debug", action="store_true")
    args = parser.parse_args()

    pwd = os.getcwd()

    jsonmodel = ""
    meshmodel = ""
    feelpp_config = configparser.ConfigParser()
    basedir = None
    with open(args.cfgfile, "r") as inputcfg:
        feelpp_config.read_string("[DEFAULT]\n[main]\n" + inputcfg.read())
        feelpp_directory = (
            os.path.expanduser("~") + "/feelppdb/" + feelpp_config["main"]["directory"]
        )

        basedir = os.path.dirname(args.cfgfile)
        name = os.path.split(args.cfgfile)[1].removesuffix(".cfg")
        if not basedir:
            basedir = "."
        os.makedirs(basedir + "/Comsol_res", exist_ok=True)

        if "case" in feelpp_config:
            dim = int(feelpp_config["case"]["dimension"])
        else:
            dim = int(feelpp_config["main"]["case.dimension"])

        jsonmodel = feelpp_config["cfpdes"]["filename"]
        jsonmodel = jsonmodel.replace(r"$cfgdir/", f"{basedir}/")
        print(f"Info    : jsonmodel={jsonmodel}")
        with open(jsonmodel, "r") as jsonfile:
            data = json.load(jsonfile)

        scale = 1
        if "mesh.filename" in feelpp_config["cfpdes"]:  # if mesh in cfg
            meshmodel = feelpp_config["cfpdes"]["mesh.filename"]
            if "mesh.scale" in feelpp_config["cfpdes"]:
                scale = feelpp_config["cfpdes"]["mesh.scale"]
        else:  # if mesh in json
            meshmodel = json_get(data, "Meshes", "cfpdes", "Import", "filename")
            scale = json_get(data, "Meshes", "cfpdes", "Import", "scale")
            if not scale:
                scale = 1

        meshmodel = meshmodel.replace(r"$cfgdir/", f"{basedir}/")
        if re.match(r".*_p\d+\.json", meshmodel):
            meshmodel = re.sub(r"_p\d+\.json", ".msh", meshmodel)
            # scale = 0.001
        print(f"Info    : meshmodel={meshmodel}")

        times = None
        if args.timedep:
            times = [
                feelpp_config["ts"]["time-initial"],
                feelpp_config["ts"]["time-step"],
                feelpp_config["ts"]["time-final"],
            ]
            if args.debug:
                print("Debug   : (time-initial,time-step,time-initial)=", times)

    if "Axi" in args.cfgfile.replace(basedir, "") and not args.axis:
        args.axis = True

    equations = json_get(data, "Models", "cfpdes", "equations")
    if type(equations) == str:
        equations = [equations]

    feel_unknowns = dict_unknown(data, equations, dim, args.axis)

    if args.debug:
        print("Debug   : equations=", equations)

    gmsh.initialize()
    # Loading the geometry or mesh given by the json
    bdffilename = meshing_nastran(meshmodel, dim, f"{pwd}/{basedir}", args.debug)

    client = mph.start()
    model = client.create(data["ShortName"])  # creating the mph model

    ### Create parameters
    params_unknowns = parameters_and_functions(
        model, data["Parameters"], basedir, args.I, args.mdata, times, args.debug
    )
    feel_unknowns.update(params_unknowns)

    fields = json_get(data, "Meshes", "cfpdes", "Fields")
    if fields:
        fields_unknowns = import_fields(
            model,
            fields,
            dim,
            f"{pwd}/{basedir}",
            feelpp_directory,
            args.axis,
        )
        feel_unknowns.update(fields_unknowns)

    ### Create component
    model.java.modelNode().create("component")

    ### Importing the mesh
    import_mesh(model, bdffilename, basedir, dim, args.axis, scale, args.debug)

    ### Creating selections
    selection_import = creating_selection(model, meshmodel, args.debug)
    gmsh.finalize()

    ### Create material variables
    material_variables(
        model, data["Materials"], feel_unknowns, selection_import, dim, args.debug
    )

    ### Create physics
    create_physics(model, equations, data, dim, selection_import, feel_unknowns, args)

    ### Create time dependent solver
    studies = model / "studies"
    solutions = model / "solutions"
    study = studies.create(name="Study 1")

    if args.timedep:
        print("Info    : Creating Time-Dependent Solver...")
        step = study.create("Transient", name="Time Dependent")
        step.property("tlist", "range(time_initial,time_step,time_final)")
    else:
        print("Info    : Creating Stationary Solver...")
        step = study.create("Stationary", name="Stationary")

    solution = solutions.create(name="Solution 1")
    solution.java.study(study.tag())
    solution.java.attach(study.tag())
    solution.create("StudyStep", name="equations")
    solution.create("Variables", name="variables")

    if args.timedep:
        solver = solution.create("Time", name="Time-Dependent Solver")
        solver.property("tlist", "range(time_initial,time_step,time_final)")
        print("Info    : Done creating Time-Dependent Solver...")

    else:
        solver = solution.create("Stationary", name="Stationary Solver")
        print("Info    : Done creating Stationary Solver...")

    ### Create post-processing
    postprocessing(model, equations, data, selection_import, dim, args)

    if args.solveit:
        print("Info    : Solving... ")
        start_solve = time.time()
        model.solve()
        end_solve = time.time()
        # results(data,model,args.formulation)
        print(f"Info    : Done solving - Solver time: {int(end_solve-start_solve)}s")
        print("Info    : Export Results... ")
        start_solve = time.time()
        eval = model / "evaluations"
        export = model / "export"
        tables = model / "tables"
        tab_dict = {}
        # add every evaluation result to the corresponding table
        for child in eval.children():
            name_tab = child.property("table")
            if name_tab not in tab_dict:
                # if table not initialised -> set result
                tab_dict[name_tab] = tables.children()[
                    int(re.sub(r"\D", "", name_tab)) - 1
                ]
                child.java.setResult()
            else:
                # if table initialised -> append result
                child.java.appendResult()

        os.makedirs(f"{basedir}/Comsol_res/tables", exist_ok=True)
        # create export of every tables
        for tab in tab_dict:
            exp = export.create(
                "Table", name=f"{str(tab_dict[tab]).replace('tables/','')}"
            )
            exp.property("table", f"{tab}")
            exp.property("filename", f"{pwd}/{basedir}/Comsol_res/{tab_dict[tab]}.csv")
            exp.java.run()

        end_solve = time.time()
        print(f"Info    : Done Export - Export time: {int(end_solve-start_solve)}s")

    print(f"Info    : Creating {name}_created.mph...")
    if args.debug:
        print(f"Debug   : path={pwd}/{basedir}/Comsol_res/{name}_created.mph")
    model.save(f"{pwd}/{basedir}/Comsol_res/{name}_created.mph")
    print(f"Info    : Done creating {name}_created.mph...")

    print("Info    : Disconnecting Client...")
    client.remove(model)
    try:
        client.disconnect()
    except Exception:
        error = "Error while disconnecting client at session clean-up."
        exit(error)
    print("Info    : Client disconnected")

    end_time = time.time()

    print(f"Info    : Model creation time: {int(end_time - start_time)}s")

    if args.openit:
        print(f"Info    : Openning {name}_created.mph on Comsol")
        os.system(f"comsol -open {basedir}/Comsol_res/{name}_created.mph")
        print(f"Info    : {name}_created.mph closed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
