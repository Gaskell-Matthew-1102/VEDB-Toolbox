from fixation.fixation_packages.event_list import EventList
from fixation.fixation_packages.event import Event
import numpy as np
import pytest

@pytest.fixture
def setup():
    event1 = Event(Event.Sample_Type.FIXATION, 0, 0.5, [0, 0], [1, 1])
    event2 = Event(Event.Sample_Type.FIXATION, 0.5, 1.0, [0, 0], [2, 2])
    event3 = Event(Event.Sample_Type.GAP, 1, 1.5, [0, 0], [1, 1])
    event4 = Event(Event.Sample_Type.GAP, 1.5, 2.0, [0, 0], [1, 1])
    event5 = Event(Event.Sample_Type.FIXATION, 2.0, 2.5, [0, 0], [1, 1])
    obj = EventList(np.array([event1, event2, event3, event4, event5]))
    yield obj

class TestEventList:
    def test_eventlist_constructor(self, setup):
        assert setup.list.size == 5

    def test_eventlist_summary(self, setup):
        assert setup.return_list_summary() == (3, 2)
    
    def test_eventlist_merge(self, setup):
        merged_list = setup.return_merge_event_list(setup.list[0], setup.list[1])
        assert merged_list[0].type == Event.Sample_Type.FIXATION
        assert merged_list[0].start_time_s == 0
        assert merged_list[0].end_time_s == 1.0
        assert np.array_equal(merged_list[0].start_pos, np.array([0,0]))
        assert np.array_equal(merged_list[0].end_pos, np.array([2,2]))

    def test_eventlist_consolidate(self, setup):
        ex_event1 = Event(Event.Sample_Type.FIXATION, 0, 1, [0, 0], [2, 2])
        ex_event2 = Event(Event.Sample_Type.GAP, 1, 2.0, [0, 0], [1, 1])
        ex_event3 = Event(Event.Sample_Type.FIXATION, 2.0, 2.5, [0, 0], [1, 1])
        
        expected_list = EventList(np.array([ex_event1, ex_event2, ex_event3]))
        setup.consolidate_list()
        assert expected_list == setup

    def test_eventList_microsaccade_filter(self):
        X = 0
        Y = 1
        event1 = Event(Event.Sample_Type.FIXATION, 0, 1, [X, X], [X, Y])
        event2 = Event(Event.Sample_Type.GAP, 1, 1.009, [0, 0], [0, 1])
        event3 = Event(Event.Sample_Type.FIXATION, 1.009, 2.5, [Y, X], [Y, Y])
        obj = EventList(np.array([event1, event2, event3]))
        obj.apply_filter(Event.microsaccade_filter, min_saccade_amp_deg=1.0, min_saccade_dur_ms=10, width_of_image_px=192, hfov=110)

        ex_event1 = Event(Event.Sample_Type.FIXATION, 0, 2.5, [X, X], [Y, Y])
        test_list = EventList(np.array([ex_event1]))

        assert obj == test_list

    def test_eventList_microsaccade_filter_beginning(self):
        X = 0
        Y = 1
        event2 = Event(Event.Sample_Type.GAP, 1, 1.009, [0, 0], [0, 1])
        event3 = Event(Event.Sample_Type.FIXATION, 1.009, 2.5, [Y, X], [Y, Y])
        obj = EventList(np.array([event2, event3]))
        obj.apply_filter(Event.microsaccade_filter, min_saccade_amp_deg=1.0, min_saccade_dur_ms=10, width_of_image_px=192, hfov=110)

        ex_event1 = Event(Event.Sample_Type.FIXATION, 1.009, 2.5, [Y, X], [Y, Y])
        test_list = EventList(np.array([ex_event1]))

        assert obj == test_list

    def test_eventList_microsaccade_filter_end(self):
        X = 0
        Y = 1
        event1 = Event(Event.Sample_Type.FIXATION, 0, 1, [X, X], [X, Y])
        event2 = Event(Event.Sample_Type.GAP, 1, 1.009, [0, 0], [0, 1])
        obj = EventList(np.array([event1, event2]))
        obj.apply_filter(Event.microsaccade_filter, min_saccade_amp_deg=1.0, min_saccade_dur_ms=10, width_of_image_px=192, hfov=110)

        ex_event1 = Event(Event.Sample_Type.FIXATION, 0, 1, [X, X], [X, Y])
        test_list = EventList(np.array([ex_event1]))

        assert obj == test_list

    def test_eventList_microsaccade_filter_large(self):
        X = 0
        Y = 1
        event1 = Event(Event.Sample_Type.GAP, 0, 0.009, [0, 0], [0, 1])
        event2 = Event(Event.Sample_Type.FIXATION, 0.009, 1, [X, X], [X, Y])
        event3 = Event(Event.Sample_Type.GAP, 1, 1.009, [0, 0], [0, 1])
        event4 = Event(Event.Sample_Type.FIXATION, 1.009, 1.5, [Y, X], [Y, Y])
        event5 = Event(Event.Sample_Type.GAP, 1.5, 1.505, [0, 0], [500, 100])
        event6 = Event(Event.Sample_Type.FIXATION, 1.5005, 2, [X, X], [X, Y])
        event7 = Event(Event.Sample_Type.GAP, 2, 2.009, [0, 0], [0, 1])
        obj = EventList(np.array([event1, event2, event3, event4, event5, event6, event7]))

        ex_ev1 = Event(Event.Sample_Type.FIXATION, 0.009, 1.5, [X, X], [Y, Y])
        ex_ev2 = Event(Event.Sample_Type.GAP, 1.5, 1.505, [0, 0], [500, 100])
        ex_ev3 = Event(Event.Sample_Type.FIXATION, 1.5005, 2, [X, X], [X, Y])
        test = EventList(np.array([ex_ev1, ex_ev2, ex_ev3]))

        obj.apply_filter(Event.microsaccade_filter, min_saccade_amp_deg=1.0, min_saccade_dur_ms=10, width_of_image_px=192, hfov=110)

        assert obj == test

    def test_short_fixation_filter(self):
        X = 0
        Y = 1
        event1 = Event(Event.Sample_Type.GAP, 0, 1, [X, X], [X, Y])
        event2 = Event(Event.Sample_Type.FIXATION, 1, 1.009, [0, 0], [1, 1])
        event3 = Event(Event.Sample_Type.GAP, 1.009, 2.5, [Y, X], [Y, Y])
        obj = EventList(np.array([event1, event2, event3]))
        obj.apply_filter(Event.short_fixation_filter, min_fixation_dur_ms=70)

        ex_event1 = Event(Event.Sample_Type.GAP, 0, 2.5, [X, X], [Y, Y])
        test_list = EventList(np.array([ex_event1]))

        assert obj == test_list

    def test_eventList_short_fixation_filter_beginning(self):
        X = 0
        Y = 1
        event2 = Event(Event.Sample_Type.FIXATION, 1, 1.009, [0, 0], [100, 1])
        event3 = Event(Event.Sample_Type.GAP, 1.009, 2.5, [Y, X], [Y, Y])
        obj = EventList(np.array([event2, event3]))
        obj.apply_filter(Event.short_fixation_filter, min_fixation_dur_ms=70)

        ex_event1 = Event(Event.Sample_Type.GAP, 1.009, 2.5, [Y, X], [Y, Y])
        test_list = EventList(np.array([ex_event1]))

        assert obj == test_list

    def test_eventList_short_fixation_filter_end(self):
        X = 0
        Y = 1
        event1 = Event(Event.Sample_Type.GAP, 0, 1, [X, X], [X, Y])
        event2 = Event(Event.Sample_Type.FIXATION, 1, 1.009, [0, 0], [100, 1])
        obj = EventList(np.array([event1, event2]))
        obj.apply_filter(Event.short_fixation_filter, min_fixation_dur_ms=70)

        ex_event1 = Event(Event.Sample_Type.GAP, 0, 1, [X, X], [X, Y])
        test_list = EventList(np.array([ex_event1]))

        assert obj == test_list

    def test_eventList_short_fixation_filter_large(self):
        X = 0
        Y = 1
        event1 = Event(Event.Sample_Type.FIXATION, 0, 0.009, [0, 0], [100, 1])
        event2 = Event(Event.Sample_Type.GAP, 0.009, 1, [X, X], [X, Y])
        event3 = Event(Event.Sample_Type.FIXATION, 1, 1.009, [0, 0], [100, 1])
        event4 = Event(Event.Sample_Type.GAP, 1.009, 1.5, [Y, X], [Y, Y])
        event5 = Event(Event.Sample_Type.FIXATION, 1.5, 1.8, [0, 0], [1, 1])
        event6 = Event(Event.Sample_Type.GAP, 1.5005, 2, [X, X], [X, Y])
        event7 = Event(Event.Sample_Type.FIXATION, 2, 2.009, [0, 0], [100, 1])
        obj = EventList(np.array([event1, event2, event3, event4, event5, event6, event7]))


        ex_ev1 = Event(Event.Sample_Type.GAP, 0.009, 1.5, [X, X], [Y, Y])
        ex_ev2 = Event(Event.Sample_Type.FIXATION, 1.5, 1.8, [0, 0], [1, 1])
        ex_ev3 = Event(Event.Sample_Type.GAP, 1.5005, 2, [X, X], [X, Y])
        test = EventList(np.array([ex_ev1, ex_ev2, ex_ev3]))

        obj.apply_filter(Event.short_fixation_filter, min_fixation_dur_ms=70)

        assert obj == test

    def test_eventList_all_filters(self):
        X = 0
        Y = 1
        event1 = Event(Event.Sample_Type.FIXATION, 0, 0.009, [0, 0], [100, 1])
        event2 = Event(Event.Sample_Type.GAP, 0.009, 1, [X, X], [X, Y])
        event3 = Event(Event.Sample_Type.FIXATION, 1, 1.009, [0, 0], [100, 1])
        event4 = Event(Event.Sample_Type.GAP, 1.009, 1.5, [Y, X], [Y, Y])
        event5 = Event(Event.Sample_Type.FIXATION, 1.5, 1.55, [0, 0], [1, 1])
        event6 = Event(Event.Sample_Type.GAP, 1.5005, 2, [X, X], [X, Y])
        event7 = Event(Event.Sample_Type.FIXATION, 2, 2.009, [0, 0], [100, 1])
        obj = EventList(np.array([event1, event2, event3, event4, event5, event6, event7]))


        ex_ev1 = Event(Event.Sample_Type.GAP, 0.009, 2, [X, X], [X, Y])
        test = EventList(np.array([ex_ev1]))

        obj.apply_filter(Event.microsaccade_filter, min_saccade_amp_deg=1.0, min_saccade_dur_ms=10, width_of_image_px=192, hfov=110)
        obj.apply_filter(Event.short_fixation_filter, min_fixation_dur_ms=70)

        assert obj == test

    # def test_eventList_iter(setup):
    #     for event in setup.obj: