import numpy as np
from typing import List
from methods import get_markers, create_group, json_get
from rich.progress import track


def postprocessing(
    model, equations: List[str], data: dict, selection_import: dict, dim: int, args
):
    ### Create the post-proc
    print("Info    : Creating Post-Processing...")

    export_method = {
        "magnetic": create_export_magnetic,
        "heat": create_export_heat,
        "elastic": create_export_elastic,
        "elastic1": create_export_elastic,
        "electric": create_export_electric,
    }

    tab = model / "tables"
    plots = model / "plots"

    ### Browse equations and create corresponding post processing
    for eq in equations:
        if eq != "elastic2":
            export_method[eq](plots, dim, equations, args)
            stats = json_get(data, "PostProcess", eq, "Measures", "Statistics")
            if stats:
                print(f"Info    :    Statistics {eq}")
                tab.create("Table", name=f"{eq}_values")
                stat_method(eq, model, stats, selection_import, dim, args)

    print("Info    : Done creating Post-Processing")


def create_export_magnetic(plots, dim: int, equations: str, args):
    print("Info    :    Export magnetic")

    create_export(plots, dim, "Magnetic field", "normB", "mf.normB")
    if args.axis:
        create_export(plots, dim, "Magnetic potential", "Aphi", "mf.Aphi")
        create_export(plots, dim, "Current Density", "Jphi", "u")
    elif dim == 2:
        create_export(plots, dim, "Magnetic potential", "Az", "mf.Az")
        create_export(plots, dim, "Current Density", "Jz", "u")
    else:
        create_export(plots, dim, "Magnetic potential", "A", "mf.normA")
        create_export(plots, dim, "Current Density", "J", "mf.normJ")


def create_export_heat(plots, dim: int, equations: str, args):
    print("Info    :    Export heat")

    create_export(plots, dim, "Temperature", "T", "T")
    create_export(plots, dim, "Heat Source", "Q", "ht.Q")


def create_export_electric(plots, dim: int, equations: str, args):
    print("Info    :    Export electric")

    create_export(plots, dim, "Electric Potential", "V", "V")
    create_export(plots, dim, "Electric Field", "E", "ec.normE")


def create_export_elastic(plots, dim: int, equations: str, args):
    print("Info    :    Export elastic")

    create_export(plots, dim, "Displacement", "disp", "solid.disp")
    create_export(plots, dim, "Von Mises", "vonmises", "solid.mises")
    if dim == 2:
        if args.axis:
            create_export(plots, dim, "Stress", "stress", "solid.srz")
        else:
            create_export(plots, dim, "Stress", "stress", "solid.sxy")
        create_export(
            plots,
            dim,
            "Flaplace",
            "force laplace",
            "sqrt(F_laplace_0^2+F_laplace_1^2)",
        )
    else:
        create_export(plots, dim, "Stress", "stress", "solid.sxyz")
        create_export(
            plots,
            dim,
            "Flaplace",
            "force laplace",
            "sqrt(F_laplace_0^2+F_laplace_1^2+F_laplace_2^2)",
        )


def create_nothing(plots, dim: int, equations: str, args):
    pass


def create_export(plots, dim: int, name: str, ID: str, expr: str):
    plot = plots.create(f"PlotGroup{dim}D", name=name)
    plot.property("titletype", "manual")
    plot.property("title", name)
    plot.property("showlegendsunit", True)
    if dim == 2:
        surface = plot.create("Surface", name=ID)
        surface.property("resolution", "normal")
        surface.property("expr", expr)
    else:
        volume = plot.create("Volume", name=ID)
        volume.property("resolution", "normal")
        volume.property("expr", expr)


def stat_method(equation, model, stats: dict, selection_import: dict, dim: int, args):
    ### Statistics
    if args.debug:
        print("Debug   : equation=", equation)

    ### create node groups to sort measures
    if equation == "heat":
        create_group(model, "grp1", "Power", "Results", "numerical")
        create_group(model, "grp2", "Temperature", "Results", "numerical")
        create_group(model, "grp3", "Flux", "Results", "numerical")
        create_group(model, "grp4", "Intensity", "Results", "numerical")

    if equation == "elastic" or equation == "elastic1":
        create_group(model, "grp5", "VonMises", "Results", "numerical")
        create_group(model, "grp6", "Stress", "Results", "numerical")

    ### function dependending on the type of measures
    stat_fct = {"list": create_stat, "str": create_integrate}

    for stat in stats:
        typeoftype = type(stats[stat]["type"]).__name__  # usable with stat_fct
        if "%1%" in stat:

            # print("Info    : Stat=", stat)
            index = stats[stat]["index1"]

            ## case 1 : markers="%1%" and index1==list of markers
            if isinstance(index, list):

                for i in track(
                    range(len(index)),
                    description=f"Info    :      Stat={stat}",
                ):
                    # for mark in index:
                    mark = index[i]
                    markers = [mark]
                    statname = stat.replace("%1%", mark)
                    stat_fct[typeoftype](
                        stat,
                        stats,
                        markers,
                        statname,
                        equation,
                        model,
                        selection_import,
                        dim,
                        args,
                    )

            ## case 2 : markers=string+"%1%" and index1="int1:int2"
            elif isinstance(index, str):
                marker = stats[stat]["markers"]
                index1, index2 = index.split(":")
                for i in track(
                    range(int(index1), int(index2)),
                    description=f"Info    :      Stat={stat}",
                ):
                    markers = [marker.replace("%1%", str(i))]
                    statname = stat.replace("%1%", str(i))
                    stat_fct[typeoftype](
                        stat,
                        stats,
                        markers,
                        statname,
                        equation,
                        model,
                        selection_import,
                        dim,
                        args,
                    )
        elif "%1_1%" in stat:
            ## case 3 : markers="marker%1_1%" and index1==list of list
            index = stats[stat]["index1"]
            marker = stats[stat]["markers"]
            if isinstance(marker, List):
                marker = marker[0]

            for i in track(
                range(len(index)),
                description=f"Info    :      Stat={stat}",
            ):
                id = index[i]
                statid = stat.replace("%1_1%", str(id[0]))
                statsid = {statid: stats[stat]}
                statsid[statid]["expr"] = (
                    statsid[statid]["expr"]
                    .replace("%1_1%", str(id[0]))
                    .replace("%1_2%", str(id[1]))
                )
                statsid[statid]["markers"] = [
                    marker.replace("%1_1%", str(id[0])).replace("%1_2%", str(id[1]))
                ]
                stat_fct[typeoftype](
                    statid,
                    statsid,
                    statsid[statid]["markers"],
                    statid,
                    equation,
                    model,
                    selection_import,
                    dim,
                    args,
                )
        else:
            if args.debug:
                print("Info    : Stat=", stat)
            markers = get_markers(stat, stats)
            if stat in markers:
                markers = None

            stat_fct[typeoftype](
                stat, stats, markers, stat, equation, model, selection_import, dim, args
            )


