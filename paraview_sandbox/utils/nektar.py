"""
Stripped-down Nektar utils to avoid having to import (e.g.) NekPlot
"""
import xml.etree.ElementTree as ET
import os.path
from glob import glob


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
    return {t[0].strip(): t[1].strip() for t in [p.text.split("=") for p in params]}
