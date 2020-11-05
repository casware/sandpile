import unittest
import numpy as np
from sandpile import SandPile
from cylindrical import CylindricalSandPile
from hourglass import HourGlassSandPile
from sandpilenumba import SandPile as NSP

class TestSandPile(unittest.TestCase):
    def test_get_neighbors(self):
        pile = SandPile(50, 40)
        self.assertEqual(pile.get_neighbors([0, 0]), [[1, 0], [0, 1]])
        self.assertEqual(pile.get_neighbors([0, 39]), [[1, 39], [0, 38]])
        self.assertEqual(pile.get_neighbors([25, 24]), [
                         [24, 24], [26, 24], [25, 23], [25, 25]])

    def test_mass(self):
        pile = SandPile(8, 8)
        pile.grid[0, 0] = 3
        pile.grid[4, 5] = 2
        pile.grid[1, 4] = 2
        self.assertEqual(pile.mass(), 7)

    def test_topple(self):
        """ Test a single topple (not a complete avalanche)
        """
        pile = SandPile(4, 4)
        # Start with
        # [[4, 2, 0,0],
        # [3,0,0,0],
        # [0,0,0,0],
        # [0,0,0,0]]

        # Topple should give
        # [[1, 3, 0,0],
        # [0,1,0,0],
        # [1,0,0,0],
        # [0,0,0,0]]
        expected = [[0, 3, 0, 0],
                    [4, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0]]
        pile.grid[0, 0] = 4
        pile.grid[1, 0] = 3
        pile.grid[0, 1] = 2
        pile.topple([0, 0])

        self.assertEqual((pile.grid == expected).all(), True)

    def test_avalanche(self):
        """
        Make sure our avalanche is leaving us in a stable state.
        """
        pile = SandPile(4, 4)
        # Start with
        # [[3, 2, 0,0],
        # [3,0,0,0],
        # [0,0,0,0],
        # [0,0,0,0]]

        # Topple should give
        # [[1, 3, 0,0],
        # [0,1,0,0],
        # [1,0,0,0],
        # [0,0,0,0]]
        pile.grid[0, 0] = 3
        pile.grid[1, 0] = 3
        pile.grid[0, 1] = 2
        pile.drop_sand(1, (0,0))
        print(pile.topples_history)
        print(pile.grid)

        # Make sure the stats are collected properly
        self.assertEqual((pile.area_history == [5]), True)
        self.assertEqual((pile.length_history == [2]), True)
        self.assertEqual((pile.topples_history == [2]), True)
        self.assertEqual((pile.mass() == 6), True)

        pile = SandPile(100, 100, random=True)
        pile.simulate(100, site=(50,50))
        self.assertEqual((np.max(pile.grid) < 4), True)

    def test_cylinder_topple(self):
        pile = CylindricalSandPile(4, 4)
        # Start with
        # [[4, 2, 0,0],
        # [3,0,0,0],
        # [0,0,0,0],
        # [0,0,0,0]]

        # Topple should give
        # [[0, 3, 0,0],
        # [4,0,0,0],
        # [0,0,0,0],
        # [1,0,0,0]]
        # Note that the indices of the python array are the transpose
        # of what we would expect
        expected = [[0, 3, 0, 0],
                    [4, 0, 0, 0],
                    [0, 0, 0, 0],
                    [1, 0, 0, 0]]
        pile.grid[0, 0] = 4
        pile.grid[1, 0] = 3
        pile.grid[0, 1] = 2
        pile.topple([0, 0])
        self.assertEqual((pile.grid == expected).all(), True)

    def test_cylinder_distance(self):
        pile = CylindricalSandPile(4, 4)
        self.assertEqual((pile.dist([3, 0], [0, 0]) == 1), True)

        pile2 = CylindricalSandPile(20,20)
        self.assertEqual((pile2.dist([0,0], [18,0]) == 2), True)

    def test_hourglass_distance(self):
        pile = HourGlassSandPile(6, 6)
        self.assertEqual((pile.dist([3, 0], [0, 0]) == 3), True)
        self.assertEqual((pile.dist([5, 0], [0, 0]) == 1), True)
        self.assertEqual((pile.dist([0, 0], [5, 4]) == 3), True)

    def test_sandpile_numba(self):
        pile = NSP(4,4)
        start = [[3, 3, 3, 0],
                 [3, 3, 0, 0],
                 [1, 0, 0, 0],
                 [0, 0, 0, 0]]
        expected = [[2, 2, 0, 1],
                    [1, 1, 2, 0],
                    [2, 1, 0, 0],
                    [0, 0, 0, 0]]
        pile.grid=np.array(start)
        pile.simulate(1, site=(0,0))
        self.assertEqual((pile.grid == expected).all(), True)
        #self.assertEqual((pile.area_history == [9]), True)

if __name__ == '__main__':
    unittest.main()
