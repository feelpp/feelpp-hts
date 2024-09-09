import re


def get_markers(jsonkey: str, jsonsubdict: dict) -> list[str]:
    """find markers from a dict of the FEEL++ json file (from materials, statistic in post processing...)

    Args:
        jsonkey (str): key from which you want the markers
        jsonsubdict (dict): sub dictionnary of the json file containing the jsonkey

    Returns:
        list[str]: lis of markes
    """

    markers = json_get(jsonsubdict, jsonkey, "markers")
    if markers:
        if markers == "%1%":
            markers = jsonsubdict[jsonkey][
                "index1"
            ]  # temporaire -> fix pour chaque marker

        elif isinstance(markers, str):
            markers = [markers]

        elif isinstance(markers, dict):
            name = markers["name"]
            if "index1" in markers:
                if isinstance(markers["index1"], list):
                    index1, index2 = markers["index1"][0].split(":")
                else:
                    index1, index2 = markers["index1"].split(":")

                markers = []
                for i in range(int(index1), int(index2)):
                    markers.append(name.replace("%1%", str(i)))

            else:
                markers = [name]
    else:
        markers = [jsonkey]  # if there is no markers the marker is defined by the title

    return markers


def get_materials_markers(model_mat: dict, materials: dict) -> list[str]:
    """find markers in for a model using the materials used in the model

    Args:
        model_mat (dict): dict of the specific model wanted
        materials (dict): dict of  all the materials

    Returns:
        list[str]: list of markers
    """
    markers_list = []
    mmat = json_get(model_mat, "materials")
    if mmat:
        if isinstance(mmat, str):
            markers_list.extend(get_markers(mmat, materials))
        else:
            for mat in mmat:
                markers_list.extend(get_markers(mat, materials))
    else:
        for mat in materials.keys():
            markers_list.extend(get_markers(mat, materials))

    return markers_list


def dict_unknown(data: dict, equations: list[str], dim: int, axis: bool = 0) -> dict:
    """Create dictionnary that translate feelpp symbols into Comsol symbols

    Args:
        data (dict): dict from jsonmodel
        equations (list[str]): list of equations of the model
        dim (int): geometry dimmension
        axis (bool, optional): bool if model is axis. Defaults to 0.

    Returns:
        dict: dict of symbol translator
    """
    eq_expr = {
        "heat": "T",
        "elastic": "u2",
        "elastic1": "u2",
        "elastic2": "u2",
        "electric": "V",
    }
    if axis:
        eq_expr["magnetic"] = "mf.Aphi"
    elif dim == 2:
        eq_expr["magnetic"] = "mf.Az"
    else:
        eq_expr["magnetic"] = "mf.A"

    feel_unknowns = {}
    for equation in equations:
        unknown = json_get(
            data, "Models", equation, "common", "setup", "unknown", "symbol"
        )
        if not unknown:
            unknown = json_get(data, "Models", equation, "setup", "unknown", "symbol")
        feel_unknowns = feel_unknowns | create_dict(
            unknown, equation, eq_expr[equation], dim, axis
        )

    return feel_unknowns


