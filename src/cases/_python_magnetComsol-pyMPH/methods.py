import numpy as np
# import gmsh
import mph
import json
import re
from typing import List
# import os

def get_markers(material: str, materials: dict) -> List[str]:
    if "markers" in materials[material] :  
        markers=materials[material]["markers"]
    else :
        markers = material  # if there is no markers the material is defined by the title

    if markers == '%1%':
        markers=materials[material]["index1"] # temporaire -> fix pour chaque marker
    elif type(markers) == str:
        markers=[markers]
    elif type(markers) == dict:
        name=markers["name"]
        if "index1" in markers:
            if type(markers["index1"])==list:
                index1,index2=markers["index1"][0].split(":")
            else:
                index1,index2=markers["index1"].split(":")
            markers=[]
            for i in range(int(index1),int(index2)):
                markers.append(name.replace("%1%",str(i)))
        else :
            markers = [name]

    return markers

def get_materials_markers(model_mat: str, materials: str):
    markers_list=[]
    if type(model_mat["materials"]) == str :
        markers_list.extend(get_markers(model_mat["materials"],materials))
    else:
        for mat in model_mat["materials"] :
            markers_list.extend(get_markers(mat,materials))
    
    return markers_list

def dict_unknown(data: dict, equations: List[str], axis: bool = 0):
    eq_expr = {
        "heat": "T",
        "elastic": "u2",
        "elastic1": "u2",
        "elastic2": "u2",
    }
    if axis:
        eq_expr["magnetic"]="mf.Aphi"
    else:
        eq_expr["magnetic"]="mf.Az"

    feel_unknowns ={}
    for equation in equations :
        unknown=data["Models"][equation]["common"]["setup"]["unknown"]["symbol"]
        feel_unknowns=feel_unknowns | create_dict(unknown, equation, eq_expr[equation], axis)

    return feel_unknowns

def create_dict(unknown: str, equation: str, expr:str, axis: bool = 0):
    dict={
            f"{equation}_{unknown}": f"{expr}",
            f"{equation}_{unknown}_rt": f"{expr}",
            f"{equation}_d{unknown}_dt": f"d({expr},t)",
            f"{equation}_d{unknown}_rt_dt": f"d({expr},t)"
        }
     
    if axis :
        dict[f"{equation}_grad_{unknown}_0"]= f"d({expr},r)"
        dict[f"{equation}_grad_{unknown}_rt_0"]= f"d({expr},r)"
        dict[f"{equation}_grad_{unknown}_1"]= f"d({expr},z)"
        dict[f"{equation}_grad_{unknown}_rt_1"]= f"d({expr},z)"
    else:
        dict[f"{equation}_grad_{unknown}_0"]= f"d({expr},x)"
        dict[f"{equation}_grad_{unknown}_rt_0"]= f"d({expr},x)"
        dict[f"{equation}_grad_{unknown}_1"]= f"d({expr},y)"
        dict[f"{equation}_grad_{unknown}_rt_1"]= f"d({expr},y)"
    return dict


def create_group(model, tag: str, label: str, location: str, type: str):
    model.java.nodeGroup().create(tag, location)
    model.java.nodeGroup(tag).set("type", type)
    model.java.nodeGroup(tag).label(label)