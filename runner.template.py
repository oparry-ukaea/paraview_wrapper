from NESO import gen_movie, plot_fluid_particle_img
from utils import get_desktop_dir, get_output_dir, avi_to_mp4


plot_fluid_particle_img(
    data_dir="[NOT_SET]",
    output_dir=get_output_dir(),
    output_time=39.0,
)

fld_name = "ne"
gen_movie(
    fld_name,
    data_dir="[NOT_SET]",
    output_dir=get_desktop_dir(),
    output_fname=f"{fld_name}.avi",
    particle_fname="particle_trajectory.h5part",
    particle_props=dict(),
    vtu_basename="[NOT_SET]",
    animation_settings=dict(FrameRate=8, FrameWindow=[0, 200], Quality=2),
    view_settings=dict(
        pos=[4.2, 19.0, 3.2], fpt=[0.0, 0.0, 5.0], up=[1.0, -0.2, 0.1], pscale=6.1
    ),
    data_settings=dict(
        range=[-0.5, 5.0], opacities=[(-0.5, 0.0), (0.3, 0.0), (1.5, 0.8), (5.0, 1.0)]
    ),
)
avi_to_mp4(get_desktop_dir(), fld_name)
