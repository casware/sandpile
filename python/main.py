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

def example_plotting():
   pile = SandPile(40, 40)
   for i in range(100):
       pile.drop_sand()

   pile.graph()

def main():
    # Make sure that the output/ directory exists, or create it otherwise.
    output_dir = Path.cwd() / "output"
    if not output_dir.is_dir():
        output_dir.mkdir()

    pile = SandPile(8,8)

    pile.simulate(11, 1, [0,0])
    print('Mean mass:')
    print(np.mean(pile.grid))
    print("Max:")
    print(np.max(pile.grid))
    print(pile.grid)
    example_plotting()



if __name__ == "__main__":
    main()
