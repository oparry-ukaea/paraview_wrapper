from glob import glob
import os.path
import re

from paraview.simple import (
    AssignViewToLayout,
    ColorBy,
    CreateLayout,
    CreateView,
    GetAnimationScene,
    GetColorTransferFunction,
    GetOpacityTransferFunction,
    GetScalarBar,
    H5PartReader,
    SaveScreenshot,
    Show,
)

from ..utils import gen_opacity_pts


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


def gen_img(
    data_dir,
    fluid_var,
    output_time,
    fluid_vtu_basename="2DWithParticles_config_",
    fluid_props={},
    fluid_view_settings={},
    output_basename=None,
    output_dir=".",
    part_data_fname=None,
    part_props={},
    part_view_settings={},
):
    if output_basename is None:
        output_basename = fluid_vtu_basename
    plotting_particles = part_data_fname is not None

    # Camera position(s), focal point(s)
    int_fluid_view_settings = dict(
        fpt=[2.75, 0.74, 0.0],
        pos=[2.75, 0.74, 212.5],
        pscale=1.0,
        up=[0.0, 1.0, 0.0],
    )
    int_fluid_view_settings.update(fluid_view_settings)
    int_view_settings = [int_fluid_view_settings]
    if plotting_particles:
        int_part_view_settings = dict(
            fpt=[2.75, 0.20755, 0.0],
            pos=[2.75, 0.20755, 212.5],
            pscale=1.0,
            up=[0.0, 1.0, 0.0],
        )
        int_part_view_settings.update(part_view_settings)
        int_view_settings.append(int_part_view_settings)

    # Ouput path
    output_fpath = os.path.join(
        output_dir, f"{output_basename}_t{str(output_time)}.png"
    )
    # -------------------------------------------------------------------------

    # Read all Nektar vtus
    fluid_data = get_vtu_data(data_dir, vtu_basename=fluid_vtu_basename)

    # Read particle data
    if plotting_particles:
        part_data = H5PartReader(
            registrationName=part_data_fname,
            FileName=f"{data_dir}/{part_data_fname}",
        )

    # ------------------------------------------------------------------------------
    # Create view(s), layout(s), assign data to views
    layout = CreateLayout()
    fluid_view = CreateView("RenderView")
    fluid_Display = Show(fluid_data, fluid_view, "UnstructuredGridRepresentation")
    views = [fluid_view]
    if plotting_particles:
        layout.SplitVertical(0, 0.5)
        part_view = CreateView("RenderView")
        part_Display = Show(part_data, part_view, "GeometryRepresentation")
        views.append(part_view)
        AssignViewToLayout(view=fluid_view, layout=layout, hint=0)
        AssignViewToLayout(view=part_view, layout=layout, hint=2)
    else:
        AssignViewToLayout(view=fluid_view, layout=layout)

    # Get data dimension, this only works after calling Show()!
    data_ndims = get_data_dim(fluid_data)

    # Common settings for both views
    for view in views:
        view.OrientationAxesVisibility = 0
        view.AxesGrid.Visibility = 1

    # Choose animation frame
    animation_scene = GetAnimationScene()
    animation_scene.UpdateAnimationUsingDataTimeSteps()
    animation_scene.AnimationTime = output_time

    # Colour fluid by density, set scale, setup colorbar
    int_fluid_props = gen_cbar_props(
        fluid_props,
        colorby=fluid_var,
        cbar_pos=[0.3, 0.75],
        cbar_range=[0, 5],
        cbar_title="n / $3*10^{18} m^{-3}$",
    )
    int_fluid_props["render_type"] = "Volume" if data_ndims == 3 else "Surface"

    # Create fluid color bar
    ColorBy(fluid_Display, ("POINTS", int_fluid_props["colorby"]))
    fluid_cbar = GetScalarBar(
        GetColorTransferFunction(int_fluid_props["colorby"]), fluid_view
    )
    cbars = [(fluid_cbar, int_fluid_props)]

    if plotting_particles:
        int_part_props = gen_cbar_props(
            part_props,
            colorby="COMPUTATIONAL_WEIGHT",
            cbar_label_fontsize=15,
            cbar_pos=[0.3, 0.1],
            cbar_title="Particle Weight",
            cbar_use_log=1,
            cbar_vals=[v * 1e14 for v in [0.3, 1, 3, 10, 30]],
            psize=2,
        )

        # Colour particle data by weight, set scale, setup colorbar
        ColorBy(part_Display, ("POINTS", int_part_props["colorby"]))
        part_cbar = GetScalarBar(
            GetColorTransferFunction(int_part_props["colorby"]), part_view
        )
        cbars.append((part_cbar, int_part_props))

    # Set colorbar properties
    for cbar, props in cbars:
        cbar.ComponentTitle = ""
        cbar.LabelFontSize = props["cbar_label_fontsize"]
        cbar.Orientation = props["cbar_orient"]
        cbar.Position = props["cbar_pos"]
        cbar.ScalarBarLength = props["cbar_len"]
        cbar.Title = props["cbar_title"]
        cbar.TitleFontSize = props["cbar_title_fontsize"]
        cbar.WindowLocation = props["cbar_loc"]
        if props["cbar_vals"]:
            cbar.UseCustomLabels = 1
            cbar.CustomLabels = props["cbar_vals"]

        if "cbar_range" in props:
            cbar_range = props["cbar_range"]
        elif props["cbar_vals"]:
            cbar_range = [props["cbar_vals"][0], props["cbar_vals"][-1]]
        else:
            cbar_range = [0, 1]

        color_trans_func = GetColorTransferFunction(props["colorby"])
        opac_trans_func = GetOpacityTransferFunction(props["colorby"])
        for trans_func in [color_trans_func, opac_trans_func]:
            trans_func.RescaleTransferFunction(*cbar_range)
            trans_func.UseLogScale = props["cbar_use_log"]

        if "opacities" in props:
            opac_trans_func.Points = gen_opacity_pts(props["opacities"])
            color_trans_func.EnableOpacityMapping = 1

    # Rendering type
    fluid_Display.SetRepresentationType(int_fluid_props["render_type"])
    if int_fluid_props["render_type"] == "Volume":
        fluid_Display.SelectMapper = int_fluid_props["render_mode"]

    # ------------------------------------------------------------------------------
    # Generate screenshot
    layout.SetSize(1216, 776)

    # Set camera positions, focal points
    for view, settings in zip(views, int_view_settings):
        view.InteractionMode = f"{data_ndims}D"
        view.CameraPosition = settings["pos"]
        view.CameraFocalPoint = settings["fpt"]
        view.CameraParallelScale = settings["pscale"]
        view.CameraViewUp = settings["up"]

    SaveScreenshot(output_fpath, layout)
