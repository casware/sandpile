import numpy as np
import scipy as sp
import scipy.stats as stats
import scipy.spatial
from matplotlib import pyplot


class SandPile:
    """SandPile class
    """

    def __init__(self, width, height, threshold=4, random=False):
        """Initialize a sandpile with the specified width and height."""
        self.width = width
        self.height = height
        self.threshold = threshold
        self.dimension = 2
        if random:
            self.grid = np.random.randint(4, 15, [width, height])

        else:
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

    def evolve(self):
        '''Evolve from the given configuration (possibly unstable) untill all sites are less than the threshold.'''
        stable = False
        while(stable == False):
            # Loop through each element, and topple it
            # Repeat this loop until all elements do not topple again
            no_topples = True
            # Toppling is abelian, so we may topple in any order
            for i in range(0, self.width):
                for j in range(0, self.height):
                    if self.grid[i,j] >= self.threshold:
                        self.topple([i,j])
                        no_topples = False

            stable = no_topples

    def topple(self, site):
        ''' Topples a site, if the number of grains is greater than the threshold
        Returns a boolean indicating whether toppling occured '''
        # Use tuple below because a list will not index properly (learned this the hard way)
        # Also, using a tuple instead of explicit destructuring means it will be easier
        # to extend to higher dimensional grid if desired
        if self.grid[tuple(site)] < self.threshold:
            return False

        neighbors = self.get_neighbors(site)
        # Move sand to neighbors
        for neighbor in neighbors:
            self.grid[tuple(neighbor)] += 1

        self.grid[tuple(site)] -= 4
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
            self.area_history.append(0)
            self.topples_history.append(0)
            self.length_history.append(0)
            return

        # If we had a topple, loop through neighbors until it dies
        buffer = self.get_neighbors(start)
        sites_affected = set([self.get_1D_coord(start)])
        distance = 0
        topples = 1
        while len(buffer) > 0:
            current = buffer[0]
            did_topple = self.topple(current)
            sites_affected.add(self.get_1D_coord(current))
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
        # Make distance the manhattan distance
        return abs(x[0] - y[0]) + abs(x[1]-y[1])

    def simulate(self, steps, n=1, site=None):
        ''' Evolve the system by dropping sand on the lattice

        steps: number of steps to evolve
        n: number of grains to drop per step
        site: coordinates (list/tuple) of site to drop on;
            if none specified, drops are made on a random site
        '''

        for i in range(steps):
            self.drop_sand(n, site)


    def ensemble_simulate(self, width, height, number_runs, n=1, site=None):
        length_hist = []
        area = []
        topples = []
        for i in range(0, number_runs):
            pile = SandPile(width, height, 4, True)
            pile.evolve()
            pile.drop_sand(n, site)
            length_hist += pile.length_history
            area += pile.area_history
            topples += pile.topples_history

        return [length_hist, area, topples]

    def get_1D_coord(self, site):
        '''A higher dimensional array can be uniquely mapped to a 1D array
        using site[0]*width + site[1].'''

        return self.width*site[0] + site[1]

    def graph(self):
        fig, (ax1, ax2, ax3, ax4, ax5) = pyplot.subplots(
            5, 1, figsize=(15, 25))
        start = int(len(self.mass_history) / 2)
        # Plot the grid
        ax1.set_title("Grid plot")
        ax1.imshow(self.grid)

        # Plot mass per site
        ax2.set_title("Mass loss:")
        scaled_mass_history = [self.mass_history[i+1] - self.mass_history[i]
                               for i in range(start, len(self.mass_history)-1)]
        ax2.hist(scaled_mass_history)

        # Plot number of topples
        ax3.set_title("Topples History")
        topples_data, exponent, location, scale = self.get_statistics(
            self.topples_history)
        ax3.set_xlabel("Topples")
        ax3.set_ylabel("Frequency")
        self.make_powerlaw_plot(topples_data, exponent, location, scale, ax3)

        # Plot Length
        ax4.set_title("Length")
        ax4.set_xlabel("Length of avalanche")
        ax4.set_ylabel("Frequency")
        length_data, exponent, location, scale = self.get_statistics(
            self.length_history)
        self.make_powerlaw_plot(length_data, exponent, location, scale, ax4)

        # Plot area
        ax5.set_title("Area")
        ax5.set_xlabel("Area of avalanche")
        ax5.set_ylabel("Frequency")
        area_data, exponent, location, scale = self.get_statistics(
            self.area_history)
        self.make_powerlaw_plot(area_data, exponent, location, scale, ax5)
        fig.savefig("output/grid.pdf")
        pyplot.close(fig)

        # Plot loss of mass

        return [exponent, location, scale]

    def get_statistics(self, field):
        '''Return power law statistics of the passed field
           Field should be one of area_history, length_history, etc. '''
        # Start our analysis mid-way through evolution, to avoid pre-critical noise
        start = self.threshold*self.height*self.width
        data = field[start:]
        exponent, location, scale = stats.powerlaw.fit(
            data)

        return [data, exponent, location, scale]

    def make_powerlaw_plot(self, data, exponent, location, scale, axis):
        '''Make a log-log plot of a power law, with data'''
        x = np.logspace(np.log10(4),
                        np.log10(np.max(data)))
        axis.plot(x, stats.powerlaw.pdf(
            x, exponent, loc=location, scale=scale))
        axis.set_xscale('log')
        axis.set_yscale('log', nonposy='clip')
        axis.hist(data, bins=x)
        axis.set_label('a =' + np.str(np.round(exponent, 3)))
        axis.legend(['a =' + np.str(np.round(exponent, 3))])