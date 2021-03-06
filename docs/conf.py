# Automatically generated by PyB
import sys
from os import path

sphinx_pyb_dir = path.abspath(path.join(path.dirname(__file__) if __file__ else ".", "../target/sphinx_pyb"))
sphinx_pyb_module = "sphinx_pyb_conf"
sphinx_pyb_module_file = path.abspath(path.join(sphinx_pyb_dir, sphinx_pyb_module + ".py"))

sys.path.insert(0, sphinx_pyb_dir)

if not path.exists(sphinx_pyb_module_file):
    raise RuntimeError("No PyB-based Sphinx configuration found in " + sphinx_pyb_module_file)

from sphinx_pyb_conf import *

# Overwrite PyB-settings here statically if that's the thing that you want
