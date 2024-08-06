from glob import glob
import os.path
import re

from paraview.simple import (
    AssignViewToLayout,
    ColorBy,
    Connect,
    CreateLayout,
    CreateView,
    GetAnimationScene,
    GetColorTransferFunction,
    GetOpacityTransferFunction,
    GetScalarBar,
    H5PartReader,
    Hide,
    SaveScreenshot,
    Show,
    Slice,
)

from ..utils import (
    gen_cbar_props,
    gen_opacity_pts,
    gen_registration_name,
    get_data_dim,
    get_vtu_data,
)


def fluid_slice(
    data_dir,
    fluid_var,
    output_time=None,
    fluid_vtu_basename="",
    fluid_props={},
    host="",
    fluid_view_settings={},
    output_basename=None,
    output_dir=".",
    # part_data_fname=None,
    #     part_props={},
    #     part_view_settings={},
    slice_settings={},
):
    if output_basename is None:
        output_basename = fluid_vtu_basename
    # plotting_particles = part_data_fname is not None

    # Camera position(s), focal point(s)
    int_fluid_view_settings = dict(
        fpt=[2.75, 0.74, 0.0],
        pos=[2.75, 0.74, 212.5],
        pscale=1.0,
        up=[0.0, 0.0, 1.0],
    )
    int_fluid_view_settings.update(fluid_view_settings)
    int_view_settings = [int_fluid_view_settings]
    # if plotting_particles:
    #     int_part_view_settings = dict(
    #         fpt=[2.75, 0.20755, 0.0],
    #         pos=[2.75, 0.20755, 212.5],
    #         pscale=1.0,
    #         up=[0.0, 1.0, 0.0],
    #     )
    #     int_part_view_settings.update(part_view_settings)
    #     int_view_settings.append(int_part_view_settings)

    # Output path
    if output_time is None:
        t_string = ""
    else:
        t_string = f"_t{str(output_time)}"
    output_fpath = os.path.join(
        output_dir, f"{output_basename}_{fluid_var}{t_string}.png"
    )

    if host:
        Connect(host)

    # Read all Nektar vtus
    fluid_data = get_vtu_data(data_dir, vtu_basename=fluid_vtu_basename)

    # # Read particle data
    # if plotting_particles:
    #     part_data = H5PartReader(
    #         registrationName=part_data_fname,
    #         FileName=f"{data_dir}/{part_data_fname}",
    #     )

    # ------------------------------------------------------------------------------
    # Create view(s), layout(s), assign data to views
    layout = CreateLayout()
    fluid_view = CreateView("RenderView")

    views = [fluid_view]

    # Get data dimension, this only works after calling Show()!
    _dummy = Show(fluid_data, fluid_view, "UnstructuredGridRepresentation")
    data_ndims = get_data_dim(fluid_data)
    Hide(fluid_data, fluid_view)
    # if plotting_particles:
    #     layout.SplitVertical(0, 0.5)
    #     part_view = CreateView("RenderView")
    #     part_Display = Show(part_data, part_view, "GeometryRepresentation")
    #     views.append(part_view)
    #     AssignViewToLayout(view=fluid_view, layout=layout, hint=0)
    #     AssignViewToLayout(view=part_view, layout=layout, hint=2)
    # else:
    #     AssignViewToLayout(view=fluid_view, layout=layout)
    AssignViewToLayout(view=fluid_view, layout=layout)
    slice = Slice(registrationName=gen_registration_name("Slice"), Input=fluid_data)

    # Default origin is domain midpoint
    def_origin = [0.00815, 0.00815, 5.0]
    int_slice_settings = dict(
        type="Plane",
        HTGslicer="Plane",
        normal=[0.0, 0.0, 1.0],
        offset_vals=[0.0],
        origin=def_origin,
        HTG_origin=def_origin,
    )
    int_slice_settings.update(slice_settings)
    slice.SliceType = int_slice_settings["type"]
    slice.HyperTreeGridSlicer = int_slice_settings["HTGslicer"]
    slice.SliceOffsetValues = int_slice_settings["offset_vals"]
    slice.SliceType.Origin = int_slice_settings["origin"]
    slice.HyperTreeGridSlicer.Origin = int_slice_settings["HTG_origin"]
    slice.SliceType.Normal = int_slice_settings["normal"]

    sliceDisplay = Show(slice, fluid_view, "GeometryRepresentation")

    sliceDisplay.Representation = "Surface"
    sliceDisplay.ColorArrayName = [None, ""]
    sliceDisplay.SelectTCoordArray = "None"
    sliceDisplay.SelectNormalArray = "None"
    sliceDisplay.SelectTangentArray = "None"
    sliceDisplay.OSPRayScaleArray = fluid_var
    sliceDisplay.OSPRayScaleFunction = "PiecewiseFunction"
    sliceDisplay.SelectOrientationVectors = "None"
    sliceDisplay.ScaleFactor = 0.00163000003
    sliceDisplay.SelectScaleArray = "None"
    sliceDisplay.GlyphType = "Arrow"
    sliceDisplay.GlyphTableIndexArray = "None"
    sliceDisplay.GaussianRadius = 8.15000015e-05
    sliceDisplay.SetScaleArray = ["POINTS", fluid_var]
    sliceDisplay.ScaleTransferFunction = "PiecewiseFunction"
    sliceDisplay.OpacityArray = ["POINTS", fluid_var]
    sliceDisplay.OpacityTransferFunction = "PiecewiseFunction"
    sliceDisplay.DataAxesGrid = "GridAxesRepresentation"
    sliceDisplay.PolarAxes = "PolarAxesRepresentation"
    sliceDisplay.SelectInputVectors = [None, ""]
    sliceDisplay.WriteLog = ""

    # Common settings for all views
    for view in views:
        view.OrientationAxesVisibility = 0
        view.AxesGrid.Visibility = 1

    # Choose animation frame
    animation_scene = GetAnimationScene()
    animation_scene.UpdateAnimationUsingDataTimeSteps()
    if output_time is not None:
        animation_scene.AnimationTime = output_time

    # Colour fluid by density, set scale, setup colorbar
    int_fluid_props = gen_cbar_props(
        fluid_props,
        colorby=fluid_var,
        cbar_pos=[0.3, 0.75],
        cbar_range=[0, 5],
        cbar_title=fluid_var,
        render_type="Surface",
    )

    # Create fluid color bar
    ColorBy(sliceDisplay, ("POINTS", int_fluid_props["colorby"]))
    fluid_cbar = GetScalarBar(
        GetColorTransferFunction(int_fluid_props["colorby"]), fluid_view
    )
    cbars = [(fluid_cbar, int_fluid_props)]

    #     if plotting_particles:
    #         int_part_props = gen_cbar_props(
    #             part_props,
    #             colorby="COMPUTATIONAL_WEIGHT",
    #             cbar_label_fontsize=15,
    #             cbar_pos=[0.3, 0.1],
    #             cbar_title="Particle Weight",
    #             cbar_use_log=1,
    #             cbar_vals=[v * 1e14 for v in [0.3, 1, 3, 10, 30]],
    #             psize=2,
    #         )

    #         # Colour particle data by weight, set scale, setup colorbar
    #         ColorBy(part_Display, ("POINTS", int_part_props["colorby"]))
    #         part_cbar = GetScalarBar(
    #             GetColorTransferFunction(int_part_props["colorby"]), part_view
    #         )
    #         cbars.append((part_cbar, int_part_props))

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

    #     # Rendering type
    #     fluid_Display.SetRepresentationType(int_fluid_props["render_type"])
    #     if int_fluid_props["render_type"] == "Volume":
    #         fluid_Display.SelectMapper = int_fluid_props["render_mode"]

    # ------------------------------------------------------------------------------
    # Generate screenshot
    layout.SetSize(1132, 816)

    # Set camera positions, focal points
    for view, settings in zip(views, int_view_settings):
        # view.InteractionMode = f"{data_ndims}D"
        view.CameraPosition = settings["pos"]
        view.CameraFocalPoint = settings["fpt"]
        view.CameraParallelScale = settings["pscale"]
        view.CameraViewUp = settings["up"]

    SaveScreenshot(output_fpath, layout)
