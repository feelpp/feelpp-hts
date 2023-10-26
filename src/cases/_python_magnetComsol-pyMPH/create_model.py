"""
Creates the demonstration model "capacitor" from scratch.

The code below uses the higher-level Python layer as much as possible
and falls back to the Java layer when functionality is (still) missing.

Requires Comsol 5.4 or newer.
"""

import sys
import numpy as np
import gmsh
import mph
import json
import re
import os
import argparse
import configparser
import pandas as pd

# from mesh import import_mesh 
from physics import create_physics
from mesh import meshing_nastran, import_mesh, creating_selection
from parameters import parameters_and_functions, material_variables
from methods import dict_unknown
from postproc import postprocessing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cfgfile", help="input cfg file", type=str)
    parser.add_argument("--I", help="give current intensity",type=float,default=31000.0)
    parser.add_argument("--mdata", help="specify current data", type=json.loads)
    parser.add_argument("--axis", help="is the model in axisymmetric coord", action='store_true')
    parser.add_argument("--nonlin", help="is the model non linear", action='store_true')
    parser.add_argument("--timedep", help="is the model timedep", action='store_true')
    parser.add_argument("--solveit", help="solve the model ?", action='store_true')
    parser.add_argument("--openit", help="open with comsol ?", action='store_true')
    parser.add_argument("--debug", help="add to print debug", action='store_true')
    args = parser.parse_args()

    pwd = os.getcwd()

    jsonmodel = ""
    meshmodel = ""
    feelpp_config = configparser.ConfigParser()
    basedir = None
    with open(args.cfgfile, "r") as inputcfg:
        feelpp_config.read_string("[DEFAULT]\n[main]\n" + inputcfg.read())
        feelpp_directory = feelpp_config["main"]["directory"]
        scale=1
        if "mesh.scale" in feelpp_config["cfpdes"]:
            scale=feelpp_config["cfpdes"]["mesh.scale"]

        basedir = os.path.dirname(args.cfgfile)
        if not basedir:
            basedir = "."
        os.makedirs(basedir+"/Comsol_res", exist_ok=True)

        jsonmodel = feelpp_config["cfpdes"]["filename"]
        jsonmodel = jsonmodel.replace(r"$cfgdir/", f"{basedir}/")
        print(f"Info    : jsonmodel={jsonmodel}")

        meshmodel = feelpp_config["cfpdes"]["mesh.filename"]
        meshmodel = meshmodel.replace(r"$cfgdir/", f"{basedir}/")
        print(f"Info    : meshmodel={meshmodel}")

        time=None
        if args.timedep:
            time=[feelpp_config["ts"]["time-initial"],feelpp_config["ts"]["time-step"],feelpp_config["ts"]["time-final"]]
            if args.debug:
                print("Debug   : (time-initial,time-step,time-initial)=", time)

    with open(jsonmodel, "r") as jsonfile:
        data = json.load(jsonfile)

    equations = data["Models"]["cfpdes"]["equations"]
    if type(equations) == str :
        equations=[equations]

    feel_unknowns = dict_unknown(data, equations, args.axis, args.timedep)
    
    if args.debug:
        print("Debug   : equations=", equations)

    gmsh.initialize()
    # Loading the geometry or mesh given by the json
    bdffilename = meshing_nastran(meshmodel, pwd+"/"+basedir,args.debug)

    client = mph.start()
    model = client.create(data["ShortName"]) # creating the mph model

    ### Create parameters
    parameters_and_functions(model, data["Parameters"], args.I, args.mdata, time, args.debug)

    ### Create component
    model.java.modelNode().create("component");


    ### Importing the mesh
    import_mesh(model, bdffilename, basedir, args.axis, scale, args.debug)

    ### Creating selections
    selection_import = creating_selection(model, meshmodel, args.debug)
    gmsh.finalize()

    # Create material variables
    material_variables(model, data["Materials"], feel_unknowns, selection_import, args.debug)


    ### Create the physic and materials
    create_physics(model, equations, data, selection_import, args)

    ### Create time dependent solver
    studies = model/'studies'
    solutions = model/'solutions'
    batches = model/'batches'
    study = studies.create(name='Study 1')

    if args.timedep :
        print("Info    : Creating Time-Dependent Solver..." )
        step = study.create('Transient', name='Time Dependent')
        step.property('tlist','range(time_initial,time_step,time_final)')
        solution = solutions.create(name='Solution 1')
        solution.java.study(study.tag())
        solution.java.attach(study.tag())
        solution.create('StudyStep', name='equations')
        solution.create('Variables', name='variables')
        solver = solution.create('Time', name='Time-Dependent Solver')
        solver.property('tlist', 'range(time_initial,time_step,time_final)')
        if args.nonlin :
            ## Special changes for non-linear models
            fcoupled = solver/'Fully Coupled'
            fcoupled.property('jtech', 'once')
            fcoupled.property('maxiter', '25')
            fcoupled.property('ntolfact', '0.1')


        print("Info    : Done creating Time-Dependent Solver..." )

        

    else :
        print("Info    : Creating Stationary Solver..." )
        step = study.create('Stationary', name='Stationary')
        # step.property('tlist','range(0,0.1,tf)')
        solution = solutions.create(name='Solution 1')
        solution.java.study(study.tag())
        solution.java.attach(study.tag())
        solution.create('StudyStep', name='equations')
        solution.create('Variables', name='variables')
        solver = solution.create('Stationary', name='Stationary Solver')
        # solver.property('tlist', 'range(0, 0.1, tf)')
        if args.nonlin :
            ## Special changes for non-linear models
            fcoupled = solver/'Fully Coupled'
            fcoupled.property('jtech', 'once')
            fcoupled.property('maxiter', '25')
            fcoupled.property('ntolfact', '0.1')
        print("Info    : Done creating Stationary Solver..." )

    postprocessing(model, equations, data, selection_import, args)
    if args.solveit :
        print("Info    : Solving... ")
        model.solve()
        # results(data,model,args.formulation)
        print("Info    : Done solving... ")

    name=os.path.split(args.cfgfile)[1].removesuffix(".cfg")
    print("Info    : Creating "+name+"_created.mph..." )
    if args.debug:
        print("Debug   : path="+pwd+'/'+basedir+"/Comsol_res/"+name+'_created.mph')
    model.save(pwd+'/'+basedir+"/Comsol_res/"+name+'_created.mph')
    print("Info    : Done creating "+name+"_created.mph..." )

    print("Info    : Disconnecting Client..." )
    client.remove(model)
    # client.disconnect()
    try:
        client.disconnect()
    except Exception:
        error = 'Error while disconnecting client at session clean-up.'
        exit(1)
    print("Info    : Client disconnected" )


    if args.openit :
        print("Info    : Openning "+name+"_created.mph on Comsol" )
        os.system('comsol -open '+basedir+'/Comsol_res/'+name+'_created.mph')
        print("Info    : "+name+"_created.mph closed" )


if __name__ == "__main__":
    sys.exit(main())
