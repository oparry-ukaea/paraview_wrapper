from glob import glob
import os.path
from paraview.simple import (
    _DisableFirstRenderCameraReset,
    ColorBy,
    Connect,
    FindViewOrCreate,
    GetAnimationScene,
    GetColorTransferFunction,
    GetLayout,
    GetOpacityTransferFunction,
    GetScalarBar,
    H5PartReader,
    SaveAnimation,
    SetActiveSource,
    Show,
)
import re

from .time_filter import add_time_filter
from ..utils import (
    data_file_exists,
    gen_opacity_pts,
    get_ugrid_props,
    get_vtu_data,
)

#### disable automatic camera reset on 'Show'
_DisableFirstRenderCameraReset()


def gen_movie(
    varname,
    data_dir,
    output_dir,
    particle_fname="",
    particle_props={},
    dt=None,
    vtu_basename="",
    animation_settings={},
    cbar_settings={},
    data_settings={},
    tlbl_settings={},
    view_settings={},
    output_fname="",
    host="",
):
    if not output_fname:
        output_fname = f"{varname}_movie.avi"

    # Output path
    output_fpath = os.path.join(output_dir, output_fname)

    if host:
        Connect(host)

    vtu_data = get_vtu_data(data_dir, basename=vtu_basename)

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
        if data_file_exists(data_dir, particle_fname):
            int_particle_props = dict(
                colorby="COMPUTATIONAL_WEIGHT",
                cbar_len=0.25,
                cbar_title="Particle Weight",
                cbar_pos=[0.05, 0.9],
                cbar_vals=[1e14 * x for x in [0, 0.5, 1, 1.5, 2, 2.5]],
                orient="Horizontal",
                psize=2,
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

            part_display.PointSize = int_particle_props["psize"]
            if int_particle_props["plot_spheres"]:
                part_display.RenderPointsAsSpheres = 1

            part_cbar = GetScalarBar(part_color_tf, view)
            part_cbar.ComponentTitle = ""
            part_cbar.Orientation = int_particle_props["orient"]
            part_cbar.ScalarBarLength = int_particle_props["cbar_len"]
            part_cbar.WindowLocation = "Any Location"
            part_cbar.Title = int_particle_props["cbar_title"]
            part_cbar.Position = int_particle_props["cbar_pos"]
            part_cbar.UseCustomLabels = 1
            part_cbar.CustomLabels = int_particle_props["cbar_vals"]
        else:
            print(f"No particle data at {data_dir}/{particle_fname}, skipping")

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
    int_data_settings = dict(
        range=[0, 1], render_mode="Resample To Image", render_type="Volume"
    )
    int_data_settings.update(data_settings)

    # get color transfer function/color map for variable
    color_tf = GetColorTransferFunction(varname)
    # Rescale transfer function
    color_tf.RescaleTransferFunction(*int_data_settings["range"])

    if "opacities" in data_settings:
        opacity_map = GetOpacityTransferFunction(varname)
        opacity_map.Points = gen_opacity_pts(data_settings["opacities"])
        color_tf.EnableOpacityMapping = 1
    else:
        color_tf.EnableOpacityMapping = 0

    # Color bar properties
    int_cbar_settings = dict(
        label_fontsize=15,
        len=0.35,
        loc="Any Location",
        orient="Vertical",
        pos=[0.93, 0.09],
        title_fontsize=15,
        title=varname,
        vals=[],
    )
    int_cbar_settings.update(cbar_settings)
    cbar = GetScalarBar(color_tf, view)
    cbar.ComponentTitle = ""
    cbar.LabelFontSize = int_cbar_settings["label_fontsize"]
    cbar.Orientation = int_cbar_settings["orient"]
    cbar.ScalarBarLength = int_cbar_settings["len"]
    cbar.WindowLocation = int_cbar_settings["loc"]
    cbar.Title = int_cbar_settings["title"]
    cbar.TitleFontSize = int_cbar_settings["title_fontsize"]
    cbar.Position = int_cbar_settings["pos"]
    if int_cbar_settings["vals"]:
        cbar.UseCustomLabels = 1
        cbar.CustomLabels = int_cbar_settings["vals"]

    # Add a time label
    if dt is not None:
        add_time_filter(dt, vtu_data, view, tlbl_settings)

    # Display properties
    display.SetRepresentationType(int_data_settings["render_type"])
    if int_data_settings["render_type"] == "Volume":
        display.SelectMapper = int_data_settings["render_mode"]

    # Default camera settings
    int_view_settings = dict(
        pos=[16.3, 3.1, 21.9],
        fpt=[0.0, 0.0, 5.0],
        up=[0.0, 1.0, -0.30],
        pscale=6.1,
        show_axes_grid=1,
        show_orient_axes=0,
    )
    # Apply any camera settings passed by the user
    int_view_settings.update(view_settings)

    # Set coordinate axes visibility. Always hide if doing projected tetra rendering
    view.AxesGrid.Visibility = int_view_settings["show_axes_grid"]
    if int_data_settings["render_mode"] == "Projected tetra":
        if int_view_settings["show_axes_grid"]:
            print("Rendering in 'Projected tetra' mode; hiding coord axes")
        view.AxesGrid.Visibility = 0

    data_ndims = get_ugrid_props(vtu_data)["ndims"]
    view.InteractionMode = f"{data_ndims}D"
    view.CameraPosition = int_view_settings["pos"]
    view.CameraFocalPoint = int_view_settings["fpt"]
    view.CameraViewUp = int_view_settings["up"]
    view.CameraParallelScale = int_view_settings["pscale"]

    # Show / hide xyz pointer
    view.OrientationAxesVisibility = int_view_settings["show_orient_axes"]

    # Default animation settings
    int_animation_settings = dict(ImageResolution=[1920, 1080], FrameRate=5)
    # Apply any animation settings passed by the user
    int_animation_settings.update(animation_settings)

    if "FrameWindow" in int_animation_settings:
        nframes_max = len(vtu_data.FileName)
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
