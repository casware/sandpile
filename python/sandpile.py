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
        self.topples_history = []   # Number of topples to reach stability in avalanche
        self.area_history = []      # Number of unique sites reached in avalanche
        self.length_history = []    # Maximum radius of avalanche

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

        self.grid[place] += n

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
        Returns a boolean indicating whether toppling occured '''
        # Use tuple below because a list will not index properly (learned this the hard way)
        # Also, using a tuple instead of explicit destructuring means it will be easier
        # to extend to higher dimensional grid if desired
        if self.grid[tuple(site)] < self.threshold:
            return [False, 0]

        neighbors = self.get_neighbors(site)
        # Move sand to neighbors
        for neighbor in neighbors:
            self.grid[tuple(neighbor)] += 1

        self.grid[tuple(site)] = 0
        return True

    def avalanche(self, start, n):
        """Run the avalanche causing all sites to topple and store the stats of
        the avalanche in the appropriate variables.
        start: site sand is dropped, beginning cascade
        n: number of grains added
        """
        did_topple = self.topple(start)

        # If no topples, update history and return
        if did_topple == False:
            self.mass_history.append(self.mass())
            self.topples_history.append(0)
            self.area_history.append(0)
            self.length_history.append(0)
            # Do not append to topples or area history since we only want stats from real topples
            return

        # If we had a topple, loop through neighbors until it dies
        buffer = self.get_neighbors(start)
        sites_affected = set()
        distance = 0
        topples = 1
        while len(buffer) > 0:
            current = buffer[0]
            did_topple = self.topple(current)
            sites_affected = sites_affected.union(tuple(current))
            distance = max(distance, self.dist(start, current))

            if(did_topple == True):
                buffer.extend(self.get_neighbors(current))

            # Remove the first element
            buffer = buffer[1:]
            topples += 1

        # Update statistics
        self.mass_history.append(self.mass())
        self.topples_history.append(topples)
        self.area_history.append(len(sites_affected))
        self.length_history.append(distance)

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
        fig, (ax1, ax2, ax3, ax4, ax5) = pyplot.subplots(5,1, figsize=(15, 20))
        # Plot the grid
        ax1.set_title("Grid plot")
        ax1.imshow(self.grid)

        # Plot mass per site
        ax2.set_title("Mass per site:")
        scaled_mass_history = np.array(self.mass_history[1:]) / (self.width * self.height)
        ax2.plot(range(len(self.mass_history[1:])), scaled_mass_history)

        # Plot number of topples
        ax3.set_title("Topples History")
        ax3.plot(range(len(self.topples_history)), self.topples_history)

        # Plot Length
        ax4.set_title("Length")
        ax4.plot(self.length_history)

        # Plot area
        ax5.set_title("Area")
        ax5.plot(self.area_history)

        fig.savefig("output/grid.pdf")
        pyplot.close(fig)

    # You are free (and encouraged) to define more methods within this class
