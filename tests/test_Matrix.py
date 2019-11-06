import unittest

from inkscape_helper.Matrix import Matrix

class TestMatrix(unittest.TestCase):
    mtx = Matrix([[1,2,3],[4,5,6],[7,8,9]])
    def test_repr(self):
        self.assertEqual(str(self.mtx), '[\n[1, 2, 3],\n[4, 5, 6],\n[7, 8, 9]\n]')

    def test_minor(self):
        self.assertEqual(str(self.mtx.minor(1, 1)), '[\n[1, 3],\n[7, 9]\n]')

    def test_determinant(self):
        self.assertEqual(self.mtx.det(), 0)
        self.assertEqual(self.mtx.minor(2, 2).det(), -3)
