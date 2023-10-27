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
    XMLUnstructuredGridReader,
)


def gen_img(
    data_dir,
    output_dir=".",
    output_time=36.0,
    fluid_vtu_basename="2DWithParticles_config_",
):
    # Filenames
    part_data_fname = "SimpleSOL_particle_trajectory.h5part"

    # Fluid rho colorbar settings
    fluid_cbar_title = "n / $3*10^{18} m^{-3}$"
    fluid_cbar_range = [0, 5]

    # Particle weight colorbar settings
    part_cbar_title = "Particle weight"
    part_cbar_vals = [v * 1e14 for v in [0.3, 1, 3, 10, 30]]
    part_cbar_use_logscale = 1

    # Camera position
    cam_x = 2.75

    # Ouput path
    output_fpath = os.path.join(
        output_dir, f"t4c2_fluid-particle_img_t{str(output_time)}.png"
    )
    # -------------------------------------------------------------------------

    # Read all Nektar vtus
    fluid_vtu_fpaths = glob(f"{data_dir}/{fluid_vtu_basename}*.vtu")
    pattern = re.compile(r".*_([0-9]*).vtu")
    fluid_vtu_fpaths = sorted(
        fluid_vtu_fpaths, key=lambda s: int(pattern.search(s).groups()[0])
    )
    fluid_data = XMLUnstructuredGridReader(
        registrationName="2DWithParticles_config_*", FileName=fluid_vtu_fpaths
    )

    # Read particle data
    part_data = H5PartReader(
        registrationName=part_data_fname,
        FileName=f"{data_dir}/{part_data_fname}",
    )

    # ------------------------------------------------------------------------------
    # Create a split layout and assign a new view to each half
    layout = CreateLayout()
    layout.SplitVertical(0, 0.5)
    fluid_view = CreateView("RenderView")
    part_view = CreateView("RenderView")
    AssignViewToLayout(view=fluid_view, layout=layout, hint=0)
    AssignViewToLayout(view=part_view, layout=layout, hint=2)

    # Common settings for both views
    for view in [fluid_view, part_view]:
        view.OrientationAxesVisibility = 0
        view.AxesGrid.Visibility = 1

    # Choose animation frame
    animation_scene = GetAnimationScene()
    animation_scene.UpdateAnimationUsingDataTimeSteps()
    animation_scene.AnimationTime = output_time

    # Assign data to views
    fluid_Display = Show(fluid_data, fluid_view, "UnstructuredGridRepresentation")
    part_Display = Show(part_data, part_view, "GeometryRepresentation")

    # Colour fluid by density and set scale
    ColorBy(fluid_Display, ("POINTS", "rho"))
    rhoLUT = GetColorTransferFunction("rho")
    rhoPWF = GetOpacityTransferFunction("rho")
    for trans_func in [rhoLUT, rhoPWF]:
        trans_func.RescaleTransferFunction(*fluid_cbar_range)

    # Colour particle data by weight and set scale
    ColorBy(part_Display, ("POINTS", "COMPUTATIONAL_WEIGHT"))
    part_weights_LUT = GetColorTransferFunction("COMPUTATIONAL_WEIGHT")
    part_opacities_PWF = GetOpacityTransferFunction("COMPUTATIONAL_WEIGHT")
    for trans_func in [part_weights_LUT, part_opacities_PWF]:
        trans_func.UseLogScale = part_cbar_use_logscale
        trans_func.RescaleTransferFunction(part_cbar_vals[0], part_cbar_vals[-1])
    # ------------------------------------------------------------------------------
    # Colour bar properties
    fluid_cbar = GetScalarBar(rhoLUT, fluid_view)
    part_cbar = GetScalarBar(part_weights_LUT, part_view)

    for cbar in [fluid_cbar, part_cbar]:
        cbar.ComponentTitle = ""
        cbar.Orientation = "Horizontal"
        cbar.ScalarBarLength = 0.33
        cbar.WindowLocation = "Any Location"

    fluid_cbar.Title = fluid_cbar_title
    fluid_cbar.Position = [0.3139144736842103, 0.7629896907216499]

    part_cbar.Title = part_cbar_title
    part_cbar.Position = [0.3270723684210524, 0.09033591731266169]
    part_cbar.UseCustomLabels = 1
    part_cbar.CustomLabels = part_cbar_vals
    # ------------------------------------------------------------------------------
    # Generate screenshot
    layout.SetSize(1216, 776)

    # Camera positions
    for view, yp in zip([fluid_view, part_view], [0.73773, 0.20755]):
        view.InteractionMode = "2D"
        view.CameraPosition = [cam_x, yp, 212.5124627460493]
        view.CameraFocalPoint = [cam_x, yp, 0.0]
        view.CameraParallelScale = 1.004356415767127

    SaveScreenshot(output_fpath, layout)
