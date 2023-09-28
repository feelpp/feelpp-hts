"""
Creates the demonstration model "capacitor" from scratch.

The code below uses the higher-level Python layer as much as possible
and falls back to the Java layer when functionality is (still) missing.

Requires Comsol 5.4 or newer.
"""

import numpy as np
import gmsh
import mph
import json
import re
import os


# from mesh import import_mesh 
from physics import physic_and_mat, results
from mesh import meshing_nastran, import_mesh, creating_selection
from parameters import parameters_and_functions

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--folder", help="give folder of json file", type=str)#, default="../../cylinder")
parser.add_argument("--file", help="give json file", type=str)#, default="mqs_axis.json")
parser.add_argument("--formulation", help="give formulation", type=str, default="cfpdes")
parser.add_argument("--axis", help="is the model in axisymmetric coord", action='store_true')
parser.add_argument("--nonlin", help="is the model non linear", action='store_true')
parser.add_argument("--timedep", help="is the model timedep", action='store_true')
parser.add_argument("--solveit", help="solve the model ?", action='store_true')
parser.add_argument("--openit", help="open with comsol ?", action='store_true')
args = parser.parse_args()

# Loading the json
if args.folder.endswith("/") :
    dir=args.folder
else :
    dir=args.folder+"/"

f = open(dir+args.file)
data = json.load(f)

equations = data["Models"]["cfpdes"]["equations"]
if type(equations) == str :
    equations=[equations]

gmsh.initialize()
# Loading the geometry or mesh given by the json
meshfilename, bdffilename = meshing_nastran(data, dir)

client = mph.start()
model = client.create(data["ShortName"]) # creating the mph model

### Create parameters
parameters_and_functions(model, data)

# model.java.variable().create("var1")

### Create component
model.java.modelNode().create("component");


### Importing the mesh
import_mesh(model, bdffilename, dir, args.axis)

### Creating selections
selection_import = creating_selection(model, meshfilename, dir)
gmsh.finalize()


# ### Create infinite element domain
# coordinates = model/'coordinates'
# ie1=coordinates.create(geometry,'InfiniteElement', name='Infinite Element Domain 1')
# ie1.select(selection_import['Air'][1])

# views = model/'views'
# view = views/'View 1'
# view.java.axis().label('axis')
# view.java.axis().set('xmin', -0.001)
# view.java.axis().set('xmax', +0.11)
# view.java.axis().set('ymin', -0.11)
# view.java.axis().set('ymax', +0.11)


### Create the physic and materials
physic_and_mat(model, data, selection_import, args.axis)

### Create time dependent solver
studies = model/'studies'
solutions = model/'solutions'
batches = model/'batches'
study = studies.create(name='Study 1')

if args.timedep :
    print("Info    : Creating Time-Dependent Solver..." )
    step = study.create('Transient', name='Time Dependent')
    step.property('tlist','range(0,0.1,tf)')
    solution = solutions.create(name='Solution 1')
    solution.java.study(study.tag())
    solution.java.attach(study.tag())
    solution.create('StudyStep', name='equations')
    solution.create('Variables', name='variables')
    solver = solution.create('Time', name='Time-Dependent Solver')
    solver.property('tlist', 'range(0, 0.1, tf)')
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

if args.solveit :
    print("Info    : Solving... ")
    model.solve()
    results(data,model,args.formulation)
    print("Info    : Done solving... ")

print("Info    : Creating "+data["ShortName"]+"_created.mph..." )
os.makedirs(dir+"res", exist_ok=True)
model.save(dir+"res/"+data["ShortName"]+'_created.mph')
print("Info    : Done creating "+data["ShortName"]+"_created.mph..." )

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
    print("Info    : Openning "+data["ShortName"]+"_created.mph on Comsol" )
    os.system('comsol -open '+dir+'res/'+data["ShortName"]+'_created.mph')
    print("Info    : "+data["ShortName"]+"_created.mph closed" )