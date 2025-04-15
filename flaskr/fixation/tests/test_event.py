import pytest
import numpy as np
import math
from fixation.fixation_packages.event import Event
from fixation.fixation_packages.event import build_event
from fixation.fixation_packages.event import classify_event
from fixation.fixation_packages.adaptive_threshold import gaze_velocity_correction

from fixation.fixation_packages.adaptive_threshold import calculate_RMS_of_window

class TestEvent:
    def test_gaze_velocity_correction(self):
        gaze_vel = np.array([[6], [10]])
        global_optic_flow = np.array([[2], [4]])
        output = gaze_velocity_correction(gaze_vel, global_optic_flow)
        # Resulting vector is <4, 6>, magnitude is sqrt(52)
        assert np.array_equal(output[0], np.array([[4], [6]]))
        assert np.linalg.norm(output[0]) == math.sqrt(52)

    def test_RMS(self):
        vec1 = np.array([[1], [2]])
        vec2 = np.array([[6], [1]])
        vec3 = np.array([[3], [2]])
        output = calculate_RMS_of_window(np.array([vec1, vec2, vec3]), 0, 3)
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
        event = build_event(rel_gaze_vel, thresh, start_time, end_time, [0,0], [1,1])
        assert event.type == Event.Sample_Type.FIXATION

    def test_event_amplitude_calculation(self):
        event = Event(Event.Sample_Type.GAP, 1.0, 2.0, [0, 0], [1, 1])
        out = event.calculate_gap_amplitude(np.array([5, 1]), np.array([10, 2]), 192, 110)
        test = 4.338
        assert out - test < 0.001

    def test_event_amplitude_calculation_no_x_displacement(self):
        event = Event(Event.Sample_Type.GAP, 1.0, 2.0, [0, 0], [1, 1])
        out = event.calculate_gap_amplitude(np.array([5, 1]), np.array([5, 2]), 192, 110)
        test = 0.852
        assert out - test < 0.001

    def test_event_microsaccade_filter_is_microsaccade(self):
        event = Event(Event.Sample_Type.GAP, 1.000, 1.005, [0, 0], [0, 1])
        out = event.microsaccade_filter(1, 10, 192, 110)
        assert out == True

    def test_event_microsaccade_filter_isnt_microsaccade_angle(self):
        event = Event(Event.Sample_Type.GAP, 1.000, 1.005, [0, 0], [1, 1])
        out = event.microsaccade_filter(1, 10, 110, 92)
        assert out == False

    def test_event_microsaccade_filter_isnt_microsaccade_time(self):
        event = Event(Event.Sample_Type.GAP, 1.000, 2.000, [0, 0], [100, 1])
        out = event.microsaccade_filter(1, 10, 110, 92)
        assert out == False

    def test_event_microsaccade_filter_isnt_microsaccade_both(self):
        event = Event(Event.Sample_Type.GAP, 1.000, 2.0, [0, 0], [1, 1])
        out = event.microsaccade_filter(1, 10, 110, 92)
        assert out == False

    def test_event_short_fixation_pass(self):
        obj = Event(Event.Sample_Type.FIXATION, 0.05, 0.075, [0, 0], [1, 1])
        assert obj.short_fixation_filter(70) == True
    
    def test_event_short_fixation_fail(self):
        obj = Event(Event.Sample_Type.FIXATION, 0.05, 0.15, [0, 0], [1, 1])
        assert obj.short_fixation_filter(70) == False
        assert obj.type == Event.Sample_Type.FIXATION