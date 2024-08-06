import os.path
from paraview.simple import (
    _DisableFirstRenderCameraReset,
    AssignViewToLayout,
    Connect,
    CreateView,
    GetAnimationScene,
    GetLayout,
    PlotOverLine,
    PythonCalculator,
    SaveAnimation,
    Show,
)
import re

from .time_filter import add_time_filter
from ..utils import (
    gen_registration_name,
    get_color_array,
    get_ugrid_bounds,
    get_vtu_data,
)

### disable automatic camera reset on 'Show'
_DisableFirstRenderCameraReset()


class PyExpr:
    def __init__(self, name, expr, data_dir=None):
        self.name = name
        self.expr = expr
        self.data_dir = data_dir


def set_series_props(display, varname, series_lbl, plot_settings):
    # Make series visible
    # all_series.extend([expr.name for expr in exprs_to_plot])
    display.SeriesVisibility = [varname]

    # Find index of series variable
    series_idx = -1
    for idx, orig_series_lbl in enumerate(list(display.SeriesLabel)):
        if orig_series_lbl == varname:
            series_idx = idx
            break
    if series_idx < 0:
        return False

    # Set display name
    display.SeriesLabel[series_idx + 1] = series_lbl

    # Set linestyle
    lstys = display.SeriesLineStyle.GetData()
    try:
        lsty_defined = lstys.index(varname) >= 0
    except:
        lsty_defined = False
    if lsty_defined:
        lstys[series_idx + 1] = str(plot_settings["lstys"].get(series_lbl, 2))
    else:
        lstys.extend([varname, "2"])
    display.SeriesLineStyle.SetData(lstys)

    # Set color
    cols = display.SeriesColor.GetData()
    try:
        col_idx = cols.index(varname)
        col_defined = col_idx >= 0
    except:
        col_defined = False
    col_arr = get_color_array(varname, plot_settings["colors"].get(series_lbl, "r"))
    if col_defined:
        for ii, el in enumerate(col_arr):
            cols[col_idx + ii] = el
    else:
        cols.extend(col_arr)
    display.SeriesColor.SetData(cols)
    return True


def line_plot_1d(
    varnames,
    data_dirs,
    output_dir,
    animation_settings={},
    axis=None,
    dt=None,
    exprs_to_plot=[],
    host="",
    output_basename="",
    plot_settings={},
    pts_arr=None,
    series_lbls=None,
    series_lbl_mode="var",
    tlbl_settings={},
    vtu_basename="",
):
    nseries = len(varnames)
    if isinstance(data_dirs, str):
        data_dirs = [data_dirs] * nseries
    elif isinstance(data_dirs, list):
        for d in data_dirs:
            assert isinstance(d, str)
    else:
        raise TypeError("Expected string or list of strings for data_dirs arg")
    assert isinstance(varnames, list)
    for vn in varnames:
        assert isinstance(vn, str)

    assert len(data_dirs) == nseries
    # Series labels
    if series_lbls is None:
        assert series_lbl_mode in ["var", "basename"]
        if series_lbl_mode == "var":
            series_lbls = varnames
        elif series_lbl_mode == "basename":
            series_lbls = [os.path.basename(d) for d in data_dirs]

    # Set line start-end points
    vtu_data = {}
    if pts_arr is None:
        midpoints = [0.0, 0.0, 0.0]
        pts = [list(midpoints), list(midpoints)]
        # Get axis lims using first data dir
        vtu_data[data_dirs[0]] = get_vtu_data(data_dirs[0], basename=vtu_basename)
        axis_min, axis_max = get_ugrid_bounds(
            vtu_data[data_dirs[0]], 0 if axis is None else axis
        )
        pts[0][axis] = axis_min
        pts[1][axis] = axis_max
        # Same start-end points for all series
        pts_arr = [pts] * nseries
    elif len(pts_arr) == 1:
        if nseries > 1:
            pts_arr = [pts_arr[0]] * nseries

    assert len(pts_arr) == nseries

    var_str = "-".join(varnames)
    default_lbl = f"{var_str}_line_plot"
    if not output_basename:
        output_basename = default_lbl

    # Ensure expressions are all instances instances of PyExpr
    for expr in exprs_to_plot:
        assert isinstance(expr, PyExpr)

    # Output path
    output_fpath = os.path.join(output_dir, output_basename + ".avi")

    if host:
        Connect(host)

    # Set up plot settings
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

    # Get animation scene
    anim_scene = GetAnimationScene()

    # Update animation scene based on data timesteps
    anim_scene.UpdateAnimationUsingDataTimeSteps()

    line_plots = []
    view = CreateView("XYChartView")
    displays = []
    for data_dir, varname, series_lbl, pts in zip(
        data_dirs, varnames, series_lbls, pts_arr
    ):
        if not data_dir in vtu_data:
            vtu_data[data_dir] = get_vtu_data(data_dir, basename=vtu_basename)

        # Create line plot
        line_plot = PlotOverLine(
            registrationName=gen_registration_name("Line"), Input=vtu_data[data_dir]
        )
        line_plot.Point1 = pts[0]
        line_plot.Point2 = pts[1]
        line_plots.append(line_plot)

        # show line plot in view
        display = Show(line_plots[-1], view, "XYChartRepresentation")
        displays.append(display)

        series_props_set = set_series_props(
            displays[-1], varname, series_lbl, int_plot_settings
        )
        if not series_props_set:
            raise ValueError(f"Variable {varname} not found in [{data_dir}] data")

    for expr_props in exprs_to_plot:
        # If no data_dir was specified for the expression, just use the first one
        expr_input = (
            vtu_data[data_dirs[0]]
            if expr_props.data_dir is None
            else vtu_data[expr_props.data_dir]
        )
        expr = PythonCalculator(registrationName=expr_props.name, Input=expr_input)
        expr.Expression = expr_props.expr
        expr.ArrayName = expr_props.name
        display = Show(expr, view, "XYChartRepresentation")
        series_props_set = set_series_props(
            display, expr.ArrayName, expr.ArrayName, int_plot_settings
        )

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
        add_time_filter(dt, vtu_data[data_dir], view, tlbl_settings)

    # Default animation settings
    int_animation_settings = dict(FrameRate=5)
    # Apply any animation settings passed by the user
    int_animation_settings.update(animation_settings)

    if "FrameWindow" in int_animation_settings:
        nframes_max = len(vtu_data[data_dir].FileName)
        fw = int_animation_settings["FrameWindow"]
        fw = [max(fw[0], 0), min(fw[1], nframes_max - 1)]

    # Add view to layout
    layout = GetLayout()
    if "ImageResolution" in int_animation_settings:
        layout.SetSize(*int_animation_settings["ImageResolution"])
    AssignViewToLayout(view=view, layout=layout, hint=0)

    # Save animation
    SaveAnimation(
        output_fpath,
        view,
        **int_animation_settings,
    )

    print(f"Saved animation to {output_fpath}")
