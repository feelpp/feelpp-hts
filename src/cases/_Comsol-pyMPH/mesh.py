import numpy as np
import gmsh
import mph
import json
import re
import os


def meshing_nastran(data, folder) :

    # Loading the geometry or mesh given by the json
    meshfilename=re.search('\$cfgdir\/(.*)', data["Meshes"]["cfpdes"]["Import"]["filename"]).group(1)
    if folder.endswith("/") :
        gmsh.open(folder+meshfilename)
    else :
        gmsh.open(folder+"/"+meshfilename)
    

    if meshfilename.endswith(".geo") :                          # if geometry is .geo
        gmsh.model.mesh.generate(2)                             # generating mesh
        bdffilename=meshfilename.removesuffix(".geo")+".bdf"
        gmsh.write(bdffilename)                                 # exporting in .bdf
    elif meshfilename.endswith(".msh") :                        # if geometry is .msh
        bdffilename=meshfilename.removesuffix(".msh")+".bdf"
        gmsh.write(bdffilename)                                 # exporting in .bdf

    gmsh.clear()
    
    return meshfilename, bdffilename

def import_mesh(model, bdffilename, axis=0) :
    ### Create empty geometry for the imported mesh
    print("Info    : Creating Geometry...")
    geometries = model/'geometries'
    geometry = geometries.create(2, name='geometry')
    if axis :
        geometry.java.axisymmetric(True) # axisymmetric model
    print("Info    : Done creating Geometry")

    ### Importing the mesh from a .nas file
    print("Info    : Importing Mesh...")
    meshes = model/'meshes'
    mesh1 = meshes.create(geometry, name='mesh1')
    imported=mesh1.create("Import")
    imported.property('source', 'nastran')
    imported.property('data', 'mesh')
    imported.property('facepartition', 'minimal')
    imported.property('filename', bdffilename)
    model.mesh() # Build the mesh in order to select its parts later
    print("Info    : Done importing Mesh")

def creating_selection(model, meshfilename, folder) :
    if folder.endswith("/") :
        gmsh.open(folder+meshfilename)
    else :
        gmsh.open(folder+"/"+meshfilename)

    # Checking if two physical groups have the same ID
    print("Info    : Checking Selections")
    selections = model/'selections'
    check_selection = [child.name() for child in selections.children()] 
    # print(check_selection)
    if len(check_selection) != len(np.unique(check_selection)) :
        print("ERROR   : Some physical lines and physical surface have the same ID")
        exit(1)
    else :
        print("Info    : Done checking Selections\n             --> Selections are valid")

    # Assigning the domain numbers of Comsol to the physical groups' names
    print("Info    : Creating Selection's dictionnary...")
    selection_import={}
    groups = gmsh.model.getPhysicalGroups()
    for g in groups :
        dim = g[0]
        tag = g[1]

        name = gmsh.model.getPhysicalName(dim, tag)
        ent = gmsh.model.getEntitiesForPhysicalGroup(dim,tag)
        tab = []
        for child in selections.children():
            for i in ent :
                if " "+str(i)+" " in child.name() and child.selection()[0] not in tab:
                    tab.append(child.selection()[0])
        selection_import[name]=tab

    print("Info    : Done creating Selection's dictionnary")
    # print(selection_import)
    gmsh.clear()
    # selection_import = import_mesh(model,data,axisymmetric)

    return selection_import