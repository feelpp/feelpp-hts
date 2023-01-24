import numpy as np
# import gmsh
import mph
import json
import re
# import os

### Create parameters
def parameters_and_functions(model, data) :
    parameters = model/'parameters'
    functions = model/'functions'
    # (parameters/'Parameters 1').rename('parameters')
    if "Parameters" in data :                                   # export parameters from json if there is a section parameters
        print("Info    : Loading Parameters...")
        param = data["Parameters"]
        for p in param :
            if type(param[p])==str :
                model.parameter(p,param[p].split(":")[0])  # if the parameter is a str, keeping ononliny the expression part
            else :
                model.parameter(p,str(param[p]))

        print("Info    : Done loading Parameters")