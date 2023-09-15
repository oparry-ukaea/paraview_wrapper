from glob import glob
import os.path
from paraview.simple import *
import re

#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()


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


def gen_movie(
    varname,
    data_dir,
    output_dir,
    vtu_basename="",
    animation_settings={},
    data_settings={},
    display_settings={},
    camera_settings={},
    output_fname="",
):
    if not output_fname:
        output_fname = f"{varname}_movie.avi"

    # Output path
    output_fpath = os.path.join(output_dir, output_fname)
    vtu_fpaths = glob(f"{data_dir}/{vtu_basename}*.vtu")
    pattern = re.compile(r".*_([0-9]*).vtu")
    vtu_fpaths = sorted(vtu_fpaths, key=lambda s: int(pattern.search(s).groups()[0]))
    vtu_data = XMLUnstructuredGridReader(
        registrationName="vtu_data", FileName=vtu_fpaths
    )

    # get animation scene
    anim_scene = GetAnimationScene()

    # update animation scene based on data timesteps
    anim_scene.UpdateAnimationUsingDataTimeSteps()

    # set active source
    SetActiveSource(vtu_data)

    # get active view
    view = FindViewOrCreate(f"gen_{varname}_movie", "RenderView")

    # show data in view
    display = Show(vtu_data, view, "UnstructuredGridRepresentation")

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    display.ScaleTransferFunction.Points = [
        0.0,
        0.0,
        0.5,
        0.0,
        0.0,
        1.0,
        0.5,
        0.0,
    ]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    display.OpacityTransferFunction.Points = [
        0.0,
        0.0,
        0.5,
        0.0,
        0.0,
        1.0,
        0.5,
        0.0,
    ]

    # reset view to fit data
    view.ResetCamera(False)

    # set scalar coloring
    ColorBy(display, ("POINTS", varname))

    # rescale color and/or opacity maps used to include current data range
    display.RescaleTransferFunctionToDataRange(True, False)

    # show color bar/color legend
    display.SetScalarBarVisibility(view, True)

    # Data settings
    int_data_settings = dict(range=[0, 1])
    int_data_settings.update(data_settings)

    # get color transfer function/color map for variable
    color_map = GetColorTransferFunction(varname)
    # Rescale transfer function
    color_map.RescaleTransferFunction(*int_data_settings["range"])

    if "opacities" in data_settings:
        opacity_map = GetOpacityTransferFunction(varname)
        opacity_map.Points = gen_opacity_pts(data_settings["opacities"])
        color_map.EnableOpacityMapping = 1

    # change representation type
    display.SetRepresentationType("Volume")

    # Properties modified on lapd_Display
    display.SelectMapper = "Resample To Image"

    # Properties modified on view.AxesGrid
    view.AxesGrid.Visibility = 1

    # Default camera settings
    int_camera_settings = dict(
        pos=[16.3, 3.1, 21.9], fpt=[0.0, 0.0, 5.0], up=[0.0, 1.0, -0.30], pscale=6.1
    )
    # Apply any camera settings passed by the user
    int_camera_settings.update(camera_settings)
    view.CameraPosition = int_camera_settings["pos"]
    view.CameraFocalPoint = int_camera_settings["fpt"]
    view.CameraViewUp = int_camera_settings["up"]
    view.CameraParallelScale = int_camera_settings["pscale"]

    # Default animation settings
    int_animation_settings = dict(ImageResolution=[1920, 1080], FrameRate=5)
    # Apply any animation settings passed by the user
    int_animation_settings.update(animation_settings)

    if "FrameWindow" in int_animation_settings:
        nframes_max = len(vtu_fpaths)
        fw = int_animation_settings["FrameWindow"]
        fw = [max(fw[0], 0), min(fw[1], nframes_max - 1)]

    # Set layout/tab size in pixels
    layout = GetLayout()
    layout.SetSize(*int_animation_settings["ImageResolution"])

    print("Saving animation...")

    # save animation
    SaveAnimation(
        output_fpath,
        view,
        **int_animation_settings,
    )

    print(f"Saved animation to {output_fpath}")
