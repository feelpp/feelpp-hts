import numpy as np
import gmsh
import mph
import json
import re


def physic_and_mat(model, data, selection_import, axis=0) : 
    
    physics = model/'physics'
    materials = model/'materials'
    geometry = (model/'geometries').children()[0]
    equations = data["Models"]["cfpdes"]["equations"]
    if type(equations) == str :
        equations=[equations]
    functions = model/'functions'

    ### Create the physic and materials
    print("Info    : Creating Physics and Materials...")
    mater = data["Materials"]
    for mat in mater :
        model.java.component("component").variable().create("var_"+mat)
        # model.java.variable("var_"+mat).model('component')
        if "markers" in mater[mat] :  
                markers=mater[mat]["markers"]
        else :
            markers = mat  # if there is no markers the material is defined by the title

        if type(markers) == str :
            markers=[markers]
        
        # print(model.java.variable("var_"+mat).selection())
        model.java.component("component").variable("var_"+mat).selection().geom(2)
        model.java.component("component").variable("var_"+mat).selection().set(np.concatenate([selection_import[markers[i]] for i in range(len(markers))]))
        #for each materials in the json, creating the law and material in comsol
        print("Info    : Loading Parameters from material \""+mat+"\"...")
        for p in mater[mat] :  # loading additionnal parameters that could be in the material definition
            if p != "markers" :
                if type(mater[mat][p])==str :
                    model.java.component("component").variable("var_"+mat).set(p,mater[mat][p].split(":")[0])
                else :
                    model.java.component("component").variable("var_"+mat).set(p,str(mater[mat][p]))
        print("Info    : Done loading Parameters from material \""+mat+"\"...")

        
    letters = {'c':'c', 'beta':'be', 'a':'a', 'alpha':'al', 'f':'f', 'gamma':'ga', 'd':'da'}
    # eq_name = [equations[i]["name"] for i in range(len(equations))]  
    
    for eq in equations :
        cfpde = physics.create('CoefficientFormPDE', geometry, name='Coefficient Form PDE '+eq)
        models = data["Models"][eq]["models"]
        cf = cfpde/'Coefficient Form PDE 1'
        cf.property('f', '0')
        cf.property('c', '0')
        cf.property('da', '0')
        for mod in models :
            print("Info    : Creating physic for material \"" + mat +"\"..." )

            cf = cfpde.create('CoefficientFormPDE',2, name='CFPDE '+mod["materials"])
            if type(mod["materials"]) == str :
                if "markers" in mater[mod["materials"]] :  
                    markers=mater[mod["materials"]]["markers"]
                else :
                    markers = mod["materials"]  # if there is no markers the material is defined by the title

                if type(markers) == str :
                    markers=[markers]
            else :
                markers=[]
                for ma in mod["materials"] :
                    if "markers" in mater[mod["materials"]] :  
                        marker=mater[ma]["markers"]
                    else :
                        marker = ma  # if there is no markers the material is defined by the title

                    if type(markers) == str :
                        markers.append(markers)
                    else:
                        for o in marker :
                            markers.append(o)

            cf.select(np.concatenate([selection_import[markers[i]] for i in range(len(markers))]))
            cf.property('f', '0')
            cf.property('c', '0')
            cf.property('da', '0')
            for p in mod["setup"]["coefficients"]:
                if type(mod["setup"]["coefficients"][p]) == str :
                    expr = mod["setup"]["coefficients"][p].split(":")[0]
                else :
                    expr = str(mod["setup"]["coefficients"][p])

                if re.search('{(.*)}', expr) :
                    expr = re.search('{(.*)}', expr).group(1)
                    expr = expr.split(",")
                    if axis :
                        for i in range(len(expr)) : 
                            expr[i] = expr[i].replace('x','r')+'/r'
                else :
                    if axis :
                        expr = expr.replace('x','r')+'/r'

                cf.property(letters[p], expr)
            print("Info    : Done creating physic for material \"" + mod["materials"] +"\"" )

        # loading boundary conditions (only dirichlet for now)
        print("Info    : Creating Boundary Conditions..." )
        index=1
        # for i in range(len(equations)) :
        if 'Dirichlet' in data["BoundaryConditions"][eq] :
            Bc = data["BoundaryConditions"][eq]["Dirichlet"]
            
            for b in Bc :
                
                if "markers" in Bc[b] :
                    markers=Bc[b]["markers"]
                else :
                    markers = b

                if type(markers) == str :
                    markers=[markers]

                expr = Bc[b]["expr"]
                if type(expr) == str :
                    expr = expr.split(":")[0]  # keeping only the expression part
                else : 
                    expr = str(expr)

                dir = cfpde.create('DirichletBoundary',1, name='Dirichlet Boundary Condition  '+str(index))
                dir.select(np.concatenate([selection_import[markers[i]] for i in range(len(markers))]))
                dir.property('r', expr)
                index=index+1
        print("Info    : Done creating Boundary Conditions" )
        
print("Info    : Done creating Physics and Materials")


def results(data, model, formulation):
    plots = model/'plots'
    if formulation == 'hform' :
        # plots.java.setOnlyPlotWhenRequested(True)
        plot = plots.create('PlotGroup2D', name='Magnetic field')
        plot.property('titletype', 'manual')
        plot.property('title', 'Magnetic field')
        plot.property('showlegendsunit', True)
        surface = plot.create('Surface', name='normB')
        surface.property('resolution', 'normal')
        surface.property('expr', 'mfh.normB')

        plot = plots.create('PlotGroup2D', name='Current Density')
        plot.property('titletype', 'manual')
        plot.property('title', 'Current Density')
        plot.property('showlegendsunit', True)
        surface = plot.create('Surface', name='Jphi')
        surface.property('resolution', 'normal')
        surface.property('expr', 'mfh.Jphi')
        
    if formulation == 'cfpdes' :
        # plots.java.setOnlyPlotWhenRequested(True)
        plot = plots.create('PlotGroup2D', name='Magnetic Potential')
        plot.property('titletype', 'manual')
        plot.property('title', 'Magnetic Potential')
        plot.property('showlegendsunit', True)
        surface = plot.create('Surface', name='potential')
        surface.property('resolution', 'normal')
        surface.property('expr', 'u')
        
        plot = plots.create('PlotGroup2D', name='Magnetic field')
        plot.property('titletype', 'manual')
        plot.property('title', 'Magnetic field')
        plot.property('showlegendsunit', True)
        surface = plot.create('Surface', name='normB')
        surface.property('resolution', 'normal')
        surface.property('expr', 'sqrt(d(u,r)^2+d(u,z)^2)')

        plot = plots.create('PlotGroup2D', name='Current Density')
        plot.property('titletype', 'manual')
        plot.property('title', 'Current Density')
        plot.property('showlegendsunit', True)
        surface = plot.create('Surface', name='Jphi')
        surface.property('resolution', 'normal')
        surface.property('expr', '-sigma*(U(t)/2/pi+d(u,t))')
        