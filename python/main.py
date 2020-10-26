#!/usr/bin/env python3
"""Sandpile Lab
============

This is the main file from which we run all the various routines in the
sandpile lab.

"""
import time
from pathlib import Path

import matplotlib
import numpy as np
import scipy as sp
import scipy.stats
from matplotlib import pyplot

from sandpile import SandPile
from cylindrical import CylindricalSandPile

def example_plotting(pile, steps, output):
    pile.simulate(steps)
    pile.graph(output)

def ensemble_simulation(width, height, steps):
    pile = SandPile(1,1)
    pile.ensemble_simulate(width, height, steps)

def main():
    # Make sure that the output/ directory exists, or create it otherwise.
    output_dir = Path.cwd() / "output"
    if not output_dir.is_dir():
        output_dir.mkdir()

    pile = CylindricalSandPile(20, 20)
    example_plotting(pile, 100000, "cylinder/")
    #ensemble_simulation(20,20, 10000)



if __name__ == "__main__":
    main()
