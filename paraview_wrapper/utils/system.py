import os
import os.path


def get_desktop_dir():
    loc = ""
    if "HOME" in os.environ:
        loc = os.path.join(os.environ["HOME"], "Desktop")
    if loc and os.path.isdir(loc):
        return loc
    else:
        raise (RuntimeError("get_desktop_dir: Desktop dir not found"))


def make_dir_on_desktop(dirname):
    desktop_dir = get_desktop_dir()
    new_dir = os.path.join(desktop_dir, dirname)
    if not os.path.isdir(new_dir):
        os.makedirs(new_dir)
    return new_dir
