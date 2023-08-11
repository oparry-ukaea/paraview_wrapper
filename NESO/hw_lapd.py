from glob import glob
import os.path
from paraview.simple import *
import re

#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()


def gen_phi_movie(
    data_dir, output_dir, animation_settings={}, output_fname="phi_movie.avi"
):

    # Output path
    output_fpath = os.path.join(output_dir, output_fname)
    vtu_fpaths = glob(f"{data_dir}/*.vtu")
    pattern = re.compile(r".*_([0-9]*).vtu")
    vtu_fpaths = sorted(vtu_fpaths, key=lambda s: int(pattern.search(s).groups()[0]))
    vtu_data = XMLUnstructuredGridReader(
        registrationName="vtu_data", FileName=vtu_fpaths
    )

    vtu_data.PointArrayStatus = ["ne", "Ge", "Gd", "w", "phi"]

    # get animation scene
    animationScene1 = GetAnimationScene()

    # update animation scene based on data timesteps
    animationScene1.UpdateAnimationUsingDataTimeSteps()

    # set active source
    SetActiveSource(vtu_data)

    # get active view
    renderView1 = FindViewOrCreate("genPhiMovie", "RenderView")

    # show data in view
    lapd_Display = Show(vtu_data, renderView1, "UnstructuredGridRepresentation")

    # trace defaults for the display properties.
    lapd_Display.Representation = "Surface"
    lapd_Display.ColorArrayName = [None, ""]
    lapd_Display.SelectTCoordArray = "None"
    lapd_Display.SelectNormalArray = "None"
    lapd_Display.SelectTangentArray = "None"
    lapd_Display.OSPRayScaleArray = "Gd"
    lapd_Display.OSPRayScaleFunction = "PiecewiseFunction"
    lapd_Display.SelectOrientationVectors = "None"
    lapd_Display.SelectScaleArray = "Gd"
    lapd_Display.GlyphType = "Arrow"
    lapd_Display.GlyphTableIndexArray = "Gd"
    lapd_Display.GaussianRadius = 0.05
    lapd_Display.SetScaleArray = ["POINTS", "Gd"]
    lapd_Display.ScaleTransferFunction = "PiecewiseFunction"
    lapd_Display.OpacityArray = ["POINTS", "Gd"]
    lapd_Display.OpacityTransferFunction = "PiecewiseFunction"
    lapd_Display.DataAxesGrid = "GridAxesRepresentation"
    lapd_Display.PolarAxes = "PolarAxesRepresentation"
    lapd_Display.ScalarOpacityUnitDistance = 0.32402688287327763
    lapd_Display.OpacityArrayName = ["POINTS", "Gd"]

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    lapd_Display.ScaleTransferFunction.Points = [
        0.0,
        0.0,
        0.5,
        0.0,
        1.1757813367477812e-38,
        1.0,
        0.5,
        0.0,
    ]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    lapd_Display.OpacityTransferFunction.Points = [
        0.0,
        0.0,
        0.5,
        0.0,
        1.1757813367477812e-38,
        1.0,
        0.5,
        0.0,
    ]

    # reset view to fit data
    renderView1.ResetCamera(False)

    # set scalar coloring
    ColorBy(lapd_Display, ("POINTS", "phi"))

    # rescale color and/or opacity maps used to include current data range
    lapd_Display.RescaleTransferFunctionToDataRange(True, False)

    # show color bar/color legend
    lapd_Display.SetScalarBarVisibility(renderView1, True)

    # get color transfer function/color map for 'phi'
    phiLUT = GetColorTransferFunction("phi")

    # get opacity transfer function/opacity map for 'phi'
    phiPWF = GetOpacityTransferFunction("phi")

    # change representation type
    lapd_Display.SetRepresentationType("Volume")

    # Rescale transfer function
    phiLUT.RescaleTransferFunction(-0.5, 0.5)

    # Properties modified on phiPWF
    phiPWF.Points = [-0.5, 1.0, 0.5, 0.0, 0.0, 0.0, 0.5, 0.0, 0.5, 1.0, 0.5, 0.0]

    # Properties modified on phiLUT
    phiLUT.EnableOpacityMapping = 1

    # Properties modified on lapd_Display
    lapd_Display.SelectMapper = "Resample To Image"

    # Properties modified on renderView1.AxesGrid
    renderView1.AxesGrid.Visibility = 1

    # get layout
    layout1 = GetLayout()

    # layout/tab size in pixels
    layout1.SetSize(1122, 784)

    # current camera placement for renderView1
    renderView1.CameraPosition = [
        16.316036635926093,
        3.0728705414900985,
        21.856809789093937,
    ]
    renderView1.CameraFocalPoint = [0.0, 0.0, 5.0]
    renderView1.CameraViewUp = [
        0.021026296521089036,
        0.9797822758171143,
        -0.1989587566538437,
    ]
    renderView1.CameraParallelScale = 6.123724356957945

    # Default animation
    SaveAnimation_settings = dict(ImageResolution=[1120, 784], FrameRate=5)
    # Apply any settings passed by user
    SaveAnimation_settings.update(animation_settings)

    print("Saving animation...")

    # save animation
    SaveAnimation(
        output_fpath,
        renderView1,
        **SaveAnimation_settings,
    )

    print(f"Saved animation to {output_fpath}")
