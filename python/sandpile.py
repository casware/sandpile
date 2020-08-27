import numpy as np
import scipy as sp
import scipy.spatial


class SandPile:
    """SandPile class
    """

    def __init__(self, width, height, threshold=4):
        """Initialize a sandpile with the specified width and height."""
        self.width = width
        self.height = height
        self.threshold = threshold

        self.grid = np.zeros((width, height), dtype=int)

        # We may want to keep track of the overall mass of the sand pile
        # overtime.  The following array will store the masses at each time
        # step (so that `len(self.mass_history)` is equal to the number of time
        # steps the sand pile has been running).
        self.mass_history = []
        # You probably will want to define other attributes to store statistics.

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
        raise NotImplementedError()

    def mass(self):
        """Return the mass of the grid."""
        raise NotImplementedError()

    def topple(self, site):
        """Topple the specified site."""
        raise NotImplementedError()

    def avalanche(self, start):
        """Run the avalanche causing all sites to topple and store the stats of
        the avalanche in the appropriate variables.

        """
        raise NotImplementedError()

    # You are free (and encouraged) to define more methods within this class

