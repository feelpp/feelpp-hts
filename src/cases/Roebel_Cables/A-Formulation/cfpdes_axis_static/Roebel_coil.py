#!/usr/bin/env python

import os
import sys
import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json

from typing import List, Union, Optional

import feelpp
from feelpp.toolboxes.core import *
from feelpp.toolboxes.cfpdes import *

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--filename", help="give name without extension", type=str, default="Roebel_coil"
)
parser.add_argument(
    "--mesh", help="give name without extension", type=str, default="Roebel_coil"
)
parser.add_argument("--criteria", help="give criteria", type=str, default="MAX")
parser.add_argument("--ns", help="give number of tapes", type=int, default=10)
parser.add_argument("--nt", help="give number of turns", type=int, default=9)
parser.add_argument("--ts", help="give turn-spacing", type=float, default=4e-3)
parser.add_argument("--ir", help="give inner_radius", type=float, default=4.3e-2)
parser.add_argument("--tolAz", help="give self-const tol", type=float, default=1e-9)
parser.add_argument("--tolp", help="give p tol", type=float, default=1e-6)
parser.add_argument("--I0", help="give initial guess I", type=float, default=80)
args = parser.parse_args()


def update_time(dftime, start: float, end: float) -> pd.DataFrame:
    return dftime.append({"time": end - start}, ignore_index=True)


def init_feelpp_env() -> tuple:
    app = feelpp.Environment(
        ["myapp"],
        opts=toolboxes_options("coefficient-form-pdes", "cfpdes"),
        config=feelpp.localRepository(""),
    )
    comm = feelpp.Environment.worldCommPtr()
    ncore = comm.globalSize()
    return app, comm, ncore


def run_FEM(filename: str):
    feelpp.Environment.setConfigFile(filename + ".cfg")
    f = cfpdes(dim=2)
    [ok, meas] = simulate(f)
    return meas


def path_jsonfile(filename: str) -> Union[str, str, str]:
    directory = os.getcwd()
    jsonfile = directory + "/" + filename + ".json"
    json_initfile = directory + "/" + filename + "_init.json"
    return directory, jsonfile, json_initfile


def update_meshname(
    meshname: str, ncore: int, jsonfile: str, json_initfile: str, comm
) -> str:
    if ncore == 1:
        meshfile = meshname + ".msh"
    else:
        meshfile = meshname + f"_p{ncore}.json"

    if comm.isMasterRank():
        with open(jsonfile, "r") as file:
            data = json.load(file)
            data["Meshes"]["cfpdes"]["Import"]["filename"] = "$cfgdir/" + meshfile
        os.remove(jsonfile)
        with open(jsonfile, "w") as file:
            json.dump(data, file, indent=4)

        with open(json_initfile, "r") as file:
            data = json.load(file)
            data["Meshes"]["cfpdes"]["Import"]["filename"] = "$cfgdir/" + meshfile
        os.remove(json_initfile)
        with open(json_initfile, "w") as file:
            json.dump(data, file, indent=4)

    return meshfile


def update_Ph5(Psave, m2d, p: List[float], ns: int, nt: int):
    for j in range(0, nt):
        for i in range(0, ns):
            Psave.on(
                range=feelpp.markedelements(m2d, f"tape_{j}{i}"),
                expr=feelpp.expr(f"{p[j*ns+i]}"),
            )
    Psave.save(directory, name="P")


def update_L(nt: int, inner_radius: float, ts: float) -> Union[List[float], float]:
    l = [0] * nt
    for j in range(0, nt):
        l[j] = 2 * np.pi * (inner_radius + ts * j)

    L = np.sum(l)
    return l, L


def update_I0(
    criteria: str,
    I0: float,
    p: List[float],
    l: List[float],
    L: float,
    n: int,
    Ec: float,
    ns: int,
    nt: int,
    jsonfile: str,
    init=False,
) -> Union[List[float], List[float], List[float], float]:
    pn = [0] * ns * nt
    avg = [0] * nt
    E = [0] * nt

    for j in range(0, nt):
        for i in range(0, ns):
            pn[j * ns + i] = p[j * ns + i] ** n

    for j in range(0, nt):
        for i in range(0, ns):
            avg[j] += p[j * ns + i] * np.abs(p[j * ns + i]) ** (n - 1)
        E[j] = Ec / ns * avg[j]

    sum_avg = 0
    for j in range(0, nt):
        sum_avg += avg[j] * l[j]

    pmax = np.max(p)
    if not init:
        if criteria == "SUM-AVG":
            Esum = 0
            for j in range(0, nt):
                Esum += E[j] * l[j]
            I0 = 2 * I0 / (1 + (Esum / Ec / L) ** (1 / n))
        elif criteria == "MAX":
            I0 = 2 * I0 / (1 + pmax)
        elif criteria == "MAX-AVG":
            Emax = np.max(E)
            I0 = 2 * I0 / +(1 + (Emax / Ec) ** (1 / n))
        else:
            exit("Criteria non reconnu")

    with open(jsonfile, "r") as file:
        data = json.load(file)
        data["Parameters"]["I0"] = I0

    os.remove(jsonfile)
    with open(jsonfile, "w") as file:
        json.dump(data, file, indent=4)

    return pmax, avg, sum_avg, I0


