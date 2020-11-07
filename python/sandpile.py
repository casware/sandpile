import numpy as np
from scipy.stats import spearmanr    # For calculating correlations
from matplotlib import pyplot       # For plotting
import sys                          # For printing to files
from pathlib import Path            # Create output directory

class SandPile:
    """
    SandPile class
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
        a random site if not site is given as an argument.

        Parameters
        ==========
        n: int
          The number of grains of sand of drop at this time step.  If left
          unspecified, defaults to 1.

        site: tuple or list of coordinates
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
        """Return the total mass of the grid."""
        return np.sum(self.grid)

    def get_neighbors(self, site):
        """
        Returns a list containing the coordinates of its
        nearest neighboring sites. If this list is shorter than 4, then
        it is on a boundary and thus sand toppled from this site will be deleted
        Neighbors returned in order Left, Right, Up, Down if these exist

        Parameters
        ==========
        site: a tuple or list of coordinates
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
        """
        Topples a site, if the number of grains is greater than the threshold
        Returns a list of affected neighbors.
        The returned list is empty if `site` is stable and did not topple

        Parameters
        ==========
        site: tuple or list of coordinates
        """
        # Use tuple below because a list will not index properly (learned this the hard way)
        # Also, using a tuple instead of explicit destructuring means it will be easier
        # to extend to higher dimensional grid if desired
        if self.grid[tuple(site)] < self.threshold:
            return []

        neighbors = self.get_neighbors(site)
        # Move sand to neighbors
        for neighbor in neighbors:
            self.grid[tuple(neighbor)] += 1

        self.grid[tuple(site)] -= 4
        return neighbors

    def avalanche(self, start):
        """Run the avalanche causing all sites to topple and store the stats of
        the avalanche in the appropriate variables.
        start: site sand is dropped, beginning cascade

        Parameters
        ==========
        start: tuple or list of coordinates of the site where the avalanche began
        """
        buffer = self.topple(start)

        # If no topples, update history and return
        if len(buffer) == 0:
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

            # If there was a topple, increment topples
            # and append the affected sites to buffer
            if len(current_neighbors) > 0:
                buffer.extend(current_neighbors)
                topples += 1

            # Need to make sure that the current site is actually stable
            if self.grid[tuple(current)] >= self.threshold:
                buffer.append(current)

            # Remove the first element
            buffer = buffer[1:]

        # Update statistics
        self.mass_history.append(self.mass())
        self.topples_history.append(topples)
        self.area_history.append(len(sites_affected))
        self.length_history.append(distance)

    def dist(self, x, y):
        """
        Distance between two sites x,y

        Parameters
        ==========
        x: tuple or list of coordinates
        y: tuple or list of coordinates
        """
        # Make distance the manhattan distance
        return abs(x[0] - y[0]) + abs(x[1]-y[1])

    def simulate(self, steps, n=1, site=None):
        """
        Evolve the system by dropping sand on the lattice

        Parameters
        ==========
        steps: int, number of steps to evolve
        n: int, number of grains to drop per step
        site: tuple or list of coordinates of site to drop grains on;
            if none specified, drops are made on a random site
        """
        for _ in range(steps):
            self.drop_sand(n, site)

    # In a refactor, this function uses logic very similar to that
    # of the avalanche function; this could likely be split out into
    # a separate function and re-used in both locations
    def stabilize(self):
        """
        Evolve from the current grid (possibly unstable) until all sites are less than the threshold.
        For use in ensemble simulations where the grid is initialized to have a value higher than
        the threshold and allow to relax to a stable configuration.
        """
        # Find all the unstable sites and start toppling them
        unstable = []
        for i in range(0, self.width):
            for j in range(0, self.height):
                if self.grid[i, j] >= self.threshold:
                    unstable.append((i, j))

        # Topple until there is nothing left to topple
        while len(unstable) > 0:
            affected_neighbors = self.topple(unstable[0])

            if len(affected_neighbors) > 0:
                unstable.extend(affected_neighbors)

            # Need to make sure that the current site is actually stable
            if self.grid[tuple(unstable[0])] >= self.threshold:
                unstable.append(unstable[0])

            unstable = unstable[1:]  # Remove current element

    @staticmethod
    def ensemble_simulate(width, height, number_runs, n=1, site=None, output='ensemble/'):
        """
        Create an ensemble of sandpiles and collect statistics about them.
        To not have statistics which are warped by
        the random initialization, create a pile which is
        unstable, stabilize it, and then collect five statistics
        from it. Note there are many other possible ways to perform an ensemble
        simulation.

        Parameters
        ==========
        width: int, width of lattices
        height: int, height of lattices
        number_runs: int, number of systems to collect data on
        n: int, number of grains to drop each simulation
        site: tuple or list of coordinates to drop grains on
        """
        length_hist = []
        area = []
        topples = []
        mass_history = []
        for _ in range(0, number_runs):
            pile = SandPile(width, height, threshold=5, random=True)
            pile.threshold = 4
            pile.stabilize()
            pile.simulate(50, n, site)
            # Need to use .extend not .append because list
            length_hist.extend(pile.length_history[-1:])
            area.extend(pile.area_history[-1:])
            topples.extend(pile.topples_history[-1:])
            mass_history.extend(pile.mass_history[-1:])

        # Plot results
        pile = SandPile(width, height)
        pile.pre_critical = False
        pile.length_history = length_hist
        pile.area_history = area
        pile.topples_history = topples
        pile.mass_history = mass_history
        # Insert a 0 at beginning so all our correlations are properly aligned
        pile.mass_history.insert(0, 0)
        pile.graph(output, no_grid=True)
        return pile

    def get_1D_coord(self, site):
        '''A higher dimensional array can be uniquely mapped to a 1D array
        using site[0]*width + site[1].'''

        return self.width*site[0] + site[1]

    # In a larger project, we would likely want to split out the following methods
    # into a separate class or interface as they are really helper functions
    # for displaying and recording results and not directly tied to the actual
    # details of the sand pile. However, because of the limited scope of this
    # project, it was not worth abstracting these into a separate class
    # as we will not be re-using them
    def graph_loss(self, output, no_mass, fig, ax):
        """
        Graph the mass loss as a power law.
        """
        if no_mass == False:
            # Shift mass loss and multiply by -1 so we can take log
            loss_history = np.array([self.mass_history[i+1] - self.mass_history[i]
                                     for i in range(0, len(self.mass_history)-1)])
            max_loss = np.max(loss_history)
            scaled_history = -1 * (loss_history - max_loss)

            # The upper and lower bounds are best guesses about what are good
            # ranges to fit power laws
            loss_data, loss_frequency, exponent, intercept = self.get_statistics(
                scaled_history, lower=max_loss, upper=max_loss*1.2)

            ax.set_xlabel("Mass Loss")
            ax.set_ylabel("Frequency")
            self.make_powerlaw_plot(
                loss_data, loss_frequency, ax, exponent=exponent, intercept=intercept)

            # Mass sizes overlap if we are not careful
            pyplot.xticks(rotation=90)
            pyplot.savefig(output + 'lossAnalysis.png')
            pyplot.cla()  # clear axis

            self.make_powerlaw_plot(loss_data, loss_frequency, ax)
            pyplot.xticks(rotation=90)

            # Mass size labels overlap if we are not careful
            for label in ax.get_xticklabels():
                label.set_ha("right")

            fig.savefig(output+'loss.png')

            pyplot.cla()

            return exponent

    def graph_topples(self, output, fig, ax):
        """
        Graph the topples number as a power law.
        """
        ax.set_xlabel("Topples")
        ax.set_ylabel("Frequency")
        topples_data, topples_frequency, topples_exponent, intercept = self.get_statistics(
            self.topples_history)
        self.make_powerlaw_plot(
            topples_data, topples_frequency, ax, exponent=topples_exponent, intercept=intercept)
        fig.savefig(output + 'topplesAnalysis.png')
        pyplot.cla()  # clear axis

        ax.set_xlabel("Topples")
        ax.set_ylabel("Frequency")
        self.make_powerlaw_plot(
            topples_data, topples_frequency, ax)
        fig.savefig(output + 'topples.png')
        pyplot.cla()  # clear axis
        return topples_exponent

    def graph_length(self, output, fig, ax):
        """
        Graph the length as a power law.
        """
        ax.set_xlabel("Length")
        ax.set_ylabel("Frequency")
        length_data, length_frequency, length_exponent, intercept = self.get_statistics(
            self.length_history, upper=(self.width+self.height) / 2)
        self.make_powerlaw_plot(
            length_data, length_frequency, ax, exponent=length_exponent, intercept=intercept)
        fig.savefig(output + 'lengthAnalysis.png')
        pyplot.cla()  # clear axis

        ax.set_xlabel("Length")
        ax.set_ylabel("Frequency")
        self.make_powerlaw_plot(
            length_data, length_frequency, ax)
        fig.savefig(output + 'length.png')
        pyplot.cla()  # clear axis

        return length_exponent

    def graph_area(self, output, fig, ax):
        """
        Graph the area as a power law.
        """
        ax.set_xlabel("Area")
        ax.set_ylabel("Frequency")
        area_data, area_frequency, area_exponent, intercept = self.get_statistics(
            self.area_history, upper=min((self.width*self.height)/2, 300),
            lower=min(self.width, self.height, 20))
        self.make_powerlaw_plot(
            area_data, area_frequency, ax, exponent=area_exponent, intercept=intercept)
        fig.savefig(output + 'areaAnalysis.png')
        pyplot.cla()
        # Plot without analysis
        ax.set_xlabel("Area")
        ax.set_ylabel("Frequency")
        self.make_powerlaw_plot(
            area_data, area_frequency, ax)
        fig.savefig(output + 'area.png')
        pyplot.cla()

        return area_exponent

    def graph_density(self, output, no_grid, fig, ax):
        """
        Graph the mass density as a power law, and the grid
        as a colormesh.
        """
        ax.set_xlabel("Density")
        ax.set_ylabel("Frequency")
        start = self.get_start_index() + 1  # Add one since we have a leading 0
        data = np.array(self.mass_history[start:]) / (self.width*self.height)
        mean_density = np.mean(data)
        counts = np.unique(data[start:], return_counts=True)
        ax.scatter(counts[0], counts[1])
        fig.savefig(output+'mass.png')
        pyplot.cla()

        # Show the grid if desired scale
        if no_grid == False:
            fig2, ax2 = pyplot.subplots(constrained_layout=True)
            psm = ax2.pcolormesh(self.grid, cmap='inferno', vmin=0, vmax=3)
            fig2.colorbar(psm, ax=ax2)
            fig2.savefig(output+'grid.png')
            pyplot.close(fig2)

            np.savetxt(output + 'grid.txt', self.grid, delimiter=',')
        return mean_density

    def graph(self, output='results/output/', no_mass=False, no_grid=False):
        '''
        Save plots of the important figures and the correlation between them
        to the 'output' directory.
        This function assumes the 'output' directory exists; if it does not
        an error will occur.
        '''
        fig, ax = pyplot.subplots()
        output_dir = Path.cwd() / output
        if not output_dir.is_dir():
            output_dir.mkdir()

        # Plot mass loss
        self.graph_loss(output, no_mass, fig, ax)
        topples_exponent = self.graph_topples(output, fig, ax)
        length_exponent = self.graph_length(output, fig, ax)
        area_exponent = self.graph_area(output, fig, ax)
        mean_density = self.graph_density(output, no_grid, fig, ax)
        self.print_correlation(output + 'correlation.txt')

        # Close the figure
        pyplot.close(fig)
        return [topples_exponent, length_exponent, area_exponent, mean_density]

    def get_statistics(self, field, upper=102, lower=3):
        '''Return power law statistics of the passed field
           Field should be one of area_history, length_history, etc.
           The upper/lower range was selected by a process of trial and error;
           it works tolerably well for length, area, topples, losses
           at least for small grid sizes; likely will be better fit
           for larger grid sizes
        '''
        # Start our analysis mid-way through evolution, to avoid pre-critical noise
        start = self.get_start_index()
        data = field[start:]
        if len(data) == 0:
            raise Exception("Not enough data")

        # Get the counts; remove 0 so we can take a logarithm
        counts = np.unique(data, return_counts=True)
        counts = np.delete(counts, 0, 1)  # Delete first column to remove 0
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

    def make_powerlaw_plot(self, log_data, log_frequency, axis, exponent=None, intercept=None):
        """
        Make a log-log plot of a power law, with data
        """
        axis.set_yscale('log')
        axis.set_xscale('log')
        axis.scatter(np.exp(log_data), np.exp(log_frequency))

        # If exponent/intercept are defined, plot them as well
        if exponent is not None and intercept is not None:
            plot_x = np.linspace(np.min(log_data), np.max(
                log_data), dtype=np.float64)
            plot_y = exponent*plot_x + intercept
            transformed_x = np.exp(plot_x)
            transformed_y = np.exp(plot_y)
            axis.plot(transformed_x, transformed_y, color='red')
            axis.set_label('a =' + np.str(np.round(exponent, 3)))
            axis.legend(['a =' + np.str(np.round(exponent, 3))])

    def correlation(self, data1, data2):
        return spearmanr(data1, data2)

    def calculate_correlations(self):
        """
        Calculates the correlation between area and 1) length 2) mass loss 3) topple number.
        Returns a list containing the correlation coefficients calculated between
        area and each of the quantities in the above order:
        area-length correlation, area-mass loss correlation, area-topples number.
        """
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
