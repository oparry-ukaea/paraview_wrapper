import glob
import os
import sys


def get_desktop_dir():
    loc = ""
    if "HOME" in os.environ:
        loc = os.path.join(os.environ["HOME"], "Desktop")
    if loc and os.path.isdir(loc):
        return loc
    else:
        raise (RuntimeError("get_desktop_dir: Desktop dir not found"))
