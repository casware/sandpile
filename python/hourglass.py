import numpy as np
import scipy as sp
import scipy.stats
from matplotlib import pyplot
from sandpile import SandPile


class HourGlassSandPile(SandPile):
    """
    Model of a sandpile with 'hour glasss' boundary conditions;
    the x and y directions wrap around and there is a central
    zone in the middle through which sand may fall.
    """

    def __init__(self, width, height, threshold=4, random=False):
        SandPile.__init__(self, width, height,
                          threshold=threshold, random=random)
        if random==True:
            for i in range(width):
                for j in range(width):
                    if self.is_central([i,j]):
                        self.grid[i,j] = 0


    def is_central(self, site):
        """
        Returns true if a site is contained in the central hole in the hourglass
        The central hole is defined to be the holes in a radius of 2 from the
        center of the grid
        """
        x = site[0]
        y = site[1]
        middle_x = np.floor(self.width / 2)
        middle_y = np.floor(self.height / 2)
        if abs(x-middle_x) < 2 and abs(y-middle_y) < 2:
            return True
        else:
            return False

    def get_neighbors(self, site):
        """
        Override get_neighbors to handle the different boundary conditions
        For hourglass boundary conditions, we fully wrap around for the x and
        y directions, but we have hole precisely in the centre.
        """
        ret = []
        x = site[0]
        y = site[1]

        # If the element is in the central hole, do not return any neighbors
        # as the will be eliminated
        if self.is_central(site):
            return []
        # Always append the x neighbors; the % handles the wrap around

        ret.append([(x - 1) % self.width, y])
        ret.append([(x+1) % self.width, y])
        ret.append([x, (y-1) % self.height])
        ret.append([x, (y+1) % self.height])

        return ret

    def topple(self, site):
        '''
        Topples a site, if the number of grains is greater than the threshold
        Returns a list of affected neighbors
        '''
        # Use tuple below because a list will not index properly (learned this the hard way)
        # Also, using a tuple instead of explicit destructuring means it will be easier
        # to extend to higher dimensional grid if desired

        # If part of the central hole, always the value to 0;
        # this allows sites to toppple their grains into the central hole
        # and ensures that once this has been done, the grains are eliminated
        if self.is_central(site):
            self.grid[tuple(site)] = 0

        if self.grid[tuple(site)] < self.threshold:
            return []

        neighbors = self.get_neighbors(site)
        # Move sand to neighbors
        for neighbor in neighbors:
            self.grid[tuple(neighbor)] += 1

        self.grid[tuple(site)] -= 4
        return neighbors

    def dist(self, x, y):
        '''Override Distance between two sites x,y'''
        # Make distance the manhattan distance
        # but need to wrap it around in both directions
        # mod out by (dimension - 1) to wrap around; subtracting 1
        # because indices start at 0
        xdist = min(abs(x[0]-y[0]), abs(self.width-(x[0] + y[0])))
        ydist = min(abs(x[1]-y[1]), abs(self.height-(x[1] + y[1])))
        return xdist + ydist
