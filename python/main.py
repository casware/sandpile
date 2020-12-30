#!/usr/bin/env python3
#################################################
#   Author: Caleb Smith
#   Student ID: 1027644
#   November 9,2020
#################################################
"""Sandpile Lab
============

This is the main file from which we run all the various routines in the
sandpile lab.

"""
from pathlib import Path

import matplotlib
import numpy as np
from joblib import Parallel, delayed  # multi-processing

from sandpile import SandPile
from cylindrical import CylindricalSandPile
from hourglass import HourGlassSandPile


def wrapper(i):
    if i == 0:
        pile = SandPile(20, 20, random=True)
        return simulate_pile(pile, 100000, "results/s20x20/", no_mass=False)
    if i == 1:
        pile = CylindricalSandPile(20, 20, random=True)
        return simulate_pile(pile, 100000, "results/c20x20/", no_mass=False)
    if i == 2:
        pile = HourGlassSandPile(20, 20, random=True)
        return simulate_pile(pile, 100000, "results/hg20x20/", no_mass=False)
    if i == 3:
        pile = SandPile(50, 50, random=True)
        return simulate_pile(pile, 100000, "results/s50x50/", no_mass=False)
    if i == 4:
        pile = CylindricalSandPile(50, 50, random=True)
        return simulate_pile(pile, 100000, "results/c50x50/", no_mass=False)
    """
    Uncomment these lines if you want: they take much longer to run
    than the others

    if i == 5:
        pile = HourGlassSandPile(50, 50, random=True)
        return simulate_pile(pile, 100000, "results/hg50x50/", no_mass=False)
    if i == 6:
        pile = SandPile(100, 100, random=True)
        return simulate_pile(pile, 100000, "results/s100x100/", no_mass=False)
    """

    if i == 7:
        SandPile.ensemble_simulate(20, 20, 10000, output='results/ensemble/')


def simulate_pile(pile, steps, output, no_mass):
    pile.simulate(steps)
    return pile.graph(output, no_mass=no_mass)


def main():
    # Saves results in ./results
    output_dir = Path.cwd() / "results"
    if not output_dir.is_dir():
        output_dir.mkdir()
    results = Parallel(n_jobs=3)(delayed(wrapper)(i)
                                 for i in range(8))


if __name__ == "__main__":
    main()
