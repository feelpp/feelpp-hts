import gmsh
import os
from typing import List


def meshing_nastran(meshmodel: str, basedir: str, debug: bool = False) -> str:

    # Loading the geometry or mesh given by the json
    gmsh.open(meshmodel)

    if meshmodel.endswith(".geo"):  # if geometry is .geo
        gmsh.model.mesh.generate(2)  # generating mesh
        bdffilename = meshmodel.removesuffix(".geo") + ".bdf"
    elif meshmodel.endswith(".msh"):  # if geometry is .msh
        bdffilename = meshmodel.removesuffix(".msh") + ".bdf"

    bdffilename = os.path.split(bdffilename)[1]
    if debug:
        print("Debug   : bdffilename=" + bdffilename)
    gmsh.write(basedir + "/Comsol_res/" + bdffilename)  # exporting in .bdf

    gmsh.clear()

    return bdffilename


def import_mesh(
    model: str,
    bdffilename: str,
    basedir: str,
    dim: int,
    axis: bool = 0,
    scale: float = 1,
    debug: bool = False,
):
    ### Create empty geometry for the imported mesh
    print("Info    : Creating Geometry...")
    geometries = model / "geometries"
    geometry = geometries.create(dim, name="geometry")
    if axis:
        geometry.java.axisymmetric(True)  # axisymmetric model
    print("Info    : Done creating Geometry")

    ### Importing the mesh from a .nas file
    print("Info    : Importing Mesh...")
    meshes = model / "meshes"
    mesh1 = meshes.create(geometry, name="mesh1")
    imported = mesh1.create("Import")
    imported.property("source", "nastran")
    imported.property("data", "mesh")
    imported.property("facepartition", "minimal")
    imported.property("filename", basedir + "/Comsol_res/" + bdffilename)

    ### Add scaling if scale !=1 in cfg
    if scale != 1:
        scaling = imported.create("Transform")
        scaling.property("isotropic", scale)

    model.mesh()  # Build the mesh in order to select its parts later
    print("Info    : Done importing Mesh")


def creating_selection(model: str, meshfilename: str, debug: bool = False) -> dict:
    gmsh.open(meshfilename)

    selections = model / "selections"
    check_selection = [child.name() for child in selections.children()]
    if debug:
        print("Debug   : selection in Comsol: ", check_selection)

    # Assigning the domain numbers of Comsol to the physical groups' names
    # -> Dictionnary : GMSH physical group names <=> Comsol domains ID
    print("Info    : Creating Selection's dictionnary...")
    selection_import = {"volume": {}, "surface": {}, "curve": {}}
    groups = gmsh.model.getPhysicalGroups()
    for g in groups:
        dim = g[0]
        tag = g[1]

        name = gmsh.model.getPhysicalName(dim, tag)
        ent = gmsh.model.getEntitiesForPhysicalGroup(dim, tag)

        tab = []
        # for child in selections.children():
        #     for i in ent :
        #         if " "+str(i)+" " in child.name() and child.selection()[0] not in tab:
        #             tab.append(child.selection()[0])

        if debug:
            print("Debug   : Entities: ", ent)
        for i in ent:
            child_index = "ID " + str(i) + " Import 1"
            child = selections / child_index
            if child.selection()[0] not in tab:
                tab.append(child.selection()[0])
        if debug:
            print("Debug   :     selection: ", tab)

        if dim == 1:
            selection_import["curve"][name] = tab
        elif dim == 2:
            selection_import["surface"][name] = tab
        elif dim == 3:
            selection_import["volume"][name] = tab

    print("Info    : Done creating Selection's dictionnary")
    if debug:
        print("Debug   : selection dictionnary: ", selection_import)
    gmsh.clear()
    # selection_import = import_mesh(model,data,axisymmetric)

    return selection_import
