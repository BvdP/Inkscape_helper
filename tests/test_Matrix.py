import unittest

from inkscape_helper.Matrix import Matrix

class TestMatrix(unittest.TestCase):
    mtx = Matrix([[1,2,3],[4,5,6],[7,8,9]])
    def test_repr(self):
        self.assertEqual(str(self.mtx), '[\n[1, 2, 3],\n[4, 5, 6],\n[7, 8, 9]\n]')

    def test_eq(self):
        self.assertEqual(self.mtx, self.mtx)

    def test_minor(self):
        self.assertEqual(str(self.mtx.minor(1, 1)), '[\n[1, 3],\n[7, 9]\n]')

    def test_determinant(self):
        self.assertEqual(self.mtx.det, 0)
        self.assertEqual(self.mtx.minor(2, 2).det, -3)

    def test_determinant_1x1(self):
        m = Matrix([[3]])
        self.assertEqual(m.det, 3)

    def test_determinant_wrong_size(self):
        m = Matrix([[1, 2]])
        with self.assertRaises(TypeError):
            m.det

    def test_add(self):
        self.assertEqual(self.mtx + self.mtx, Matrix([[2,4,6],[8,10,12],[14,16,18]]))

    def test_add_size_mismatch(self):
        m = Matrix([[1, 2]])
        with self.assertRaises(TypeError):
            m + self.mtx