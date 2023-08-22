import omni.usd
import os
import sys
import math

import carb.settings


_settings = None


def _init_settings():
    global _settings
    if _settings is None:
        _settings = carb.settings.get_settings()
    return _settings


def get_setting(name, default, db=False):
    settings = _init_settings()
    key = f"/persistent/omni/sphereflake/{name}"
    val = settings.get(key)
    if db:
        oval = val
        if oval is None:
            oval = "None"
    if val is None:
        val = default
    if db:
        print(f"get_setting {name} {oval} {val}")
    return val


def save_setting(name, value):
    settings = _init_settings()
    key = f"/persistent/omni/sphereflake/{name}"
    settings.set(key, value)


def truncf(number, digits) -> float:
    # Improve accuracy with floating point operations, to avoid truncate(16.4, 2) = 16.39 or truncate(-1.13, 2) = -1.12
    nbDecimals = len(str(number).split('.')[1])
    if nbDecimals <= digits:
        return number
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


def delete_if_exists(primpath: str) -> None:
    ctx = omni.usd.get_context()
    stage = ctx.get_stage()
    if stage.GetPrimAtPath(primpath):
        stage.RemovePrim(primpath)
        # okc.execute("DeletePrimsCommand", paths=[primpath])


def write_out_path(fname: str = 'd:/nv/ov/path.txt') -> None:
    # Write out the path to a file
    path = os.environ["PATH"]
    with open(fname, "w") as f:
        npath = path.replace(";", "\n")
        f.write(npath)


def write_out_syspath(fname: str = 'd:/nv/ov/syspath.txt', indent=False) -> None:
    # Write out the python syspath to a file
    # Indent should be True if to be used for the settings.json python.analsys.extraPaths setting
    pplist = sys.path
    with open(fname, 'w') as f:
        for line in pplist:
            nline = line.replace("\\", "/")
            if indent:
                nnline = f"        \"{nline}\",\n"
            else:
                nnline = f"\"{nline}\",\n"
            f.write(nnline)


def read_in_syspath(fname: str = 'd:/nv/ov/syspath.txt') -> None:
    # Read in the python path from a file
    with open(fname, 'r') as f:
        for line in f:
            nline = line.replace(',', '')
            nline = nline.replace('"', '')
            nline = nline.replace('"', '')
            nline = nline.replace('\n', '')
            nline = nline.replace(' ', '')
            sys.path.append(nline)


