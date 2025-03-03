import pytest
import fixation_packages.adaptive_threshold
import numpy as np

class TestAdaptiveThreshold:
    def test_gaze_velocity_correction_valid(self):
        gaze_vec = np.array([[6, 3, 2, 5, 1, -1], [5, 2, 1, 1, 7, -6]])
        flow_vec = np.array([[2, 7, 2, 2, 1, 10], [-5, 0, 0, -2, 1, 2]])
        out = fixation_packages.adaptive_threshold.gaze_velocity_correction(gaze_vec, flow_vec)
        test = np.array([[4, -4, 0, 3, 0, -11], [10, 2, 1, 3, 6, -8]])
        assert np.array_equal(out[0], test)
        assert out[1] == 0

    # def test_gaze_velocity_correction_empty(self):
    #     pass
    
    def test_gaze_velocity_correction_size_mismatch(self):
        gaze_vec = np.array([[6, 3, 2], [5, 2, 1]])
        flow_vec = np.array([[2, 7, 2, 2], [-5, 0, 0, -2]])

        # Current assumption is that we will shrink the longer array to match the size of the shorter array, then subtract
        out = fixation_packages.adaptive_threshold.gaze_velocity_correction(gaze_vec, flow_vec)
        test = np.array([[4, -4, 0], [10, 2, 1]])
        assert np.array_equal(out[0], test)
        assert out[1] == 2
