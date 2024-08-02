import sys


def report_kwargs(kwargs):
    caller_name = sys._getframe().f_back.f_code.co_name
    if kwargs:
        print(f"Keyword args for {caller_name} are: ")
    else:
        print(f"No kwargs supplied to {caller_name}")

    max_key_len = max([len(k) for k in kwargs.keys()])
    if max_key_len > 50:
        raise RuntimeError(f"Very long key encountered in max_key_len {max_key_len}")

    for k, v in kwargs.items():
        if type(k) is not str:
            raise ValueError("report_kwargs: non string key in kwargs dict?!")
        print(f"  {k.rjust(max_key_len)} = {v}")


def set_default_kwargs(kwargs, defaults):
    for key in defaults:
        kwargs[key] = kwargs.pop(key, defaults[key])
