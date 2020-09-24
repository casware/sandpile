import unittest
import numpy as np
from sandpile import SandPile


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
        pile.topple([0,0])

        self.assertEqual((pile.grid == expected).all(), True)


if __name__ == '__main__':
    unittest.main()
