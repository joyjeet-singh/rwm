"""Moved to scripts/s8_runtime.py in round 2, T8, so reproduce.sh can drive it (stage 20t7).
This stub runs the moved script, so the path recorded in earlier session logs still works."""
import os
import runpy

runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, "scripts", "s8_runtime.py"),
               run_name="__main__")
