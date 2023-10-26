# JSON to MPH

## Running as case

Requires Python MPH library to work:

Current version needs:
- a JSON CFPDES file with Meshes part giving the mesh name
- a MSH or GEO file

To run mqs_axis example :

```
python create_model.py example/hltest/hltest-cfpdes-thmagel_hcurl-Axi-sim.cfg --axi --I 31000.0 --openit --debug
```

Options of create_model.py:
- "cfgfile": input the cfg file
- "--I": give the applied current intensity
or 
- "--mdata": give a dict with the applied current intensities for each magnet (ex:'{"M10Bitters":21000.0, "M19020601":31000.0}')
- "--axis": if the model is in axisymmetric coordinates, set this option
- "--timedep": if the model is time dependante, set this option
- "--solveit": to solve the model, set this option
- "--openit": to open the created file with comsol, set this option
- "--debug": to display additionnal information, set this option

[NOTE]
====
In the MSH, two physical groups must not have the same ID
====