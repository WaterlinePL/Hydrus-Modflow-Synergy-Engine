import unittest
import numpy as np

import modflow.modflow_utils as utils

modflow_project = "simple1"
nam_file = "simple1.nam"


class ModflowUtilsTest(unittest.TestCase):

    def test_get_nam_file(self):
        self.assertEqual(utils.get_nam_file(modflow_project), nam_file)

    def test_get_model_data(self):
        self.assertEqual(utils.get_model_data(modflow_project, nam_file), {
            "rows": 10,
            "cols": 10,
            "row_cells": [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
            "col_cells": [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
            "grid_unit": "meters"
        })

    def test_scale_cells_size(self):
        row_cells = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100]
        col_cells = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100]

        r, c = utils.scale_cells_size(row_cells, col_cells, 100)
        self.assertListEqual(list(r), [10, 10, 10, 10, 10, 10, 10, 10, 10, 10])
        self.assertListEqual(list(c), [10, 10, 10, 10, 10, 10, 10, 10, 10, 10])

    def test_validate_model(self):
        self.assertTrue(utils.validate_model(modflow_project, nam_file))
        self.assertFalse(utils.validate_model("", nam_file))

    @staticmethod
    def test_get_shapes_from_rch():
        results = utils.get_shapes_from_rch(modflow_project, nam_file, (10, 10))
        np.testing.assert_array_equal(results[0], np.array([
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]))

        np.testing.assert_array_equal(results[1], np.array([
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        ]))

        np.testing.assert_array_equal(results[2], np.array([
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
        ]))


if __name__ == '__main__':
    unittest.main()
