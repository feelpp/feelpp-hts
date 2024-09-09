import os
import numpy as np
import pandas as pd
from methods import get_markers, feel_to_comsol_symbols
from paraview.simple import EnSightReader, SaveData


### Create parameters
def parameters_and_functions(
    model,
    feel_parameters: dict,
    basedir: str,
    I: float = 31000.0,
    mdata: dict = None,
    times: list[float] = None,
    debug: bool = False,
) -> dict:
    """Create parameters in Comsol

    Args:
        model: mph file (pyComsol model)
        feel_parameters (dict): dict of parameters from FEEL++ model
        basedir (str): cfg directory
        I (float, optional): applied current. Defaults to 31000.0.
        mdata (dict, optional): applied current if more than 1 magnet. Defaults to None.
        times (list[float], optional): time parameters if model is time dependant. Defaults to None.
        debug (bool, optional): print debug. Defaults to False.

    Returns:
        dict: dict of parameters unknowns
    """

    params_unknowns = {}
    # export parameters from json
    print("Info    : Loading Parameters...")
    for p in feel_parameters:
        if type(feel_parameters[p]) == str:
            model.parameter(
                p, feel_parameters[p].split(":")[0]
            )  # if the parameter is a str, keeping only the expression part
        elif type(feel_parameters[p]) == dict:
            if "filename" in feel_parameters[p]:
                model.java.func().create(p, "Interpolation")
                model.java.func(p).set("source", "file")
                model.java.func(p).set(
                    "filename",
                    feel_parameters[p]["filename"].replace("$cfgdir/", basedir + "/"),
                )
                model.java.func(p).label(f"fit {p}")
                params_unknowns[p] = f"{p}({feel_parameters[p]['expr'].split(':')[0]})"
        else:
            model.parameter(p, str(feel_parameters[p]))

    # Time dependent parameters
    if times:
        model.parameter("time_initial", times[0])
        model.parameter("time_step", times[1])
        model.parameter("time_final", times[2])

    # Chosen I
    if mdata:
        for magnet in mdata:
            model.parameter(f"{magnet}_Imax", mdata[magnet])
    else:
        model.parameter("Imax", I)

    print("Info    : Done loading Parameters")
    return params_unknowns


def material_variables(
    model,
    materials: dict,
    unknowns: dict,
    selection_import: dict,
    dim: int,
    debug: bool = False,
):
    """Create parameters for materials (variables)

    Args:
        model: mph file (pyComsol model)
        materials (dict): dict of materials from FEEL++ model
        unknowns (dict): dict that translate feelpp symbols into Comsol symbols
        selection_import (dict): dict that translate feelpp markers into Comsol markers
        dim (int): geometry dimmension
        debug (bool, optional): print debug. Defaults to False.
    """
    if dim == 2:
        si_markers = "surface"
    elif dim == 3:
        si_markers = "volume"
    for mat in materials:
        model.java.component("component").variable().create(f"var_{mat}")
        model.java.component("component").variable(f"var_{mat}").label(mat)
        # model.java.variable("var_"+mat).model('component')

        markers = get_markers(mat, materials)

        # print(model.java.variable("var_"+mat).selection())
        model.java.component("component").variable(f"var_{mat}").selection().geom(dim)
        model.java.component("component").variable(f"var_{mat}").selection().set(
            np.concatenate([selection_import[si_markers][ma] for ma in markers])
        )
        # for each materials in the json, creating the law and material in comsol
        print(f'Info    : Loading Parameters from material "{mat}"...')

        for p in materials[
            mat
        ]:  # loading additionnal parameters that could be in the material definition
            if p != "markers" and p != "filename":
                if type(materials[mat][p]) == str:
                    var = materials[mat][p].split(":")[0]

                    # if var is a vector, separate it in its parts
                    if "{" in var:
                        var = var[var.find("{") + 1 : var.find("}")].split(",")
                        for i in range(len(var)):
                            var[i] = feel_to_comsol_symbols(var[i], unknowns)
                            model.java.component("component").variable(
                                f"var_{mat}"
                            ).set(f"{p}_{i}", var[i])
                    # if var is scalar/ expr
                    else:
                        var = feel_to_comsol_symbols(var, unknowns)
                        model.java.component("component").variable(f"var_{mat}").set(
                            p, var
                        )

                else:
                    model.java.component("component").variable(f"var_{mat}").set(
                        p, str(materials[mat][p])
                    )

            # if electric conductiviy/resitivity create electric resistivity/conductivy
            if p == "sigma":
                model.java.component("component").variable(f"var_{mat}").set(
                    "rho", "1/sigma"
                )
            elif p == "rho":
                model.java.component("component").variable(f"var_{mat}").set(
                    "sigma", "1/rho"
                )

        # print(f'Info    : Done loading Parameters from material "{mat}"...')


