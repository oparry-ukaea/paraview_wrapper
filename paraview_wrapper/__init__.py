import glob
import os.path
import sys


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


find_paraview()
from paraview.simple import Connect
from .utils import *
from .NESO import gen_img as __gen_img
from .NESO import gen_movie as __gen_movie
from .NESO import fluid_slice as __fluid_slice
from .NESO import line_plot_1d as __line_plot_1d
from .NESO import PyExpr


def make_vis(*args, **kwargs):
    """
    Main wrapper function for creating paraview visualisations. The first argument is a string
    specifying the type of visualisation to create, and the remaining arguments are passed to the
    relevant function for that visualisation type.
    """
    vis_type = args[0]
    allowed_vis_types = [
        "img",
        "line_plot",
        "movie",
        "multi_img",
        "slice",
    ]
    if vis_type not in allowed_vis_types:
        raise ValueError(
            f"paraview_wrapper.make_vis: unrecognized visualisation type '{vis_type}' (allowed types are: {allowed_vis_types})"
        )

    # Connect to paraview server if host specified
    host = kwargs.pop("host", "")
    if host:
        Connect(host)

    if vis_type == "img":
        __gen_img(*args[1:], **kwargs)
    elif vis_type == "line_plot":
        __line_plot_1d(*args[1:], **kwargs)
    elif vis_type == "movie":
        __gen_movie(*args[1:], **kwargs)
    elif vis_type == "slice":
        __fluid_slice(*args[1:], **kwargs)
    elif vis_type == "multi_img":
        outputs = args[1]
        # Check that a valid list of numerical output identifiers has been provided
        output_format_valid = (
            type(outputs) is list
            and len(outputs) > 0
            and all(type(output) in [int, float] for output in outputs)
        )
        if not output_format_valid:
            raise ValueError(
                "paraview_wrapper.make_vis: 'multi_img' visualisation type requires a list of numerical output identifiers as the second argument (times or iteration numbers)"
            )

        # Generate an image for each output
        gen_img_kwargs = kwargs.pop("gen_img_kwargs", {})
        for output in outputs:
            __gen_img(
                *args[2:4],
                output,
                *args[4:],
                **gen_img_kwargs.get(output, {}),
                **kwargs,
            )
