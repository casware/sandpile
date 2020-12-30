#################################################
#   Author: Caleb Smith
#   Student ID: 1027644
#   November 9,2020
#################################################
import numpy as np
import scipy as sp
import scipy.stats
from matplotlib import pyplot
from sandpile import SandPile


class CylindricalSandPile(SandPile):
    """
    Model of a sandpile with cylindrical boundary conditions;
    the x-direction wraps together, so grains can only fall off
    the y-direction
    """

    def __init__(self, width, height, threshold=4, random=False):
        SandPile.__init__(self, width, height, threshold=threshold, random=random)

    def get_neighbors(self, site):
        """
        Override get_neighbors to handle the different boundary conditions
        For cylindrical boundary conditions, we want to identify the first and
        the last column and make sure we only act on one copy
        """

        ret = []
        x = site[0]
        y = site[1]
        # Always append the x neighbors; the % handles the wrap around
        ret.append([(x - 1) % self.width, y])
        ret.append([(x+1) % self.width, y])
        if y > 0 and y < self.height:
            ret.append([x, y-1])
        if y < (self.height - 1):
            ret.append([x, y + 1])

        return ret

    def dist(self, x, y):
        '''Override Distance between two sites x,y'''
        # Make distance the manhattan distance
        # but need to wrap it around in the x-direction
        xdist = min(abs(x[0]-y[0]), abs(self.width - (x[0] + y[0])))
        ydist = abs(x[1]-y[1])
        return xdist + ydist