def Ic_criteria(
    criteria: str,
    pmax: float,
    L: float,
    avg: List[float],
    sum_avg: List[float],
    ns: int,
) -> float:
    if criteria == "SUM-AVG":
        return np.abs(sum_avg / L / ns - 1)
    elif criteria == "MAX":
        return np.abs(pmax - 1)
    elif criteria == "MAX-AVG":
        return np.abs(np.max(avg) / ns - 1)
    else:
        exit("Criteria non reconnu")


def update_p(meas, I0: float, ns: int, nt: int) -> List[float]:
    for j in range(0, nt):
        for i in range(0, ns):
            Ics = meas[0][f"Statistics_Ics_tape_{j}{i}_integrate"]
            p[j * ns + i] = I0 / Ics
    return p


def update_err(meas) -> float:
    return meas[0]["Statistics_Linf_max"]


dftime = pd.DataFrame(columns=["time"])
start_total = time.time()

### path for model files
directory, jsonfile, json_initfile = path_jsonfile(args.filename)


### Parameters
I0 = args.I0

p = [0] * args.ns * args.nt

with open(jsonfile, "r") as file:
    data = json.load(file)
    n = data["Parameters"]["n"]
    Ec = data["Parameters"]["Ec"]

### Initialize feelpp environment and comm pointer for parallel calc
app, comm, ncore = init_feelpp_env()

### load original mesh or partitionned mesh in the model
meshfile = update_meshname(args.mesh, ncore, jsonfile, json_initfile, comm)

### Creating .h5 for parameter P
m2d = feelpp.load(feelpp.mesh(dim=2), name=meshfile, verbose=1)
Xh = feelpp.functionSpace(space="Pch", mesh=m2d, order=1)
Psave = Xh.element()

update_Ph5(Psave, m2d, p, args.ns, args.nt)

### Initial simulation
start = time.time()
meas = run_FEM(args.filename + "_init")
end = time.time()
dftime = update_time(dftime, start, end)

### Update .h5 for parameter P
p = [0.9] * args.ns * args.nt
update_Ph5(Psave, m2d, p, args.ns, args.nt)

### parameters for incomming WHILE loop
if comm.isMasterRank():
    l, L = update_L(args.nt, args.ir, args.ts)
    pmax, avg, sum_avg, I0 = update_I0(
        args.criteria, I0, p, l, L, n, Ec, args.ns, args.nt, jsonfile, True
    )
else:
    l = None
    L = None
    pmax = None
    avg = None
    sum_avg = None
    I0 = None

l = comm.localComm().bcast(l, root=0)
L = comm.localComm().bcast(L, root=0)
pmax = comm.localComm().bcast(pmax, root=0)
avg = comm.localComm().bcast(avg, root=0)
sum_avg = comm.localComm().bcast(sum_avg, root=0)
I0 = comm.localComm().bcast(I0, root=0)

### WHILE loop for Ic criteria
while (
    Ic_criteria(args.criteria, pmax, L, avg, sum_avg, args.ns) > args.tolp
):  ## Ic criterion
    if comm.isMasterRank():  ## Reset err variable
        print("I0 = ", I0)
        err = 1
    else:
        err = None
    err = comm.localComm().bcast(err, root=0)

    while err > args.tolAz:  ## Self consistency loop
        start = time.time()
        meas = run_FEM(args.filename)
        end = time.time()
        dftime = update_time(dftime, start, end)

        if comm.isMasterRank():
            p = update_p(meas, I0, args.ns, args.nt)
            err = update_err(meas)

            print(f"err={err}                 I0={I0}")
        else:
            p = None
            err = None

        p = comm.localComm().bcast(p, root=0)
        err = comm.localComm().bcast(err, root=0)

        ### Update .h5 for parameter P
        update_Ph5(Psave, m2d, p, args.ns, args.nt)

    ### Update parameters for Ic criteria
    if comm.isMasterRank():
        pmax, avg, sum_avg, I0 = update_I0(
            args.criteria, I0, p, l, L, n, Ec, args.ns, args.nt, jsonfile
        )
    else:
        pmax = None
        sum_avg = None
        avg = None
        I0 = None

    pmax = comm.localComm().bcast(pmax, root=0)
    avg = comm.localComm().bcast(avg, root=0)
    sum_avg = comm.localComm().bcast(sum_avg, root=0)
    I0 = comm.localComm().bcast(I0, root=0)


if comm.isMasterRank():
    print(f"\n\nIc= {args.ns*I0} A ({args.criteria} criteria)")

    end_total = time.time()
    print(f"\n\nTotal Time = {end_total - start_total}")

    dftime = update_time(dftime, start_total, end_total)

    dftime.to_csv(f"Ic_{args.filename}.csv")

    os.remove(directory + "/P.h5")