def create_integrate(
    stat: str,
    stats: dict,
    markers: List[str],
    statname: str,
    equation: str,
    model,
    selection_import: dict,
    dim: int,
    args,
):
    if args.debug:
        print(f"Info    :    Statistics {statname}")
    eval = model / "evaluations"
    if dim == 2:
        si_markers = "surface"
        si_bound = "curve"
        stat_dict = {
            "Flux": {
                "type": "IntLine",
                "selection": si_bound,
                "expr": stats[stat]["expr"]
                .replace("Channel%1%", markers[0])
                .replace("Channel%1_1%", markers[0])
                .replace("heat_T", "T")
                .replace("2*pi*x", "2*pi*r")
                .split(":")[0],
                "group": "grp3",
            },
            "Power": {
                "type": "IntSurface",
                "selection": si_markers,
                "expr": "2*pi*r*ht.Q",
                "group": "grp1",
            },
            "MagneticEnergy": {
                "type": "IntSurface",
                "selection": si_markers,
                "expr": "2*pi*mf.Aphi*u",
                "group": None,
            },
            "Intensity": {
                "type": "IntSurface",
                "selection": si_markers,
                "expr": f"u/N_{markers[0]}",
                "group": "grp4",
            },
        }
    elif dim == 3:
        si_markers = "volume"
        si_bound = "surface"
        stat_dict = {
            "Flux": {
                "type": "IntSurface",
                "selection": si_bound,
                "expr": stats[stat]["expr"]
                .replace("Channel%1%", markers[0])
                .replace("Channel%1_1%", markers[0])
                .replace("heat_T", "T")
                .replace("2*pi*x", "2*pi*r")
                .split(":")[0],
                "group": "grp3",
            },
            "Power": {
                "type": "IntVolume",
                "selection": si_markers,
                "expr": "ht.Q",
                "group": "grp1",
            },
            "MagneticEnergy": {
                "type": "IntVolume",
                "selection": si_markers,
                "expr": "",
                "group": None,
            },
            "Intensity": {
                "type": "IntSurface",
                "selection": si_bound,
                "expr": f"sigma*(Vx*nx+Vy*ny+Vz*nz)",
                "group": "grp4",
            },
        }

    for ts in stat_dict:
        if ts in stat:
            integrate = stat_dict[ts]
            inte = eval.create(integrate["type"], name=statname)
            inte.select(
                np.concatenate(
                    [
                        selection_import[integrate["selection"]][marker]
                        for marker in markers
                    ]
                )
            )
            inte.property("expr", integrate["expr"])
            inte.property("descr", statname)
            inte.property("table", model / f"tables/{equation}_values")

            if integrate["group"]:
                model.java.nodeGroup(integrate["group"]).add("numerical", inte.tag())


def create_stat(
    stat: str,
    stats: dict,
    markers: List[str],
    statname: str,
    equation: str,
    model,
    selection_import: dict,
    dim: int,
    args,
):
    if args.debug:
        print(f"Info    :    Statistics {statname}")
    eval = model / "evaluations"
    if dim == 2:
        si_markers = "surface"
        type_dict = {
            "min": "MinSurface",
            "max": "MaxSurface",
            "mean": "AvSurface",
        }
    elif dim == 3:
        si_markers = "volume"
        type_dict = {
            "min": "MinVolume",
            "max": "MaxVolume",
            "mean": "AvVolume",
        }

    if markers:
        typeofstat = stats[stat]["type"]
        for type in typeofstat:
            stat_dict = {
                "Stat_T": {"type": type_dict[type], "expr": "T", "group": "grp2"},
                f"T_\\w+": {"type": type_dict[type], "expr": "T", "group": "grp2"},
                "Displ": {"type": type_dict[type], "expr": "solid.disp", "group": None},
                "VonMises": {
                    "type": type_dict[type],
                    "expr": "solid.mises",
                    "group": "grp5",
                },
                "Stress": {
                    "type": type_dict[type],
                    "expr": "solid.sphi",
                    "group": "grp6",
                },
            }
            for ts in stat_dict:
                if ts in stat:
                    surstat = stat_dict[ts]
                    sur = eval.create(surstat["type"], name=statname + type)
                    sur.select(
                        np.concatenate(
                            [selection_import[si_markers][marker] for marker in markers]
                        )
                    )
                    sur.property("expr", surstat["expr"])
                    sur.property("descr", statname + type)
                    sur.property("table", model / f"tables/{equation}_values")

                    if surstat["group"]:
                        model.java.nodeGroup(surstat["group"]).add(
                            "numerical", sur.tag()
                        )
