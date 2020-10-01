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
pile = SandPile(50, 50, 4, True)
pile.evolve()

def example_plotting(pile, steps):
    pile.simulate(steps)
    log_hist(pile.area_history[])
    pile.graph()

def log_hist(data):
    counts = np.unique(data, return_counts=True)
    counts = np.delete(counts,0,1)
    x,y = np.log(counts)
    pyplot.scatter(x,y)

def main():
    # Make sure that the output/ directory exists, or create it otherwise.
    output_dir = Path.cwd() / "output"
    if not output_dir.is_dir():
        output_dir.mkdir()




if __name__ == "__main__":
    main()
