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

filename = os.getcwd()+'/Roebel_coil.json'

app = feelpp.Environment(["myapp"], opts= toolboxes_options("coefficient-form-pdes", "cfpdes"),config=feelpp.localRepository(""))

feelpp.Environment.setConfigFile('Roebel_coil_init.cfg')
f = cfpdes(dim=2)
[ok,meas]=simulate(f)
f.checkResults()

s=1
s1=1
c="MAX"
if s :
    if s1 :
        c="SUM-AVG"
    else :
        c="MAX-AVG"
ns=10

n=21
Ec=1e-4

inner_radius=4.3e-2
wg=4e-3

tolAz=1e-9
tolp=1e-6
I0=60

with open(filename, 'r') as file:
    data = json.load(file)
    for j in range(0,9) :
        for i in range(0,ns) :
            data["Parameters"][f"P{j}{i}"] = 0.9
        data["Parameters"]["I0"] = I0
    
        
os.remove(filename)
with open(filename, 'w') as file:
    json.dump(data, file, indent=4)



p=[0.9]*(ns*9)
avg=[0]*9
E=[0]*9
for j in range(0,9) :   
    for i in range(0,ns) :
        avg[j]+=p[j*10+i]*np.abs(p[j*10+i])**(n-1)
    E[j]=Ec/ns*avg[j]

l=[0]*9
for j in range(0,9) :
    l[j]=2*np.pi*(inner_radius+wg*j)

L=np.sum(l)

sum_avg=0
for j in range(0,9):
    sum_avg+=avg[j]*l[j] 

pmax=np.max(p)
while np.abs(pmax-1)*(1-s) + np.abs(np.max(avg)-ns)*s*(1-s1) + np.abs(sum_avg-L*ns)*s*s1> tolp :                    ## Ic criterion
    print("I0 = ",I0)
    err=1                                                                   ## Reset err variable
    while err > tolAz :                                                     ## Self consistency loop
        """"""""
        feelpp.Environment.setConfigFile('Roebel_coil.cfg')
        f = cfpdes(dim=2)
        [ok,meas]=simulate(f)                                               ## Run FEM problem
        """"""""
        with open(filename, 'r') as file:
            data = json.load(file)

            # print(meas)

            for j in range(0,9) :   
                for i in range(0,ns) :
                    Ics=meas[0][f'Statistics_Ics_tape_{j}{i}_integrate']   
                    p[j*10+i]=I0/Ics
                    data["Parameters"][f"P{j}{i}"] = p[j*10+i]
                    print(f"        P{j}{i} = {p[j*10+i]}")

        os.remove(filename)
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

        err = meas[0]["Statistics_Linf_max"]
        print(f"err={err}                 I0={I0}")

    for j in range(0,9) :   
        for i in range(0,ns) :
            avg[j]+=p[j*10+i]*np.abs(p[j*10+i])**(n-1)
        E[j]=Ec/ns*avg[j]

    Etest=sum(E)
    sum_avg=0
    for j in range(0,9):
        sum_avg+=avg[j]*l[j]

    Emax=np.max(E)
    Esum=0
    for j in range(0,9):
        Esum+=E[j]*l[j] 
    pmax=np.max(p)
    I0=2*I0/((1+pmax)*(1-s)+(1+Emax/Ec)*s*(1-s1)+(1+(Esum/Ec/L)**(1/n))*s*s1)
    with open(filename, 'r') as file:
        data = json.load(file)
        data["Parameters"]["I0"] = I0

    os.remove(filename)
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
        
print(f"\n\nIc= {ns*I0} A ({c} criteria)")