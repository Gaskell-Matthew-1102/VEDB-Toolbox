from fixation_packages.event_list import EventList
from fixation_packages.event import Event
import numpy as np
import pytest

@pytest.fixture
def setup():
    event1 = Event(Event.Sample_Type.FIXATION, 0, 0.5)
    event2 = Event(Event.Sample_Type.FIXATION, 0.5, 1.0)
    event3 = Event(Event.Sample_Type.GAP, 1, 1.5)
    event4 = Event(Event.Sample_Type.GAP, 1.5, 2.0)
    event5 = Event(Event.Sample_Type.FIXATION, 2.0, 2.5)
    obj = EventList(np.array([event1, event2, event3, event4, event5]))
    yield obj

class TestEventList:
    def test_eventlist_constructor(self, setup):
        assert setup.list.size == 5

    def test_eventlist_summary(self, setup):
        assert setup.return_list_summary() == (3, 2)
    
    def test_eventlist_merge(self, setup):
        merged_list = setup.return_merge_event_list(0, 1)
        assert merged_list[0].type == Event.Sample_Type.FIXATION
        assert merged_list[0].start_time_ms == 0
        assert merged_list[0].end_time_ms == 1.0

    def test_eventlist_consolidate(self, setup):
        ex_event1 = Event(Event.Sample_Type.FIXATION, 0, 1)
        ex_event2 = Event(Event.Sample_Type.GAP, 1, 2.0)
        ex_event3 = Event(Event.Sample_Type.FIXATION, 2.0, 2.5)
        
        expected_list = EventList(np.array([ex_event1, ex_event2, ex_event3]))
        setup.consolidate_list()
        assert expected_list == setup

    # def test_eventList_iter(setup):
    #     for event in setup.obj:

