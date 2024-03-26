import numpy as np
import pandas as pd
from typing import List
from methods import get_markers, get_materials_markers


### Create parameters
def parameters_and_functions(
    model,
    feel_parameters: dict,
    basedir: str,
    I: float = 31000.0,
    mdata: dict = None,
    time: List[float] = None,
    debug: bool = False,
):
    functions = model / "Functions"
    # export parameters from json
    print("Info    : Loading Parameters...")
    for p in feel_parameters:
        if type(feel_parameters[p]) == str:
            model.parameter(
                p, feel_parameters[p].split(":")[0]
            )  # if the parameter is a str, keeping only the expression part
        elif type(feel_parameters[p]) == dict:
            pass
            # if "filename" in feel_parameters[p]:
            # df = pd.read_csv(
            #     feel_parameters[p]["filename"].replace("$cfgdir/", basedir + "/")
            # )
            # fit = model.java.func().create(p, "Interpolation")
            # fit = functions.create("Interpolation", name=p)
            # print(row for index, row in df.iterrows())
            # fit.property("table", [df["r"], df["Bz"]])
            # fit.import_(feel_parameters[p]["filename"].replace("$cfgdir/", ""))
            # fit.remove("table", 0)
            # fit.property("funcname", p)

        else:
            model.parameter(p, str(feel_parameters[p]))

    # Time dependent parameters
    if time:
        model.parameter("time_initial", time[0])
        model.parameter("time_step", time[1])
        model.parameter("time_final", time[2])

    # Chosen I
    if mdata:
        for magnet in mdata:
            model.parameter(f"{magnet}_Imax", mdata[magnet])
    else:
        model.parameter("Imax", I)

    print("Info    : Done loading Parameters")


def material_variables(
    model,
    materials: dict,
    unknowns: dict,
    selection_import: dict,
    dim: int,
    debug: bool = False,
):
    if dim == 2:
        si_markers = "surface"
    elif dim == 3:
        si_markers = "volume"
    for mat in materials:
        model.java.component("component").variable().create("var_" + mat)
        model.java.component("component").variable("var_" + mat).label(mat)
        # model.java.variable("var_"+mat).model('component')

        markers = get_markers(mat, materials)

        # print(model.java.variable("var_"+mat).selection())
        model.java.component("component").variable("var_" + mat).selection().geom(2)
        model.java.component("component").variable("var_" + mat).selection().set(
            np.concatenate([selection_import[si_markers][ma] for ma in markers])
        )
        # for each materials in the json, creating the law and material in comsol
        print('Info    : Loading Parameters from material "' + mat + '"...')

        for p in materials[
            mat
        ]:  # loading additionnal parameters that could be in the material definition
            if p != "markers" and p != "filename":
                if type(materials[mat][p]) == str:
                    var = materials[mat][p].split(":")[0]
                    for word in unknowns:
                        var = var.replace(word, unknowns[word])

                    if "{" in var:
                        var = var[var.find("{") + 1 : var.find("}")].split(",")
                        for i in range(len(var)):
                            model.java.component("component").variable(
                                "var_" + mat
                            ).set(f"{p}_{i}", var[i])
                    else:
                        model.java.component("component").variable("var_" + mat).set(
                            p, var
                        )
                else:
                    model.java.component("component").variable("var_" + mat).set(
                        p, str(materials[mat][p])
                    )

            if p == "sigma":
                model.java.component("component").variable("var_" + mat).set(
                    "rho", "1/sigma"
                )
            elif p == "rho":
                model.java.component("component").variable("var_" + mat).set(
                    "sigma", "1/rho"
                )

        # print("Info    : Done loading Parameters from material \""+mat+"\"...")
