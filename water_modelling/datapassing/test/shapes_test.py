import unittest
from typing import List

import numpy as np
from numpy import ndarray

from datapassing.hydrus_modflow_passing import HydrusModflowPassing
from datapassing.shape_data import ShapeMetadata, Shape


# FIXME
class HydrusShapesTest(unittest.TestCase):

    @staticmethod
    def test_four_shapes():
        shapes_metadata: List[ShapeMetadata] = HydrusShapesTest.create_shape_files()
        sample_hydrus_output = ["hydrus_out/" + base_name for base_name in
                                ["t_level1.out", "t_level2.out", "t_level3.out", "t_level4.out"]]

        shapes = [Shape(metadata.shape_mask, t_level_file)
                  for (metadata, t_level_file) in zip(shapes_metadata, sample_hydrus_output)]

        expected0 = np.array([[0.00102814, 0.00102814, 0.00102814, 0.00102814, 0.00102814, 0., 0., 0., 0., 0.],
                              [0.00102814, 0.00102814, 0.00102814, 0.00102814, 0.00102814, 0., 0., 0., 0., 0.],
                              [0.00102814, 0.00102814, 0.00102814, 0.00102814, 0.00102814, 0., 0., 0., 0., 0.],
                              [0.00102814, 0.00102814, 0.00102814, 0.00102814, 0.00102814, 0., 0., 0., 0., 0.],
                              [0.00102814, 0.00102814, 0.00102814, 0.00102814, 0.00102814, 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]])

        expected1 = np.array([[0.00077233335, 0.00077233335, 0.00077233335, 0.00077233335, 0.00077233335, 0.001, 0.001,
                               0.001, 0.001, 0.001],
                              [0.00077233335, 0.00077233335, 0.00077233335, 0.00077233335, 0.00077233335, 0.001, 0.001,
                               0.001, 0.001, 0.001],
                              [0.00077233335, 0.00077233335, 0.00077233335, 0.00077233335, 0.00077233335, 0.0012, 0.001,
                               0.001, 0.001, 0.001],
                              [0.00077233335, 0.00077233335, 0.00077233335, 0.00077233335, 0.00077233335, 0.0012, 0.001,
                               0.001, 0.001, 0.001],
                              [0.00077233335, 0.00077233335, 0.00077233335, 0.00077233335, 0.00077233335, 0.0012, 0.001,
                               0.001, 0.001, 0.001],
                              [0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001],
                              [0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001],
                              [0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001],
                              [0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001],
                              [0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]])

        expected2 = np.array(
            [[0.000577, 0.000577, 0.000577, 0.000577, 0.000577, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020],
             [0.000577, 0.000577, 0.000577, 0.000577, 0.000577, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020],
             [0.000577, 0.000577, 0.000577, 0.000577, 0.000577, 0.0012, 0.00020, 0.00020, 0.00020, 0.00020],
             [0.000577, 0.000577, 0.000577, 0.000577, 0.000577, 0.0012, 0.00020, 0.00020, 0.00020, 0.00020],
             [0.000577, 0.000577, 0.000577, 0.000577, 0.000577, 0.0012, 0.00020, 0.00020, 0.00020, 0.00020],
             [0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020],
             [0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020],
             [0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020],
             [0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020],
             [0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020, 0.00020]])

        expected3 = np.array(
            [[0.00038567, 0.00038567, 0.00038567, 0.00038567, 0.00038567, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030],
             [0.00038567, 0.00038567, 0.00038567, 0.00038567, 0.00038567, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030],
             [0.00038567, 0.00038567, 0.00038567, 0.00038567, 0.00038567, 0.0012, 0.00030, 0.00030, 0.00030, 0.00030],
             [0.00038567, 0.00038567, 0.00038567, 0.00038567, 0.00038567, 0.0012, 0.00030, 0.00030, 0.00030, 0.00030],
             [0.00038567, 0.00038567, 0.00038567, 0.00038567, 0.00038567, 0.0012, 0.00030, 0.00030, 0.00030, 0.00030],
             [0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030],
             [0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030],
             [0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030],
             [0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030],
             [0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030, 0.00030]])

        result = HydrusModflowPassing("./simple1", "simple1.nam", shapes)
        np.testing.assert_array_almost_equal(result.update_rch(spin_up=105).array[0][0], expected0)
        np.testing.assert_array_almost_equal(result.update_rch(spin_up=105).array[1][0], expected1)
        np.testing.assert_array_almost_equal(result.update_rch(spin_up=105).array[2][0], expected2)
        np.testing.assert_array_almost_equal(result.update_rch(spin_up=105).array[3][0], expected3)

    @staticmethod
    def test_bad_hydrus_length():
        shapes_metadata: List[ShapeMetadata] = HydrusShapesTest.create_shape_files()
        sample_hydrus_output = ["hydrus_out/" + base_name for base_name in
                                ["t_level5.out", "t_level5.out", "t_level3.out", "t_level4.out"]]

        shapes = [Shape(metadata.shape_mask, t_level_file)
                  for (metadata, t_level_file) in zip(shapes_metadata, sample_hydrus_output)]

        result = HydrusModflowPassing("./simple1", "simple1.nam", shapes)
        np.testing.assert_raises(ValueError, result.update_rch, 105)
        np.testing.assert_raises(ValueError, result.update_rch, 0)

    @staticmethod
    def create_shape_files() -> List[ShapeMetadata]:
        return [ShapeMetadata(HydrusShapesTest.create_shape1()),
                ShapeMetadata(HydrusShapesTest.create_shape2()),
                ShapeMetadata(HydrusShapesTest.create_shape3()),
                ShapeMetadata(HydrusShapesTest.create_shape4())]

    @staticmethod
    def create_shape1() -> ndarray:
        return np.array([[1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                         [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

    @staticmethod
    def create_shape2() -> ndarray:
        return np.array([[0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
                         [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
                         [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
                         [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

    @staticmethod
    def create_shape3() -> ndarray:
        return np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
                         [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

    @staticmethod
    def create_shape4() -> ndarray:
        return np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                         [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                         [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])


if __name__ == '__main__':
    unittest.main()
