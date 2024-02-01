import datetime
import glob
import os
import os.path
from paraview.simple import XMLUnstructuredGridReader
import paraview.util
import re
import sys


def get_desktop_dir():
    loc = ""
    if "HOME" in os.environ:
        loc = os.path.join(os.environ["HOME"], "Desktop")
    if loc and os.path.isdir(loc):
        return loc
    else:
        raise (RuntimeError("get_desktop_dir: Desktop dir not found"))


def get_vtu_data(
    data_dir,
    vtu_basename="",
    registration_name=None,
):
    # Default registration name
    if registration_name is None:
        registration_name = "vtu_data" + datetime.datetime.now().strftime(
            "%Y-%m-%d-%H-%M-%S-%f"
        )

    glob_pattern = f"{data_dir}/{vtu_basename}*.vtu"
    vtu_fpaths = paraview.util.Glob(path=glob_pattern)

    # Sort
    pattern = re.compile(r".*_([0-9]*).vtu")
    vtu_fpaths = sorted(vtu_fpaths, key=lambda s: int(pattern.search(s).groups()[0]))

    # Check for multiple basenames if none was specified
    if not vtu_basename:
        unique_basenames = set([os.path.basename(p) for p in vtu_fpaths])
        if len(unique_basenames) > 1:
            print(
                f"get_vtu_data: WARNING - Found vtus with multiple basenames in {data_dir}; pass 'vtu_basename' to choose one"
            )

    vtu_data = XMLUnstructuredGridReader(
        registrationName=registration_name, FileName=vtu_fpaths
    )
    return vtu_data
