from glob import glob
import os.path
from paraview.simple import *
import re

### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()


class PyExpr:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr


def line_plot_1d(
    varnames,
    data_dir,
    output_dir,
    dt=None,
    vtu_basename="",
    animation_settings={},
    exprs_to_plot=[],
    output_fname="",
    plot_settings={},
    tlbl_settings={},
    host="",
):
    var_str = "-".join(varnames)
    default_lbl = f"{var_str}_line_plot"
    if not output_fname:
        output_fname = f"{default_lbl}.avi"

    # Ensure expressions are all instances instances of PyExpr
    for expr in exprs_to_plot:
        assert isinstance(expr, PyExpr)

    # Output path
    output_fpath = os.path.join(output_dir, output_fname)

    # Fluid vtus
    if host:
        Connect(host)
        if vtu_basename and "FrameWindow" in animation_settings:
            fw = animation_settings["FrameWindow"]
            vtu_fpaths = [f"{data_dir}/{vtu_basename}{n}.vtu" for n in range(*fw)]
        else:
            raise RuntimeError(
                "Must specify vtu_basename and animation_settings['FrameWindow'] when using remote host"
            )
    else:
        vtu_fpaths = glob(f"{data_dir}/{vtu_basename}*.vtu")
        pattern = re.compile(r".*_([0-9]*).vtu")
        vtu_fpaths = sorted(
            vtu_fpaths, key=lambda s: int(pattern.search(s).groups()[0])
        )

    vtu_data = XMLUnstructuredGridReader(
        registrationName="vtu_data", FileName=vtu_fpaths
    )

    # get animation scene
    anim_scene = GetAnimationScene()

    # update animation scene based on data timesteps
    anim_scene.UpdateAnimationUsingDataTimeSteps()

    # get active view
    data_view = GetActiveViewOrCreate("RenderView")

    # Show data in view
    data_display = Show(vtu_data, data_view, "UnstructuredGridRepresentation")

    # Plot python expressions, daisy-chaining inputs so that paraview plots the correct sources.
    line_plot_inputs = [vtu_data]
    for expr_props in exprs_to_plot:
        expr = PythonCalculator(
            registrationName=expr_props.name, Input=line_plot_inputs[-1]
        )
        expr.Expression = expr_props.expr
        expr.ArrayName = expr_props.name
        tmp_display = Show(expr, data_view, "UnstructuredGridRepresentation")
        line_plot_inputs.append(expr)

    # Create line plot
    line_plot = PlotOverLine(registrationName="line_plot", Input=line_plot_inputs[-1])

    # set active source
    SetActiveSource(line_plot)

    # hide data in view
    Hide(vtu_data, data_view)

    view = CreateView("XYChartView")

    # ylabel=" or ".join(varnames)
    # Apply settings
    int_plot_settings = dict(
        xlabel="x",
        ylabel="",
        xrange=[0.0, 2.0],
        yrange=[-1.1, 2.2],
        font_size=16,
    )
    int_plot_settings.update(plot_settings)

    # show line plot in view
    display = Show(line_plot, view, "XYChartRepresentation")

    lstys = display.SeriesLineStyle.GetData()
    for expr in exprs_to_plot:
        idx = lstys.index(expr.name)
        lstys[idx + 1] = "2"
    display.SeriesLineStyle.SetData(lstys)

    view.BottomAxisRangeMinimum = int_plot_settings["xrange"][0]
    view.BottomAxisRangeMaximum = int_plot_settings["xrange"][1]
    view.BottomAxisTitle = int_plot_settings["xlabel"]
    view.BottomAxisTitleBold = 0
    view.BottomAxisTitleFontSize = int_plot_settings["font_size"]
    view.BottomAxisUseCustomRange = 1
    view.LeftAxisRangeMinimum = int_plot_settings["yrange"][0]
    view.LeftAxisRangeMaximum = int_plot_settings["yrange"][1]
    view.LeftAxisTitle = int_plot_settings["ylabel"]
    view.LeftAxisTitleBold = 0
    view.LeftAxisTitleFontSize = int_plot_settings["font_size"]
    view.LeftAxisUseCustomRange = 1

    if dt is not None:
        tlbl_settings_int = dict(pos=[0.65, 0.1], fmt=".1E")
        tlbl_settings_int.update(tlbl_settings)
        # Create'Annotate Time Filter'
        annotate_time_filter = AnnotateTimeFilter(
            registrationName="annotate_time_filter", Input=vtu_data
        )

        annotate_time_filter.Format = "Time: {time:" + tlbl_settings_int["fmt"] + "}"
        annotate_time_filter.Scale = dt

        # show data in view
        display_annotate_time_filter = Show(
            annotate_time_filter, view, "ChartTextRepresentation"
        )

        # Properties modified on display_annotate_time_filter
        display_annotate_time_filter.LabelLocation = "Any Location"

        # Properties modified on display_annotate_time_filter
        display_annotate_time_filter.Position = tlbl_settings_int["pos"]

    # Default animation settings
    int_animation_settings = dict(FrameRate=5)
    # Apply any animation settings passed by the user
    int_animation_settings.update(animation_settings)

    if "FrameWindow" in int_animation_settings:
        nframes_max = len(vtu_fpaths)
        fw = int_animation_settings["FrameWindow"]
        fw = [max(fw[0], 0), min(fw[1], nframes_max - 1)]

    layout = GetLayout()
    if "ImageResolution" in int_animation_settings:
        layout.SetSize(*int_animation_settings["ImageResolution"])

    # add view to a layout so it's visible in UI
    AssignViewToLayout(view=view, layout=layout, hint=0)

    # save animation
    SaveAnimation(
        output_fpath,
        view,
        **int_animation_settings,
    )

    print(f"Saved animation to {output_fpath}")
