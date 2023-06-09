#!/usr/bin/env python

import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--ncore", help="give nb of core", type=int, default=1)
parser.add_argument("--scale", help="give mesh scale", type=float, default=1)
args = parser.parse_args()

filename = "Roebel_coil"
directory = os.getcwd()

res = os.system(
    f"gmsh -2 -format msh2 {directory}/{filename}.geo -o {directory}/{filename}.msh"
)

res = os.system(
    f"feelpp_mesh_partitioner --ifile {directory}/{filename}.msh  --dim 2 --part {args.ncore} --mesh.scale {args.scale} --odir {directory}"
)
