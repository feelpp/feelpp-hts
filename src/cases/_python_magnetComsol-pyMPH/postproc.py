import numpy as np
import mph
import json
import re
from typing import List
from methods import get_markers, get_materials_markers, create_group


def postprocessing(model, equations: List[str], data: dict, selection_import: dict, args):
    ### Create the post-proc
    print("Info    : Creating Post-Processing...")

    export_method = {
        "magnetic": create_export_magnetic,
        "heat": create_export_heat,
        "elastic": create_export_elastic,
        "elastic1": create_export_elastic,
        "elastic2": create_nothing,
    }

    tab=model/'tables'
    plots = model/'plots'

    ### Browse equations and create corresponding post processing
    for eq in equations :
        export_method[eq](plots, args)
        tab.create("Table", name=f"{eq}_values")
        stat_method(eq,model, data, selection_import, args)
        
    print("Info    : Done creating Post-Processing")

def create_export_magnetic(plots, args):
    print("Info    :    Export Magnetic")

    create_export(plots, 'Magnetic field', 'normB', 'mf.normB')
    if args.axis:
        create_export(plots, 'Magnetic potential', 'Aphi', 'mf.Aphi')
        create_export(plots, 'Current Density', 'Jphi', 'u')
    else:
        create_export(plots, 'Magnetic potential', 'Az', 'mf.Az')
        create_export(plots, 'Current Density', 'Jz', 'u')

    
def create_export_heat(plots, args):
    print("Info    :    Export Heat")

    create_export(plots, 'Temperature', 'T', 'T')
    create_export(plots, 'Heat Source', 'Q', 'ht.Q')


def create_export_elastic(plots, args):
    print("Info    :    Export Elastic")

    create_export(plots, 'Displacement', 'disp', 'solid.disp')
    create_export(plots, 'Von Mises', 'vonmises', 'solid.mises')
    if args.axis:
        create_export(plots, 'Stress', 'stress', 'solid.srz')
        create_export(plots, 'Flaplace_0', 'force laplace r', 'u*mf.Bz')
        create_export(plots, 'Flaplace_1', 'force laplace z', '-u*mf.Br')
    else:
        create_export(plots, 'Stress', 'stress', 'solid.sxy')
        create_export(plots, 'Flaplace_0', 'force laplace x', '-u*mf.By')
        create_export(plots, 'Flaplace_1', 'force laplace y', '-u*mf.Bx')



def create_nothing(plots, args):
    pass

def create_export(plots, name: str, ID: str, expr:str):
    plot = plots.create('PlotGroup2D', name=name)
    plot.property('titletype', 'manual')
    plot.property('title', name)
    plot.property('showlegendsunit', True)
    surface = plot.create('Surface', name=ID)
    surface.property('resolution', 'normal')
    surface.property('expr', expr)


def stat_method(equation, model, data: dict, selection_import: dict, args):
    ### Statistics
    stats = data["PostProcess"][equation]["Measures"]["Statistics"]

    ### create node groups to sort measures
    if equation=="heat":
        create_group(model, "grp1","Power","Results","numerical")
        create_group(model, "grp2","Temperature","Results","numerical")
        create_group(model, "grp3","Flux","Results","numerical")
        create_group(model, "grp4","Intensity","Results","numerical")

    if equation=="elastic" or equation=="elastic1":
        create_group(model, "grp5","VonMises","Results","numerical")
        create_group(model, "grp6","Stress","Results","numerical")

    ### function dependending on the type of measures
    stat_fct ={
        "list":create_stat,
        "str":create_integrate
    }

    for stat in stats:
        typeoftype=type(stats[stat]["type"]).__name__ # usable with stat_fct
        if "%1%" in stat:
            typeofindex=type(stats[stat]["index1"])

            ## case 1 : markers="%1%" and index1==list of markers
            if typeofindex == list: 
                for mark in stats[stat]["index1"]:
                    markers=[mark]
                    statname=stat.replace("%1%",mark)
                    stat_fct[typeoftype](stat,stats, markers, statname, equation, model, selection_import, args)

            ## case 2 : markers=string+"%1%" and index1="int1:int2"
            elif typeofindex == str:
                marker=stats[stat]["markers"]
                index1,index2=stats[stat]["index1"].split(":")
                for i in range(int(index1),int(index2)):
                    markers=[marker.replace("%1%", str(i))]
                    statname=stat.replace("%1%",str(i))
                    stat_fct[typeoftype](stat,stats, markers, statname, equation, model, selection_import, args)
        else:
            markers = get_markers(stat,stats)
            if stat in markers:
                markers = None

            stat_fct[typeoftype](stat,stats, markers, stat, equation, model, selection_import, args)
        


def create_integrate(stat: str,stats:dict, markers: List[str], statname: str, equation:str, model, selection_import: dict, args):
    if args.debug:
        print(f"Info    :    Statistics {statname}")
    eval = model/'evaluations'

    stat_dict={
        "Flux":{
            "type":"IntLine",
            "selection":"curve",
            "expr":stats[stat]["expr"].replace("Channel%1%",markers[0]).replace("heat_T","T").replace("2*pi*x","2*pi*r").split(":")[0],
            "group":"grp3"
            },
        "Power":{
            "type":"IntSurface",
            "selection":"surface",
            "expr":"2*pi*r*ht.Q",
            "group":"grp1"
            },
        "MagneticEnergy":{
            "type":"IntSurface",
            "selection":"surface",
            "expr":"2*pi*mf.Aphi*u",
            "group":None
            },
        "Intensity":{
            "type":"IntSurface",
            "selection":"surface",
            "expr":f"u/N_{markers[0]}",
            "group":"grp4"
            }
    }

    for ts in stat_dict:
        if ts in stat:
            integrate=stat_dict[ts]
            inte=eval.create(integrate["type"],name=statname)
            inte.select(np.concatenate([selection_import[integrate["selection"]][marker] for marker in markers]))
            inte.property("expr",integrate["expr"])
            inte.property("descr",statname)
            inte.property("table", model/f'tables/{equation}_values')

            if integrate["group"]:
                model.java.nodeGroup(integrate["group"]).add("numerical", inte.tag())



def create_stat(stat: str,stats:dict, markers: List[str], statname: str, equation:str, model, selection_import: dict, args):
    if args.debug:
        print(f"Info    :    Statistics {statname}")
    eval = model/'evaluations'

    type_dict ={
        "min": "MinSurface",
        "max": "MaxSurface",
        "mean": "AvSurface",
    }
    if markers:
        typeofstat = stats[stat]["type"]
        for type in typeofstat:
            stat_dict={
                "T":{
                    "type":type_dict[type],
                    "expr":"T",
                    "group":"grp2"
                    },
                "Displ":{
                    "type":type_dict[type],
                    "expr":"solid.disp",
                    "group":None
                    },
                "VonMises":{
                    "type":type_dict[type],
                    "expr":"solid.mises",
                    "group":"grp5"
                    },
                "Stress":{
                    "type":type_dict[type],
                    "expr":"solid.sphi",
                    "group":"grp6"
                    }
            }
            for ts in stat_dict:
                if ts in stat:
                    surstat=stat_dict[ts]
                    sur=eval.create(surstat["type"],name=statname+type)
                    sur.select(np.concatenate([selection_import["surface"][marker] for marker in markers]))
                    sur.property("expr",surstat["expr"])
                    sur.property("descr",statname+type)
                    sur.property("table", model/f'tables/{equation}_values')

                    if surstat["group"]:
                        model.java.nodeGroup(surstat["group"]).add("numerical", sur.tag())