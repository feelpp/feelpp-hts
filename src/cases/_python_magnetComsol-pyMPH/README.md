# python_magnetComsol-pyMPH

This directory contain a python scrpit to create a Comsol model from a Feel++ CFPDEs model

## Requirement

Requires Python MPH library to work:

```bash
python -m venv --system-site-packages mph-env
source ./mph-env/bin/activate
pip install mph
```

## Running as case

The script needs the 3 files of a Feel++ CFPDEs model:
- a CFG file 
- a JSON file
- a MSH or GEO file

[NOTE]
====
If the CFPDEs model contains a field via a h5 file (ex: sigma.h5), run the FEEL++ model once first, as the script will create a csv file for the h5 files from Paraview.
===

To run mqs_axis example :

```bash
python create_model.py example/hltest/hltest-cfpdes-thmagel_hcurl-Axi-sim.cfg --axi --I 31000.0 --openit --debug
```

Options of create_model.py:
- "cfgfile": input the cfg file
- "--I": give the applied current intensity
or 
- "--mdata": give a dict with the applied current intensities for each magnet (ex:'{"M10Bitters":21000.0, "M19020601":31000.0}')
- "--axis": if the model is in axisymmetric coordinates, set this option (if 'Axi' in name of CFG file, this automatic)
- "--timedep": if the model is time dependant, set this option
- "--solveit": to solve the model and export the results, set this option
- "--openit": to open the created file with comsol, set this option
- "--debug": to display additionnal information, set this option

Comsol model file & exported results are in the cfg dir, in a folder 'Comsol_res'