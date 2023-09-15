import ffmpeg
import os.path


def avi_to_mp4(common_dir, fbase, fpath_in="", fpath_out="", ffmpeg_output_options={}):
    if not fpath_in:
        fpath_in = os.path.join(common_dir, fbase + ".avi")
    if not fpath_out:
        fpath_out = os.path.join(common_dir, fbase + ".mp4")
    ffmpeg_output_options_int = dict(
        vcodec="libx264", vf="pad=ceil(iw/2)*2:ceil(ih/2)*2"
    )
    ffmpeg_output_options_int.update(ffmpeg_output_options)
    ffmpeg.input(fpath_in, f="avi").output(
        fpath_out, f="mp4", **ffmpeg_output_options_int
    ).run()
