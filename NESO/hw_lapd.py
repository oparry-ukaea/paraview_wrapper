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
    particle_fname="",
    particle_props={},
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

    # Fluid vtus
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

    # show vtu data in view
    display = Show(vtu_data, view, "UnstructuredGridRepresentation")

    # Particle data
    if particle_fname:
        int_particle_props = dict(
            colorby="COMPUTATIONAL_WEIGHT",
            cbar_title="Particle Weight",
            cbar_pos=[0.05, 0.9],
            cbar_vals=[1e14 * x for x in [0, 0.5, 1, 1.5, 2, 2.5]],
        )
        int_particle_props.update(particle_props)
        particle_fpath = os.path.join(data_dir, particle_fname)
        part_data = H5PartReader(
            registrationName=particle_fname,
            FileName=particle_fpath,
        )
        part_display = Show(part_data, view, "GeometryRepresentation")
        ColorBy(part_display, ("POINTS", int_particle_props["colorby"]))
        part_color_tf = GetColorTransferFunction(int_particle_props["colorby"])

        part_color_tf.RescaleTransferFunction(
            int_particle_props["cbar_vals"][0], int_particle_props["cbar_vals"][-1]
        )

        part_cbar = GetScalarBar(part_color_tf, view)
        part_cbar.ComponentTitle = ""
        part_cbar.Orientation = "Horizontal"
        part_cbar.ScalarBarLength = 0.25
        part_cbar.WindowLocation = "Any Location"
        part_cbar.Title = int_particle_props["cbar_title"]
        part_cbar.Position = int_particle_props["cbar_pos"]
        part_cbar.UseCustomLabels = 1
        part_cbar.CustomLabels = int_particle_props["cbar_vals"]

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
    int_data_settings = dict(range=[0, 1], render_mode="Resample To Image")
    int_data_settings.update(data_settings)

    # get color transfer function/color map for variable
    color_tf = GetColorTransferFunction(varname)
    # Rescale transfer function
    color_tf.RescaleTransferFunction(*int_data_settings["range"])

    if "opacities" in data_settings:
        opacity_map = GetOpacityTransferFunction(varname)
        opacity_map.Points = gen_opacity_pts(data_settings["opacities"])
        color_tf.EnableOpacityMapping = 1

    # Color bar properties
    cbar = GetScalarBar(color_tf, view)
    cbar.ComponentTitle = ""
    cbar.Orientation = "Vertical"
    cbar.ScalarBarLength = 0.35
    cbar.WindowLocation = "Any Location"
    cbar.Title = "$n_e~/~10^{17} m^{-3}$"
    cbar.Position = [0.92, 0.08]
    # cbar.UseCustomLabels = 1
    # cbar.CustomLabels = int_particle_props["cbar_vals"]

    # change representation type
    display.SetRepresentationType("Volume")

    # Properties modified on lapd_Display
    display.SelectMapper = int_data_settings["render_mode"]

    # Make coordinate axes visible, hide xyz pointer
    if int_data_settings["render_mode"] == "Resample To Image":
        view.AxesGrid.Visibility = 1
    else:
        view.AxesGrid.Visibility = 1
    view.OrientationAxesVisibility = 0

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
