import pytest
from fixation_packages.gaze_processing import *

class TestGazeProcessing:
    def test_calculate_gaze_velocity_valid(self):
        vec = np.array([[6, 2, 8], [2, 5, 2]])
        assert np.array_equal(calculateGazeVelocity(vec), np.array([[-4, 6], [3, -3]]))