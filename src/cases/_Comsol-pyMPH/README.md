# JSON to MPH

## Running as case

Requires Python MPH library to work:

Current version needs:
- a JSON CFPDES file with Meshes part giving the mesh name
- a MSH or GEO file

To run mqs_axis example :

```
python create_model.py --folder ./example/ --file mqs_axis.json --axis --timedep --solveit --openit
```

Options of create_model.py:
- "--folder": give the folder containing the json file
- "--file": give json file name
- "--formulation": give the formulation/physic to use (only "cfpdes" is implemented for now)
- "--axis": if the model is in axisymmetric coordinates, set this option
- "--nonlin": if the model is non linear, set this option
- "--timedep": if the model is time dependante, set this option
- "--solveit": to solve the model, set this option
- "--openit": to open the created file with comsol, set this option

[NOTE]
====
In the MSH, two physical groups must not have the same ID
====