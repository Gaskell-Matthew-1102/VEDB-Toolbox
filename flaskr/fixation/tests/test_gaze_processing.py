import pytest
from fixation.fixation_packages.gaze_processing import *

class TestGazeProcessing:
    def test_calculate_gaze_velocity_valid(self):
        vec = np.array([6, 2, 8])
        timestamps = np.array([0.1, 0.2, 0.3])
        test = np.array([-40., 60.])

        output = calculateGazeVelocity(vec, timestamps)

        assert np.allclose(output, test)