import os.path
from paraview.simple import *
import re

from .time_filter import add_time_filter
from ..utils import get_color_array, get_vtu_data

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
    pt1=[],
    pt2=[],
    dt=None,
    vtu_basename="",
    animation_settings={},
    exprs_to_plot=[],
    output_basename="",
    plot_settings={},
    tlbl_settings={},
    host="",
    line_dim=0,
):
    var_str = "-".join(varnames)
    default_lbl = f"{var_str}_line_plot"
    if not output_basename:
        output_basename = default_lbl

    # Ensure expressions are all instances instances of PyExpr
    for expr in exprs_to_plot:
        assert isinstance(expr, PyExpr)

    # Output path
    output_fpath = os.path.join(output_dir, output_basename + ".avi")

    vtu_data = get_vtu_data(data_dir, vtu_basename=vtu_basename)

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

    # Defaults for line start,end
    if not pt1:
        pt1 = [0.0] * 3
    if not pt2:
        pt2 = [0.0] * 3
        pt2[line_dim] = 2.0

    # Create line plot
    line_plot = PlotOverLine(registrationName="line_plot", Input=line_plot_inputs[-1])
    line_plot.Point1 = pt1
    line_plot.Point2 = pt2

    # set active source
    SetActiveSource(line_plot)

    # hide data in view
    Hide(vtu_data, data_view)

    view = CreateView("XYChartView")

    # ylabel=" or ".join(varnames)
    # Apply settings
    int_plot_settings = dict(
        legend_loc="TopRight",
        legend_pos=[],
        xlabel="x",
        ylabel="",
        xrange=[0.0, 2.0],
        yrange=[-1.1, 2.2],
        font_size=16,
        colors={},
        lstys={},
    )
    int_plot_settings.update(plot_settings)

    # show line plot in view
    display = Show(line_plot, view, "XYChartRepresentation")
    all_series = varnames
    all_series.extend([expr.name for expr in exprs_to_plot])
    display.SeriesVisibility = all_series

    # Set line colours and styles
    cols = display.SeriesColor.GetData()
    cols_to_add = []
    lstys = display.SeriesLineStyle.GetData()
    lstys_to_add = []
    for expr in exprs_to_plot:
        try:
            lsty_idx = lstys.index(expr.name)
            lsty_defined = lsty_idx >= 0
        except:
            lsty_defined = False
        if lsty_defined:
            lstys[lsty_idx + 1] = str(int_plot_settings["lstys"].get(expr.name, 2))
        else:
            lstys_to_add.extend([expr.name, "2"])
        try:
            col_idx = cols.index(expr.name)
            col_defined = col_idx >= 0
        except:
            col_defined = False
        col_arr = get_color_array(
            expr.name, int_plot_settings["colors"].get(expr.name, "r")
        )
        if col_defined:
            for ii, el in enumerate(col_arr):
                cols[col_idx + ii] = el
        else:
            lstys_to_add.extend(col_arr)
    cols.extend(cols_to_add)
    display.SeriesColor.SetData(cols)
    lstys.extend(lstys)
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
    if int_plot_settings["legend_pos"]:
        view.LegendLocation = "Custom"
        view.LegendPosition = int_plot_settings["legend_pos"]
    else:
        view.LegendLocation = int_plot_settings["legend_loc"]

    if dt is not None:
        add_time_filter(dt, vtu_data, view, tlbl_settings)

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
