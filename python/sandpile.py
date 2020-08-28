import numpy as np
import scipy as sp
import scipy.spatial
from matplotlib import pyplot


class SandPile:
    """SandPile class
    """

    def __init__(self, width, height, threshold=4):
        """Initialize a sandpile with the specified width and height."""
        self.width = width
        self.height = height
        self.threshold = threshold
        self.dimension = 2
        self.grid = np.zeros((width, height), dtype=int)

        # We may want to keep track of the overall mass of the sand pile
        # overtime.  The following array will store the masses at each time
        # step (so that `len(self.mass_history)` is equal to the number of time
        # steps the sand pile has been running).
        self.mass_history = [0]
        # You probably will want to define other attributes to store statistics.
        self.topples_history = []
        self.area_history = []
        # It is good practice to define *all* class attributes in the
        # `__init__` function, even if they get redefined later.  You may want
        # to define variables which are used to keep track of avalanches.

    def drop_sand(self, n=1, site=None):
        """Add `n` grains of sand to the grid.  Each grains of sand is added to
        a random site.

        This function also increments the time by 1 and update the internal
        `mass_history`.  Depending on how you want to code things, you may wish
        to also run the avalanche (alternatively, the avalanching might be
        executed elsewhere).

        Parameters
        ==========
        n: int
          The number of grains of sand of drop at this time step.  If left
          unspecified, defaults to 1.

        site:
          The site on which the grain(s) of sand should be dropped.  If `None`,
          a random site is used.

        """
        place = site
        if site == None:
            place = (np.random.randint(0, self.width),
                     np.random.randint(0, self.height))
        else:
            place = tuple(site)

        self.grid[place] += 1

        # Call avalanche to stabilize the configuration and updated as needed
        self.avalanche(place, n)

    def mass(self):
        """Return the mass of the grid."""
        return np.sum(self.grid)

    def get_neighbors(self, site):
        """
        site: a list of coordinates
        Returns a list containing the coordinates of its
        nearest neighboring sites. If this list is shorter than 4, then
        it is on a boundary and thus sand toppled from this site will be deleted
        Neighbors returned in order Left, Right, Up, Down if these exist
        """
        ret = []
        x = site[0]
        y = site[1]
        if x > 0 and x < self.width:
            ret.append([x - 1, y])
        if x < (self.width-1):
            ret.append([x+1, y])
        if y > 0 and y < self.height:
            ret.append([x, y-1])
        if y < (self.height - 1):
            ret.append([x, y + 1])

        return ret

    def topple(self, site):
        ''' Topples a site, if the number of grains is greater than the threshold
        Returns a boolean indicating whether toppling occured and the number grains deleted '''
        if self.grid[tuple(site)] < self.threshold:
            return [False, 0]

        neighbors = self.get_neighbors(site)
        deleted = 2*self.dimension - len(neighbors)
        # Move sand to neighbors
        for neighbor in neighbors:
            self.grid[tuple(neighbor)] += 1

        self.grid[tuple(site)] = 0
        return [True, deleted]

    def avalanche(self, start, n):
        """Run the avalanche causing all sites to topple and store the stats of
        the avalanche in the appropriate variables.
        n: number of grains added
        """
        did_topple, deleted = self.topple(start)

        # If no topples, update history and return
        if did_topple == False:
            self.mass_history.append(self.mass_history[-1] + n)
            # Do not append to topples or area history since we only want stats from real topples
            return

        # If we had a topple, loop through neighbors until it dies
        buffer = self.get_neighbors(start)
        sites_affected = set()
        distance = 0
        topples = 1
        while len(buffer) > 0:
            current = buffer[0]
            did_topple, new_deleted = self.topple(current)
            deleted += new_deleted
            sites_affected = sites_affected.union(tuple(current))
            distance = max(distance, self.dist(start, current))

            if(did_topple == True):
                buffer.extend(self.get_neighbors(current))

            # Remove the first element
            buffer = buffer[1:]
            topples += 1

        # Update statistics
        self.mass_history.append(self.mass_history[-1] + n - deleted)
        self.topples_history.append(topples)
        self.area_history.append(len(sites_affected))

    def dist(self, x, y):
        '''Distance between two sites x,y'''
        return max(abs(x[0] - y[0]), abs(x[1]-y[1]))

    def simulate(self, steps, n=1, site=None):
        ''' Evolve the system by dropping sand on the lattice

        steps: number of steps to evolve
        n: number of grains to drop per step
        site: coordinates (list/tuple) of site to drop on;
            if none specified, drops are made on a random site
        '''
        for i in range(steps):
            self.drop_sand(n, site)


    def graph(self):
        fig, ax = pyplot.subplots()
        ax.set_title("Grid plot")
        ax.imshow(self.grid)

    # You are free (and encouraged) to define more methods within this class
