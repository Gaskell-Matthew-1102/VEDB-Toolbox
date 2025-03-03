import pytest
import numpy as np
import math
from fixation_packages.event import Event
from fixation_packages.event import classify_event
from fixation_packages.adaptive_threshold import gaze_velocity_correction

from fixation_packages.adaptive_threshold import calculate_RMS_of_window

class TestEvent:
    def test_gaze_velocity_correction(self):
        gaze_vel = np.array([[6], [10]])
        global_optic_flow = np.array([[2], [4]])
        output = gaze_velocity_correction(gaze_vel, global_optic_flow)
        # Resulting vector is <4, 6>, magnitude is sqrt(52)
<<<<<<< HEAD
        assert np.array_equal(output[0], np.array([[4], [6]]))
=======
        assert (output == np.array([[4], [6]])).all()
>>>>>>> 131ef9622d49d62b80bbd1ec54cecae1402c1f4a
        assert np.linalg.norm(output) == math.sqrt(52)

    def test_RMS(self):
        vec1 = np.array([[1], [2]])
        vec2 = np.array([[6], [1]])
        vec3 = np.array([[3], [2]])
        output = calculate_RMS_of_window([vec1, vec2, vec3], 0, 3)
        assert output == math.sqrt(55/3)


    def test_event_classification_fixation(self):
        rel_gaze_vel = 4.0
        thresh = 5.0
        output = classify_event(rel_gaze_vel, thresh)
        assert output == Event.Sample_Type.FIXATION

    def test_event_classification_gap(self):
        rel_gaze_vel = 4.0
        thresh = 3.0
        output = classify_event(rel_gaze_vel, thresh)
        assert output == Event.Sample_Type.GAP

    def test_event_classification_border(self):
        rel_gaze_vel = 4.0
        thresh = 4.0
        output = classify_event(rel_gaze_vel, thresh)
        assert output == Event.Sample_Type.GAP

    def test_build_event_fixation(self):
        rel_gaze_vel = 4.0
        thresh = 5.0
        start_time = 0.0
        end_time = 0.5
        event = Event.build_event(rel_gaze_vel, thresh, start_time, end_time)
        assert event.type == Event.Sample_Type.FIXATION

    def test_event_amplitude_calculation(self):
        # assert False
        ...

    def test_event_microsaccade_filter(self):
        # assert False
        ...

    def test_event_short_fixation_pass(self):
        obj = Event(Event.Sample_Type.FIXATION, 50, 75)
        assert obj.short_fixation_filter() == True
        assert obj.type == Event.Sample_Type.GAP
    
    def test_event_short_fixation_fail(self):
        obj = Event(Event.Sample_Type.FIXATION, 50, 150)
        assert obj.short_fixation_filter() == False
        assert obj.type == Event.Sample_Type.FIXATION