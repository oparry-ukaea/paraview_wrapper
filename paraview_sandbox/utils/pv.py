import datetime
import os.path
from paraview.simple import XMLUnstructuredGridReader
import paraview.util
import re


def get_data_dim(vtu_data):
    info = vtu_data.GetDataInformation()
    bounds = info.GetBounds()
    for idim in [3, 2, 1]:
        if bounds[2 * idim - 1] > bounds[2 * idim - 2]:
            return idim


def gen_cbar_props(user_settings, **defaults):
    # Common defaults
    props = dict(
        cbar_label_fontsize=15,
        cbar_len=0.35,
        cbar_loc="Any Location",
        cbar_orient="Horizontal",
        cbar_pos=[0.3, 0.68],
        cbar_title_fontsize=18,
        cbar_title="No title set",
        cbar_use_log=0,
        cbar_vals=[],
    )
    props.update(**defaults)
    props.update(**user_settings)
    return props


def gen_opacity_pts(opacity_vals):
    # Check types
    try:
        tmp_it1 = iter(opacity_vals)
        tmp_it2 = iter(opacity_vals[0])
        if len(opacity_vals[0]) != 2:
            raise TypeError
    except TypeError:
        print("opacity_values must be a list of 2-tuples [(val1,op1),(val2,op2)...]")
        raise

    pts = []
    for val_op in opacity_vals:
        pts.extend(val_op)
        pts.extend((0.5, 0.0))
    return pts


def gen_registration_name(prefix):
    return prefix + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")


def _extract_basename(p, nektar_fname_fmt=False):
    if nektar_fname_fmt:
        return os.path.split(p)[-1].split("_")[0]
    else:
        return os.path.basename(p)


def get_vtu_data(
    data_dir,
    vtu_basename="",
    nektar_fname_fmt=False,
    registration_name=None,
):
    # Default registration name
    if registration_name is None:
        registration_name = gen_registration_name("vtu_data")

    glob_pattern = f"{data_dir}/{vtu_basename}*.vtu"
    vtu_fpaths = paraview.util.Glob(path=glob_pattern)

    # Sort
    pattern = re.compile(r".*_([0-9]*).vtu")
    vtu_fpaths = sorted(vtu_fpaths, key=lambda s: int(pattern.search(s).groups()[0]))

    # Check for multiple basenames if none was specified
    if not vtu_basename:
        unique_basenames = set(
            [
                _extract_basename(p, nektar_fname_fmt=nektar_fname_fmt)
                for p in vtu_fpaths
            ]
        )
        if len(unique_basenames) > 1:
            print(
                f"get_vtu_data: WARNING - Found vtus with multiple basenames in {data_dir}; pass 'vtu_basename' to choose one"
            )

    vtu_data = XMLUnstructuredGridReader(
        registrationName=registration_name, FileName=vtu_fpaths
    )
    return vtu_data
