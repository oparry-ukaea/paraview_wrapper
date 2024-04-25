"""
Stripped-down Nektar utils to avoid having to import (e.g.) NekPlot
"""

import xml.etree.ElementTree as ET
import os.path
from glob import glob
import math


def is_nektar_config(path):
    """
    Return True if <path> is a valid xml file with a root/CONDITIONS node, False otherwise.
    """
    is_config = False
    try:
        root = ET.parse(path).getroot()
        conditions_node = root.find("./CONDITIONS")
        is_config = conditions_node is not None
    except:
        pass
    finally:
        return is_config


def find_nektar_config(dir):
    """
    Find nektar config in <dir>.
    If multiple config files are found, print a warning and return the most recently modified
    """
    all_xmls = glob(dir + "/*.xml")
    nektar_configs = [p for p in all_xmls if is_nektar_config(p)]
    if len(nektar_configs) == 0:
        raise RuntimeError(f"No nektar configuration files found in {dir}")
    elif len(nektar_configs) > 1:
        nektar_configs.sort(key=lambda f: os.path.getmtime(f))
        print(
            f"Found multiple nektar configs in {dir}, using most recent ({os.path.basename(nektar_configs[-1])})"
        )
    return nektar_configs[-1]


def convert_str_dict(sd, d={}):
    """
    Convert Nektar params with string values to ints and floats.
    Handle param references by calling recursively.
    """
    nd_in = len(d)
    ops = {"sqrt(": "math.sqrt("}

    # Any purely numeric strings can be converted straight away
    for k in list(sd.keys()):
        for op_k, op_v in ops.items():
            if op_v not in sd[k] and op_k in sd[k]:
                sd[k] = sd[k].replace(op_k, op_v)
        try:
            val = eval(sd[k])
            discard = sd.pop(k)
            d[k] = val
        except:
            pass
    # If entries have been added to d (new numeric values are available)
    # and there are still strings to be processed; try subbing in values, then call convert again
    if sd and len(d) > nd_in:
        for ks, vs in list(sd.items()):
            tmp = vs
            for k, v in d.items():
                if k in tmp:
                    tmp = tmp.replace(k, str(v))
            sd[ks] = tmp
        convert_str_dict(sd, d)
    for ks, vs in list(sd.items()):
        print(
            f"convert_str_dict: Unable to convert {ks} value {vs} to a number; discarding"
        )

    return d


def get_nektar_params(dir, fname=""):
    """
    Read params node from Nektar XML and return in a dict
    """

    if fname:
        path = os.path.join(dir, fname)
    else:
        path = find_nektar_config(dir)

    tree = ET.parse(path)
    root = tree.getroot()
    params = root.find("./CONDITIONS/PARAMETERS")
    str_dict = {t[0].strip(): t[1].strip() for t in [p.text.split("=") for p in params]}
    return convert_str_dict(str_dict)
