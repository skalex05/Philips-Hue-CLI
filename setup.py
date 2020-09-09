import cx_Freeze
import sys
import os

executables = [cx_Freeze.Executable("hue.py",base = None)]

cx_Freeze.setup(
    name = "Hue",
    options = {"build_exe" : {"packages":["requests","pickle","argparse","ast"]}},
    version = "1.0",
    description = "A simple CLI to make controlling Philips Hue Lights easier on pc",
    executables = executables
    )
