#!/usr/bin/env python

import os
import sys
import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json 


import sys
import os
import feelpp
from feelpp.toolboxes.core import *
from feelpp.toolboxes.cfpdes import *

### New function Simulate
def new_simulate(toolbox, export=True, buildModelAlgebraicFactory=True,data=None):
    ns=10                  
    tolAz=1e-9
    tolp=1e-9


    toolbox.init(buildModelAlgebraicFactory)
    #toolbox.printAndSaveInfo()
    meas=[]
    if toolbox.isStationary():
        Jc0=4.75e10
        th=1.e-6, 
        sw=1.8e-3
        I0=85.5
        

        p=[0]*10
        Ics=[0]*10

        pmax=np.max(p)
        while np.abs(pmax-1)>tolp :                 ## Ic criterion
            print("I0 = ",I0)
            err=1                                   ## Reset err variable
            while err > tolAz :                     ## Self consistency loop
                meas = []
                toolbox.solve()                     ## Run FEM problem
                if export:
                    toolbox.exportResults()
                if not toolbox.postProcessMeasures().empty():
                    meas.append(toolbox.postProcessMeasures().values())
                    
                print(meas)

                for j in range(0,ns) :              ## Ic and p value updated for each materials
                    Ics[j]=meas[0][f'Statistics_Ics_tape_{j}_integrate']   
                    p[j]=I0/Ics[j]
                    toolbox.addParameterInModelProperties(f"P{j}", p[j])
                    toolbox.updateParameterValues()
                    print(f"        P{j} = {p[j]}")

                err = meas[0]["Statistics_Linf_max"]
                print(err)

            pmax=np.max(p)
            I0=2*I0/(1+pmax)
            toolbox.addParameterInModelProperties("I0", I0)
            toolbox.updateParameterValues()

    else:
        if not toolbox.doRestart():
            toolbox.exportResults(toolbox.timeInitial())
        toolbox.startTimeStep()
        while not toolbox.timeStepBase().isFinished():
            if feelpp.Environment.isMasterRank():
                print("============================================================\n")
                print("time simulation: {}s/{}s with step: {}".format(toolbox.time(),toolbox.timeFinal(),toolbox.timeStep()))
                print("============================================================\n")
            toolbox.solve()
            if not toolbox.postProcessMeasures().empty():
                meas.append(toolbox.postProcessMeasures().values())
            if export:
                toolbox.exportResults()

            toolbox.updateTimeStep()
    return [toolbox.checkResults(),meas]
#######################################


app = feelpp.Environment(["myapp"], opts= toolboxes_options("coefficient-form-pdes", "cfpdes"),config=feelpp.localRepository(""))

feelpp.Environment.setConfigFile('/home/LNCMI-G/muzet/stage/2021-m2-lncmi-supermagnets/simulations/aform/Ic_Roebel/Roebel_init.cfg')
f = cfpdes(dim=2)
[ok,meas]=simulate(f)
f.checkResults()

s=1
c="AVG"
if s :
    c="MAX"
ns=10

n=21
E=0
Ec=1e-4

tolAz=1e-9
tolp=1e-9
I0=85.5

filename = '/home/LNCMI-G/muzet/stage/2021-m2-lncmi-supermagnets/simulations/aform/Ic_Roebel/Roebel.json'
with open(filename, 'r') as file:
    data = json.load(file)
    for j in range(0,ns) :
        data["Parameters"][f"P{j}"] = 0.9
        data["Parameters"]["I0"] = I0
    
        
os.remove(filename)
with open(filename, 'w') as file:
    json.dump(data, file, indent=4)



p=[0.9]*10
pn=[0.9]*10
Ics=[0]*10

pmax=np.max(p)
while np.abs(pmax-1)*s + abs(sum(pn)/ns-1)*(1-s)> tolp :                 ## Ic criterion
    print("I0 = ",I0)
    err=1                                   ## Reset err variable
    while err > tolAz :                     ## Self consistency loop
        """"""""
        feelpp.Environment.setConfigFile('/home/LNCMI-G/muzet/stage/2021-m2-lncmi-supermagnets/simulations/aform/Ic_Roebel/Roebel.cfg')
        f = cfpdes(dim=2)
        [ok,meas]=simulate(f)                   ## Run FEM problem
        """"""""
        with open(filename, 'r') as file:
            data = json.load(file)

            # print(meas)

            for j in range(0,ns) :              ## Ic and p value updated for each materials
                Ics[j]=meas[0][f'Statistics_Ics_tape_{j}_integrate']   
                p[j]=I0/Ics[j]
                data["Parameters"][f"P{j}"] = p[j]
                print(f"        P{j} = {p[j]}        Pn{j} = {pn[j]}")

        os.remove(filename)
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

        err = meas[0]["Statistics_Linf_max"]
        print("err=",err)

    for i in range(0,ns):
        pn[i]=p[i]**n

    E= sum(pn)/ns*Ec
    pmax=np.max(p)
    I0=2*I0/((1+pmax)*s+(1+(E/Ec)**(1/n))*(1-s))
    with open(filename, 'r') as file:
        data = json.load(file)
        data["Parameters"]["I0"] = I0

    os.remove(filename)
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
        
print(f"\n\nIc= {ns*I0} A ({c} criteria)")