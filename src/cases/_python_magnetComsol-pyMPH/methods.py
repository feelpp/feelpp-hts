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

def dict_unknown(data: dict, equations: List[str], axis: bool = 0, timedep: bool = 0):
    create_dict = {
        "magnetic": create_dict_mag,
        "heat": create_dict_heat,
        "elastic": create_dict_elas,
        "elastic1": create_dict_elas,
        "elastic2": create_dict_elas,
    }

    feel_unknowns ={}
    for equation in equations :
        unknown=data["Models"][equation]["common"]["setup"]["unknown"]["symbol"]
        feel_unknowns=feel_unknowns | create_dict[equation](unknown, equation, axis)

    return feel_unknowns

def create_dict_mag(unknown, equation, axis: bool = 0):
    if axis :
        dict={
            f"{equation}_{unknown}": "mf.Aphi",
            f"{equation}_d{unknown}_dt": "d(mf.Aphi,t)",
            f"{equation}_grad_{unknown}_0": "d(mf.Aphi,r)",
            f"{equation}_grad_{unknown}_1": "d(mf.Aphi,z)"
        }
    else:
        dict={
            f"{equation}_{unknown}": "mf.Az",
            f"{equation}_d{unknown}_dt": "d(mf.Az,t)",
            f"{equation}_grad_{unknown}_0": "d(mf.Az,x)",
            f"{equation}_grad_{unknown}_1": "d(mf.Az,y)"
        }

    return dict

def create_dict_heat(unknown, equation, axis: bool = 0):
    if axis :
        dict={
            f"{equation}_{unknown}": "T",
            f"{equation}_d{unknown}_dt": "d(T,t)",
            f"{equation}_grad_{unknown}_0": "d(T,r)",
            f"{equation}_grad_{unknown}_1": "d(T,z)"
        }
    else:
        dict={
            f"{equation}_{unknown}": "T",
            f"{equation}_d{unknown}_dt": "d(T,t)",
            f"{equation}_grad_{unknown}_0": "d(T,x)",
            f"{equation}_grad_{unknown}_1": "d(T,y)"
        }

    return dict

def create_dict_elas(unknown, equation, axis: bool = 0):
    if axis :
        dict={
            f"{equation}_{unknown}": "u2",
            f"{equation}_d{unknown}_dt": "d(u2,t)",
            f"{equation}_grad_{unknown}_0": "d(u2,r)",
            f"{equation}_grad_{unknown}_1": "d(u2,z)"
        }
    else:
        dict={
            f"{equation}_{unknown}": "u2",
            f"{equation}_d{unknown}_dt": "d(u2,t)",
            f"{equation}_grad_{unknown}_0": "d(u2,x)",
            f"{equation}_grad_{unknown}_1": "d(u2,y)"
        }

    return dict

def create_group(model, tag: str, label: str, location: str, type: str):
    model.java.nodeGroup().create(tag, location)
    model.java.nodeGroup(tag).set("type", type)
    model.java.nodeGroup(tag).label(label)