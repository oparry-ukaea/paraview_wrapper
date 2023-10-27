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


def _paraview_importable():
    try:
        import paraview

        return True
    except:
        return False


def find_paraview():
    if _paraview_importable():
        return
    else:
        # Try and find via environment variable
        site_packages_from_envvar = glob.glob(
            os.path.join(os.getenv("PARAVIEW_ROOT"), "lib/python*/site-packages")
        )
        if site_packages_from_envvar:
            sys.path.append(site_packages_from_envvar[0])

        if _paraview_importable():
            return
        else:
            raise ModuleNotFoundError(
                "Unable to find paraview - add <paraview>/lib/python*/site-packages to your PYTHONPATH or define PARAVIEW_ROOT env var."
            )