def create_dict(
    unknown: str, equation: str, expr: str, dim: int, axis: bool = 0
) -> dict:
    """Create dictionnary that translate feelpp symbols into Comsol symbols (2nd step: from unknown)

    Args:
        unknown (str): symbol of the unknown of the equation
        equation (str): equation of the unknown
        expr (str): expression of the unknown in Comsol
        dim (int): geometry dimmension
        axis (bool, optional): bool if model is axis. Defaults to 0.

    Returns:
        dict: dict of symbol translator
    """
    dict = {
        f"{equation}_{unknown}": f"{expr}",
        f"{equation}_{unknown}_rt": f"{expr}",
        f"{equation}_d{unknown}_dt": f"d({expr},t)",
        f"{equation}_d{unknown}_rt_dt": f"d({expr},t)",
    }

    if equation == "electric":
        if axis:
            dict[f"{equation}_grad_{unknown}_0"] = f"ec.Er"
            dict[f"{equation}_grad_{unknown}_rt_0"] = f"ec.Er"
            dict[f"{equation}_grad_{unknown}_1"] = f"ec.Ez"
            dict[f"{equation}_grad_{unknown}_rt_1"] = f"ec.Ez"
        elif dim == 2:
            dict[f"{equation}_grad_{unknown}_0"] = f"ec.Ex"
            dict[f"{equation}_grad_{unknown}_rt_0"] = f"ec.Ex"
            dict[f"{equation}_grad_{unknown}_1"] = f"ec.Ey"
            dict[f"{equation}_grad_{unknown}_rt_1"] = f"ec.Ey"
        elif dim == 3:
            dict[f"{equation}_grad_{unknown}_0"] = f"ec.Ex"
            dict[f"{equation}_grad_{unknown}_rt_0"] = f"ec.Ex"
            dict[f"{equation}_grad_{unknown}_1"] = f"ec.Ey"
            dict[f"{equation}_grad_{unknown}_rt_1"] = f"ec.Ey"
            dict[f"{equation}_grad_{unknown}_2"] = f"ec.Ez"
            dict[f"{equation}_grad_{unknown}_rt_2"] = f"ec.Ez"
    else:
        if axis:
            dict[f"{equation}_grad_{unknown}_00"] = f"d({expr}r,r)"
            dict[f"{equation}_grad_{unknown}_rt_00"] = f"d({expr}r,r)"
            dict[f"{equation}_grad_{unknown}_11"] = f"d({expr}z,z)"
            dict[f"{equation}_grad_{unknown}_rt_11"] = f"d({expr}z,z)"
            dict[f"{equation}_grad_{unknown}_01"] = f"d({expr}r,z)"
            dict[f"{equation}_grad_{unknown}_rt_01"] = f"d({expr}r,z)"
            dict[f"{equation}_grad_{unknown}_10"] = f"d({expr}z,r)"
            dict[f"{equation}_grad_{unknown}_rt_10"] = f"d({expr}z,r)"
            dict[f"{equation}_grad_{unknown}_0"] = f"d({expr},r)"
            dict[f"{equation}_grad_{unknown}_rt_0"] = f"d({expr},r)"
            dict[f"{equation}_grad_{unknown}_1"] = f"d({expr},z)"
            dict[f"{equation}_grad_{unknown}_rt_1"] = f"d({expr},z)"
        elif dim == 2:
            dict[f"{equation}_grad_{unknown}_00"] = f"d({expr}x,x)"
            dict[f"{equation}_grad_{unknown}_rt_00"] = f"d({expr}x,x)"
            dict[f"{equation}_grad_{unknown}_11"] = f"d({expr}y,y)"
            dict[f"{equation}_grad_{unknown}_rt_11"] = f"d({expr}y,y)"
            dict[f"{equation}_grad_{unknown}_01"] = f"d({expr}x,y)"
            dict[f"{equation}_grad_{unknown}_rt_01"] = f"d({expr}x,y)"
            dict[f"{equation}_grad_{unknown}_10"] = f"d({expr}y,x)"
            dict[f"{equation}_grad_{unknown}_rt_10"] = f"d({expr}y,x)"
            dict[f"{equation}_grad_{unknown}_0"] = f"d({expr},x)"
            dict[f"{equation}_grad_{unknown}_rt_0"] = f"d({expr},x)"
            dict[f"{equation}_grad_{unknown}_1"] = f"d({expr},y)"
            dict[f"{equation}_grad_{unknown}_rt_1"] = f"d({expr},y)"
        else:
            dict[f"{equation}_grad_{unknown}_00"] = f"d({expr}x,x)"
            dict[f"{equation}_grad_{unknown}_rt_00"] = f"d({expr}x,x)"
            dict[f"{equation}_grad_{unknown}_11"] = f"d({expr}y,y)"
            dict[f"{equation}_grad_{unknown}_rt_11"] = f"d({expr}y,y)"
            dict[f"{equation}_grad_{unknown}_22"] = f"d({expr}z,z)"
            dict[f"{equation}_grad_{unknown}_rt_22"] = f"d({expr}z,z)"
            dict[f"{equation}_grad_{unknown}_01"] = f"d({expr}x,y)"
            dict[f"{equation}_grad_{unknown}_rt_01"] = f"d({expr}x,y)"
            dict[f"{equation}_grad_{unknown}_10"] = f"d({expr}y,x)"
            dict[f"{equation}_grad_{unknown}_rt_10"] = f"d({expr}y,x)"
            dict[f"{equation}_grad_{unknown}_02"] = f"d({expr}x,z)"
            dict[f"{equation}_grad_{unknown}_rt_02"] = f"d({expr}x,z)"
            dict[f"{equation}_grad_{unknown}_20"] = f"d({expr}z,x)"
            dict[f"{equation}_grad_{unknown}_rt_20"] = f"d({expr}z,x)"
            dict[f"{equation}_grad_{unknown}_12"] = f"d({expr}y,z)"
            dict[f"{equation}_grad_{unknown}_rt_12"] = f"d({expr}y,z)"
            dict[f"{equation}_grad_{unknown}_21"] = f"d({expr}z,y)"
            dict[f"{equation}_grad_{unknown}_rt_21"] = f"d({expr}z,y)"
    return dict


def create_group(model, tag: str, label: str, location: str, type: str):
    """Create groups for post-proc exports

    Args:
        model (str): mph file (pyComsol model)
        tag (str): group tag
        label (str): group label
        location (str): group location
        type (str): group type
    """
    model.java.nodeGroup().create(tag, location)
    model.java.nodeGroup(tag).set("type", type)
    model.java.nodeGroup(tag).label(label)


def json_get(data: dict, *keys):
    """find part of dict from keys, return None if it doesn't exist

    Args:
        data (dict): dict to explore
        keys (str): keys that form the path in the dict (data[key1][key2][key3]....)

    Returns:
        data[key1][key2][key3]... or None if doesn't exist
    """
    current_data = data
    for key in keys:
        current_data = current_data.get(key)
        if not current_data:
            break

    return current_data


def feel_to_comsol_symbols(param: str, dict_unknown: dict) -> str:
    """replace the FEEL++ symbols by Comsol symbols

    Args:
        param (str): string to translate
        dict_unknown (dict): dict containing the translation of all symbols

    Returns:
        str: updated params with Comsol symbols
    """
    return re.sub(
        r"\b(" + "|".join(re.escape(key) for key in dict_unknown.keys()) + r")\b",
        lambda match: dict_unknown[match.group(0)],
        param,
    )
