import pytest
from fixation.fixation_packages.event import Event
from fixation.fixation_packages.event_list import EventList
from fixation.fixation_packages.export import create_timestamp_list, create_json, write_json_to_file
import numpy as np
import json

@pytest.fixture
def setup():
    event1 = Event(Event.Sample_Type.FIXATION, 0, 1, [0, 0], [1, 1])
    event2 = Event(Event.Sample_Type.GAP, 1, 2.0, [0, 0], [1, 1])
    event3 = Event(Event.Sample_Type.FIXATION, 2.0, 2.5, [0, 0], [1, 1])
    obj = EventList(np.array([event1, event2, event3]))
    yield obj

class TestExport:
    def test_generate_timestamp_list(self, setup):
        out_list = create_timestamp_list(setup)
        agh = np.array([(np.float64(0), np.float64(1)), (np.float64(2.0), np.float64(2.5))])
        assert (out_list==agh).all()

    def test_generate_json_valid(self):
        test = "[[0.0, 1.0], [2.0, 2.5]]"
        out = create_json(np.array([[0, 1], [2.0, 2.5]]))
        # write_json_to_file(out, "export.json")
        assert test == out

    def test_generate_json_no_input(self):
        test = "[]"
        out = create_json(np.array([]))
        assert test == out

        