def import_fields(
    model,
    Fields: dict,
    dim: int,
    basedir: str,
    feelpp_directory: str,
    axis: bool,
    debug: bool = False,
) -> dict:
    """import h5 fields in Comsol
    -> instead of importing h5, load Export.case and creat a csv, then load the parts of the csv as interpolations

    Args:
        model: mph file (pyComsol model)
        Fields (dict): dict of Fields from FEEL++ model
        dim (int): geometry dimmension
        basedir (str): cfg directory
        feelpp_directory (str): directory of FEEL++ results for the model
        axis (bool): bool if model is axis
        debug (bool, optional): print debug. Defaults to False.

    Returns:
        dict: dict of fields unknowns
    """
    # instead of importing h5, load Export.case and creat a csv, then load the parts of the csv as interpolations
    fields_unknowns = {}
    for f in Fields:
        file = (
            Fields[f]["filename"]
            .replace("$cfgdir", f"{basedir}/Comsol_res")
            .replace(".h5", ".csv")
        )

        if "v" in Fields[f]["basis"]:
            paraview_export(f, file, feelpp_directory)
            for i in range(dim):
                filei = file.replace(".csv", f"_{i}.csv")
                if os.path.exists(filei):
                    df = pd.read_csv(file)
                    col_to_drop = [f"cfpdes.expr.{f}:{j}" for j in range(3) if j != i]
                    df.drop(
                        columns=col_to_drop,
                        inplace=True,
                    )
                    df.to_csv(filei, index=False)

                # feelpp symbols need to be replaced with corresponding comsol symbols
                if axis:
                    fields_unknowns[f"meshes_cfpdes_fields_{f}_{i}"] = (
                        f"meshes_cfpdes_fields_{f}_{i}(r,z,0)"
                    )
                elif dim == 2:
                    fields_unknowns[f"meshes_cfpdes_fields_{f}_{i}"] = (
                        f"meshes_cfpdes_fields_{f}_{i}(x,y,0)"
                    )
                else:
                    fields_unknowns[f"meshes_cfpdes_fields_{f}_{i}"] = (
                        f"meshes_cfpdes_fields_{f}_{i}(x,y,z)"
                    )

                model.java.func().create(
                    f"meshes_cfpdes_fields_{f}_{i}", "Interpolation"
                )
                model.java.func(f"meshes_cfpdes_fields_{f}_{i}").set("source", "file")
                model.java.func(f"meshes_cfpdes_fields_{f}_{i}").importData()
                model.java.func(f"meshes_cfpdes_fields_{f}_{i}").set("filename", filei)
                model.java.func(f"meshes_cfpdes_fields_{f}_{i}").label(
                    f"Meshes Field {f}_{i}"
                )
            os.remove(file)

        elif f != "U":
            paraview_export(f, file, feelpp_directory)

            if axis:
                fields_unknowns[f"meshes_cfpdes_fields_{f}"] = (
                    f"meshes_cfpdes_fields_{f}(r,z,0)"
                )
            elif dim == 2:
                fields_unknowns[f"meshes_cfpdes_fields_{f}"] = (
                    f"meshes_cfpdes_fields_{f}(x,y,0)"
                )
            else:
                fields_unknowns[f"meshes_cfpdes_fields_{f}"] = (
                    f"meshes_cfpdes_fields_{f}(x,y,z)"
                )
            model.java.func().create(f"meshes_cfpdes_fields_{f}", "Interpolation")
            model.java.func(f"meshes_cfpdes_fields_{f}").set("source", "file")
            model.java.func(f"meshes_cfpdes_fields_{f}").importData()
            model.java.func(f"meshes_cfpdes_fields_{f}").set("filename", file)
            model.java.func(f"meshes_cfpdes_fields_{f}").label(f"Meshes Field {f}")
            # model.java.func(f"meshes_cfpdes_fields_{f}").importData()

    return fields_unknowns


def paraview_export(field: str, file: str, feelpp_directory: str):
    """export csv in paraview for comsol interpolation

    Args:
        field (str): field name
        file (str): file name
        feelpp_directory (str): feelpp directory
    """
    print(
        f'Info    : Loading Interpolation from field "meshes_cfpdes_fields_{field}"...'
    )
    exportcase = EnSightReader(
        registrationName="Export.case",
        CaseFileName=f"{feelpp_directory}/np_1/cfpdes.exports/Export.case",
    )

    # print(f"save data {file}")
    SaveData(
        file,
        proxy=exportcase,
        ChooseArraysToWrite=1,
        PointDataArrays=[
            f"cfpdes.expr.{field}",
        ],
    )
