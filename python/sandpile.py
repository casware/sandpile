import numpy as np
from scipy.stats import pearsonr    # For calculating correlations
from matplotlib import pyplot       # For plotting
import sys                          # For printing to files
from pathlib import Path            # Create output directory
from numba import jit, boolean, int64

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
            self.grid = np.random.randint(1, threshold, [width, height])
            self.pre_critical = False

        else:
            self.grid = np.zeros((width, height), dtype=int)
            self.pre_critical = True

        # We may want to keep track of the overall mass of the sand pile
        # over time.  The following array will store the masses at each time
        # step (so that `len(self.mass_history)` is equal to the number of time
        # steps the sand pile has been running).
        # Need to start with 0 because we are going to take the difference
        self.mass_history = [0]
        self.topples_history = []   # Number of topples to reach stability in avalanche
        self.area_history = []      # Number of unique sites reached in avalanche
        self.length_history = []    # Maximum radius of avalanche

    def drop_sand(self, n=1, site=None):
        """Add `n` grains of sand to the grid.  Each grains of sand is added to
        a random site.

        This function also increments the time by 1 and update the internal
        `mass_history`.
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
        self.avalanche(place)

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
        # Better way: find all the unstable sites and start toppling them
        unstable = np.zeros((1,2), dtype=int)
        for i in range(0, self.width):
            for j in range(0, self.height):
                if self.grid[i, j] >= self.threshold:
                    unstable= np.concatenate((unstable, [[i,j]]))

        # Topple until there is nothing left to topple
        while len(unstable) > 0:
            did_topple = self.topple(unstable[0])
            if did_topple == True:
                neighbors = self.get_neighbors(unstable[0])
                unstable = np.concatenate((unstable, neighbors))

            unstable = unstable[1:] # Remove current element

    def topple(self, site):
        ''' Topples a site, if the number of grains is greater than the threshold
        Returns a boolean indicating whether toppling occured '''
        # Use tuple below because a list will not index properly (learned this the hard way)
        # Also, using a tuple instead of explicit destructuring means it will be easier
        # to extend to higher dimensional grid if desired
        if self.grid[tuple(site)] < self.threshold:
            return []

        neighbors = self.get_neighbors(site)
        # Move sand to neighbors
        for neighbor in neighbors:
            self.grid[tuple(neighbor)] += 1

        self.grid[tuple(site)] -= self.threshold
        return neighbors

    def avalanche(self, start):
        """Run the avalanche causing all sites to topple and store the stats of
        the avalanche in the appropriate variables.
        start: site sand is dropped, beginning cascade
        n: number of grains added
        """
        buffer = self.topple(start)

        # If no topples, update history and return
        if len(buffer) > 0:
            self.mass_history.append(self.mass())
            self.area_history.append(0)
            self.topples_history.append(0)
            self.length_history.append(0)
            return

        # If we had a topple, loop through neighbors until it dies
        sites_affected = set([self.get_1D_coord(start)])
        distance = 0
        topples = 1
        while len(buffer) > 0:
            current = buffer[0]
            current_neighbors = self.topple(current)
            sites_affected.add(self.get_1D_coord(current))
            distance = max(distance, self.dist(start, current))

            if len(current_neighbors) > 0:
                buffer.extend(current_neighbors)

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
        mass_history = []
        for i in range(0, number_runs):
            pile = SandPile(width, height, 4, True)
            pile.evolve()
            pile.drop_sand(n, site)
            # Need to use .extend not .append because list
            length_hist.extend(pile.length_history)
            area.extend(pile.area_history)
            topples.extend(pile.topples_history)
            mass_history.append(pile.mass())

        # Plot results
        pile = SandPile(width, height)
        pile.length_history = length_hist
        pile.area_history = area
        pile.topples_history = topples
        pile.mass_history = mass_history
        # Insert a 0 at beginning so all our correlations are properly aligned
        pile.mass_history.insert(0, 0)
        pile.graph('ensemble1/')

    def get_1D_coord(self, site):
        '''A higher dimensional array can be uniquely mapped to a 1D array
        using site[0]*width + site[1].'''

        return self.width*site[0] + site[1]

    def graph(self, output='output/', no_mass=False):
        '''
        Save plots of the important figures and the correlation between them
        to the 'output' directory.
        This function assumes the 'output' directory exists; if it does not
        an error will occur.
        Consider refactoring into separate functions.
        '''
        fig, ax = pyplot.subplots()
        output_dir = Path.cwd() / output
        if not output_dir.is_dir():
            output_dir.mkdir()

        # Plot mass per site
        if no_mass != True:
            ax.set_title("Mass loss:")
            # Shift mass loss and multiply by -1 so we can take log
            loss_history = np.array([self.mass_history[i+1] - self.mass_history[i]
                                     for i in range(0, len(self.mass_history)-1)])
            max_loss = np.max(loss_history)
            scaled_history = -1*(loss_history - max_loss)
            loss_data, loss_frequency, exponent, intercept = self.get_statistics(
                scaled_history)

            # Shift and scale back to original:
            loss_data = -1*loss_data
            exponent = -1*exponent
            ax.set_xlabel("log(loss)")
            ax.set_ylabel("log(frequencey)")
            self.make_powerlaw_plot(
                loss_data, loss_frequency, ax, exponent=exponent, intercept=intercept)
            fig.savefig(output + 'loss.png')
            pyplot.cla()  # clear axis

        # Plot number of topples
        # Because of the geometry of the system, we guess most topples
        # will be a multiple of 4. Only look at these
        # when we compute our power law to see if this gives a better
        # result
        ax.set_title("Topples History")
        common_topples = [
            topple for topple in self.topples_history if topple % 4 == 0]
        _, _, exponent, intercept = self.get_statistics(
            common_topples)
        topples_data, topples_frequency, _, _ = self.get_statistics(
            self.topples_history)
        ax.set_xlabel("log(topples)")
        ax.set_ylabel("log(frequencey)")
        self.make_powerlaw_plot(
            topples_data, topples_frequency, ax, exponent=exponent, intercept=intercept)
        fig.savefig(output + 'topples.png')
        pyplot.cla()  # clear axis

        # Plot Length
        ax.set_title("Length")
        ax.set_xlabel("Length of avalanche")
        ax.set_ylabel("Frequency")
        length_data, length_frequency, exponent, intercept = self.get_statistics(
            self.length_history)
        self.make_powerlaw_plot(
            length_data, length_frequency, ax, exponent=exponent, intercept=intercept)
        fig.savefig(output + 'length.png')
        pyplot.cla()  # clear axis

        # Plot area
        ax.set_title("Area")
        ax.set_xlabel("log(area)")
        ax.set_ylabel("log(frequency)")
        area_data, area_frequency, exponent, intercept = self.get_statistics(
            self.area_history)
        self.make_powerlaw_plot(
            area_data, area_frequency, ax, exponent=exponent, intercept=intercept)
        fig.savefig(output + 'area.png')
        pyplot.cla()

        # Plot mass
        ax.set_title("Mass Density")
        ax.set_xlabel("Density")
        ax.set_ylabel("Frequency")
        start = self.get_start_index()
        data = np.array(self.mass_history) / (self.width*self.height)
        counts = np.unique(data[start:], return_counts=True)
        ax.scatter(counts[0], counts[1])
        fig.savefig(output+'mass.png')
        pyplot.cla()

        self.print_correlation(output + 'correlation.txt')

    def get_statistics(self, field):
        '''Return power law statistics of the passed field
           Field should be one of area_history, length_history, etc. '''
        # Start our analysis mid-way through evolution, to avoid pre-critical noise
        start = self.get_start_index()
        data = field[start:]
        if len(data) == 0:
            raise Exception("Not enough data")

        # This range was selected by a process of trial and error;
        # it works tolerably well for length, area, topples, losses
        # at least for small grid sizes; likely will be better fit
        # for larger grid sizes
        lower = 3
        upper = 102

        # Get the counts; remove 0 so we can take a logarithm
        counts = np.unique(data, return_counts=True)
        counts = np.delete(counts, 0, 1)
        log_data, log_frequency = np.log(counts)

        # Keep the values which were between lower and upper; need to take the log
        # of upper and lower since we have taken the log of the data
        filtered_log_area = log_data[(log_data > np.log(
            lower)) & (log_data < np.log(upper))]
        filtered_log_frequency = log_frequency[(
            log_data > np.log(lower)) & (log_data < np.log(upper))]

        exponent, intercept = np.polyfit(
            filtered_log_area, filtered_log_frequency, 1)

        return [log_data, log_frequency, exponent, intercept]


    def make_powerlaw_plot(self, log_data, log_frequency, axis, exponent='None', intercept='None'):
        '''Make a log-log plot of a power law, with data'''
        axis.set_yscale('log')
        axis.set_xscale('log')
        axis.scatter(np.exp(log_data), np.exp(log_frequency))

        # If exponent/intercept are defined, plot them as well
        if type(exponent) != 'str' and type(intercept) != 'str':
            plot_x = np.linspace(np.min(log_data), np.max(log_data))
            plot_y = (lambda x: exponent*x + intercept)(plot_x)
            transformed_x = np.exp(plot_x)
            transformed_y = np.exp(plot_y)
            axis.plot(transformed_x, transformed_y, color='red')
            axis.set_label('a =' + np.str(np.round(exponent, 3)))
            axis.legend(['a =' + np.str(np.round(exponent, 3))])

    def correlation(self, data1, data2):
        return pearsonr(data1, data2)

    def calculate_correlations(self):
        ''' Calculates the correlation between area and 1) length 2) mass loss 3) topple number
            It returns a list containing the correlation coefficients calculated between
            area and each of the quantities in the above order:
            area-length correlation, area-mass loss correlation, area - topples number
        '''

        start = self.get_start_index()
        len_data = np.array(self.length_history[start:])
        area_data = np.array(self.area_history[start:])
        loss_data = np.array([self.mass_history[i+1] - self.mass_history[i]
                              for i in range(start, len(self.mass_history) - 1)])

        topples_data = np.array(self.topples_history[start:])

        # Calculate correlations between area and the other quantities
        area_len_correlation = self.correlation(len_data, area_data)
        area_loss_correlation = self.correlation(area_data, loss_data)
        area_topples_correlation = self.correlation(area_data, topples_data)

        return [area_len_correlation, area_loss_correlation, area_topples_correlation]

    def calculate_average_mass(self):
        start = self.get_start_index()
        data = np.array(self.mass_history[start:]) / (self.width*self.height)
        return np.mean(data)

    def get_start_index(self):
        if self.pre_critical == True:
            return int(self.threshold*self.width*self.height / 2)
        else:
            return 0

    def print_correlation(self, file_name):
        correlations = self.calculate_correlations()
        mass_average = self.calculate_average_mass()
        original_stdout = sys.stdout  # Save a reference to the original standard output

        with open(file_name, 'w') as f:
            sys.stdout = f  # Change the standard output to the file
            print(
                'Area-Length Correlation: {}: pvalue: {}'.format(correlations[0][0], correlations[0][1]))
            print(
                'Area-Loss Correlation: {}: pvalue: {}'.format(correlations[1][0], correlations[1][1]))
            print(
                'Area-Topples Correlation: {}: pvalue: {}'.format(correlations[2][0], correlations[2][1]))
            print('Average Mass: {}'.format(mass_average))
            sys.stdout = original_stdout  # Reset the standard output to its original value
