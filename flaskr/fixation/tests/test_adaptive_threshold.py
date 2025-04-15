import pytest
# import fixation_packages.adaptive_threshold
import fixation.fixation_packages.adaptive_threshold as adaptive_threshold
import numpy as np

class TestAdaptiveThreshold:
    def test_gaze_velocity_correction_valid(self):
        gaze_vec = np.array([[6, 5], [3, 2], [2, 1], [5, 1], [1, 7], [-1, -6]])
        flow_vec = np.array([[2, -5], [7, 0], [2, 0], [2, -2], [1, 1], [10, 2]])
        out_arr, status_code = adaptive_threshold.gaze_velocity_correction(gaze_vec, flow_vec)
        # test = np.array([[4, -4, 0, 3, 0, -11], [10, 2, 1, 3, 6, -8]])
        test = np.array([[4, 10], [-4, 2], [0, 1], [3, 3], [0, 6], [-11, -8]])
        assert np.array_equal(out_arr, test)
        assert status_code == 0

    # def test_gaze_velocity_correction_empty(self):
    #     pass
    
    def test_gaze_velocity_correction_size_mismatch(self):
        gaze_vec = np.array([[6, 5], [3, 2], [2, 1], [5, 1], [1, 7], [-1, -6]])
        flow_vec = np.array([[2, -5], [7, 0], [2, 0], [2, -2]])

        # Current assumption is that we will shrink the longer array to match the size of the shorter array, then subtract
        out_arr, status_code = adaptive_threshold.gaze_velocity_correction(gaze_vec, flow_vec)
        test = np.array([[4, 10], [-4, 2], [0, 1], [3, 3]])
        assert np.array_equal(out_arr, test)
        assert status_code == 1
