import gmsh
import numpy as np
import os
from typing import List
from rich.progress import track


def meshing_nastran(meshmodel: str, dim: int, basedir: str, debug: bool = False) -> str:
    """Create bdf mesh from a .msh file or a .geo file

    Args:
        meshmodel (str): path & name of mesh file
        dim (int): geometry dimmension
        basedir (str): cfg directory
        debug (bool, optional): print debug. Defaults to False.

    Returns:
        str: bdf file name
    """
    # Loading the geometry or mesh given by the json
    gmsh.open(meshmodel)

    if meshmodel.endswith(".geo"):  # if geometry is .geo
        gmsh.model.mesh.generate(2)  # generating mesh
        if dim == 3:
            gmsh.model.mesh.generate(3)
        bdffilename = meshmodel.removesuffix(".geo") + ".bdf"
    elif meshmodel.endswith(".msh"):  # if geometry is .msh
        bdffilename = meshmodel.removesuffix(".msh") + ".bdf"

    bdffilename = os.path.split(bdffilename)[1]
    if debug:
        print(f"Debug   : bdffilename={bdffilename}")
    gmsh.write(f"{basedir}/Comsol_res/{bdffilename}")  # exporting in .bdf

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
    """import the bdf mesh in the Comsol model

    Args:
        model (str): mph file (pyComsol model)
        bdffilename (str): path & name of bdf mesh file
        basedir (str): cfg directory
        dim (int): geometry dimmension
        axis (bool, optional):  bool if model is axis. Defaults to 0.
        scale (float, optional): scale of the mesh. Defaults to 1.
        debug (bool, optional): print debug. Defaults to False.
    """
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
    imported.property("filename", f"{basedir}/Comsol_res/{bdffilename}")

    ### Add scaling if scale !=1 in cfg
    if scale != 1:
        scaling = imported.create("Transform")
        scaling.property("isotropic", scale)

    model.mesh()  # Build the mesh in order to select its parts later
    print("Info    : Done importing Mesh")


def creating_selection(model: str, meshmodel: str, debug: bool = False) -> dict:
    """Assigning the domain numbers of Comsol to the physical groups' names
    -> Dictionnary : GMSH physical group names <=> Comsol domains ID

    Args:
        model (str): mph file (pyComsol model)
        meshmodel (str): path & name of mesh file
        debug (bool, optional): print debug. Defaults to False.

    Returns:
        dict: dictionnary selection import
    """
    gmsh.open(meshmodel)

    selections = model / "selections"
    check_selection = [child.name() for child in selections.children()]
    if debug:
        print("Debug   : selection in Comsol: ", check_selection)

    # Assigning the domain numbers of Comsol to the physical groups' names
    # -> Dictionnary : GMSH physical group names <=> Comsol domains ID
    # print("Info    : Creating Selection's dictionnary...")
    selection_import = {"volume": {}, "surface": {}, "curve": {}}
    groups = gmsh.model.getPhysicalGroups()
    for i in track(
        range(len(groups)), description="Info    : Creating Selection's dictionnary "
    ):
        # for g in groups:
        g = groups[i]
        dim = g[0]
        tag = g[1]

        name = gmsh.model.getPhysicalName(dim, tag)
        ent = gmsh.model.getEntitiesForPhysicalGroup(dim, tag)

        tab = []
        # for child in selections.children():
        #     for i in ent:
        #         if " " + str(i) + " " in child.name() and child.selection()[0] not in tab:
        #             tab.append(child.selection()[0])

        if debug:
            print("Debug   : Entities: ", ent)
        for i in ent:  # for each entity of the marker, select comsol ID
            child_index = f"ID {str(i)} Import 1"
            child = selections / child_index
            tab.append(child.selection().tolist())
        if debug:
            print("Debug   :     selection: ", tab)

        if dim == 1:
            selection_import["curve"][name] = np.concatenate(tab)
        elif dim == 2:
            selection_import["surface"][name] = np.concatenate(tab)
        elif dim == 3:
            selection_import["volume"][name] = np.concatenate(tab)

    # print("Info    : Done creating Selection's dictionnary")
    if debug:
        print("Debug   : selection dictionnary: ", selection_import)
    gmsh.clear()

    return selection_import
