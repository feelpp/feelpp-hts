import numpy as np
from typing import List


def get_markers(material: str, materials: dict) -> List[str]:
    if "markers" in materials[material]:
        markers = materials[material]["markers"]

        if markers == "%1%":
            markers = materials[material][
                "index1"
            ]  # temporaire -> fix pour chaque marker

        elif type(markers) == str:
            markers = [markers]

        elif type(markers) == dict:
            name = markers["name"]
            if "index1" in markers:
                if type(markers["index1"]) == list:
                    index1, index2 = markers["index1"][0].split(":")
                else:
                    index1, index2 = markers["index1"].split(":")

                markers = []
                for i in range(int(index1), int(index2)):
                    markers.append(name.replace("%1%", str(i)))

            else:
                markers = [name]
    else:
        markers = [
            material
        ]  # if there is no markers the material is defined by the title

    return markers


def get_materials_markers(model_mat: str, materials: str):
    markers_list = []
    if type(model_mat["materials"]) == str:
        markers_list.extend(get_markers(model_mat["materials"], materials))
    else:
        for mat in model_mat["materials"]:
            markers_list.extend(get_markers(mat, materials))

    return markers_list


def dict_unknown(data: dict, equations: List[str], dim: int, axis: bool = 0) -> dict:
    eq_expr = {
        "heat": "T",
        "elastic": "u2",
        "elastic1": "u2",
        "elastic2": "u2",
        "electric": "V",
    }
    if axis:
        eq_expr["magnetic"] = "mf.Aphi"
    elif dim == 2:
        eq_expr["magnetic"] = "mf.Az"
    else:
        eq_expr["magnetic"] = "mf.A"

    feel_unknowns = {}
    for equation in equations:
        if "common" in data["Models"][equation]:
            unknown = data["Models"][equation]["common"]["setup"]["unknown"]["symbol"]
        else:
            unknown = data["Models"][equation]["setup"]["unknown"]["symbol"]
        feel_unknowns = feel_unknowns | create_dict(
            unknown, equation, eq_expr[equation], dim, axis
        )

    return feel_unknowns


def create_dict(
    unknown: str, equation: str, expr: str, dim: int, axis: bool = 0
) -> dict:
    dict = {
        f"{equation}_{unknown}": f"{expr}",
        f"{equation}_{unknown}_rt": f"{expr}",
        f"{equation}_d{unknown}_dt": f"d({expr},t)",
        f"{equation}_d{unknown}_rt_dt": f"d({expr},t)",
    }

    if equation == "electric":
        if axis:
            dict[f"{equation}_grad_{unknown}_0"] = f"ec.Er"
            dict[f"{equation}_grad_{unknown}_rt_0"] = f"ec.Er"
            dict[f"{equation}_grad_{unknown}_1"] = f"ec.Ez"
            dict[f"{equation}_grad_{unknown}_rt_1"] = f"ec.Ez"
        elif dim == 2:
            dict[f"{equation}_grad_{unknown}_0"] = f"ec.Ex"
            dict[f"{equation}_grad_{unknown}_rt_0"] = f"ec.Ex"
            dict[f"{equation}_grad_{unknown}_1"] = f"ec.Ey"
            dict[f"{equation}_grad_{unknown}_rt_1"] = f"ec.Ey"
    else:
        if axis:
            dict[f"{equation}_grad_{unknown}_0"] = f"d({expr},r)"
            dict[f"{equation}_grad_{unknown}_rt_0"] = f"d({expr},r)"
            dict[f"{equation}_grad_{unknown}_1"] = f"d({expr},z)"
            dict[f"{equation}_grad_{unknown}_rt_1"] = f"d({expr},z)"
        elif dim == 2:
            dict[f"{equation}_grad_{unknown}_0"] = f"d({expr},x)"
            dict[f"{equation}_grad_{unknown}_rt_0"] = f"d({expr},x)"
            dict[f"{equation}_grad_{unknown}_1"] = f"d({expr},y)"
            dict[f"{equation}_grad_{unknown}_rt_1"] = f"d({expr},y)"
        else:
            dict[f"{equation}_grad_{unknown}_00"] = f"d({expr}x,x)"
            dict[f"{equation}_grad_{unknown}_rt_00"] = f"d({expr}x,x)"
            dict[f"{equation}_grad_{unknown}_11"] = f"d({expr}y,y)"
            dict[f"{equation}_grad_{unknown}_rt_11"] = f"d({expr}y,y)"
            dict[f"{equation}_grad_{unknown}_22"] = f"d({expr}z,z)"
            dict[f"{equation}_grad_{unknown}_rt_22"] = f"d({expr}z,z)"
            dict[f"{equation}_grad_{unknown}_01"] = f"d({expr}x,y)"
            dict[f"{equation}_grad_{unknown}_rt_01"] = f"d({expr}x,y)"
            dict[f"{equation}_grad_{unknown}_10"] = f"d({expr}y,x)"
            dict[f"{equation}_grad_{unknown}_rt_10"] = f"d({expr}y,x)"
            dict[f"{equation}_grad_{unknown}_02"] = f"d({expr}x,z)"
            dict[f"{equation}_grad_{unknown}_rt_02"] = f"d({expr}x,z)"
            dict[f"{equation}_grad_{unknown}_20"] = f"d({expr}z,x)"
            dict[f"{equation}_grad_{unknown}_rt_20"] = f"d({expr}z,x)"
            dict[f"{equation}_grad_{unknown}_12"] = f"d({expr}y,z)"
            dict[f"{equation}_grad_{unknown}_rt_12"] = f"d({expr}y,z)"
            dict[f"{equation}_grad_{unknown}_21"] = f"d({expr}z,y)"
            dict[f"{equation}_grad_{unknown}_rt_21"] = f"d({expr}z,y)"
    return dict


def create_group(model, tag: str, label: str, location: str, type: str):
    model.java.nodeGroup().create(tag, location)
    model.java.nodeGroup(tag).set("type", type)
    model.java.nodeGroup(tag).label(label)
