import pytest
from fixation_packages.event import Event
from fixation_packages.event_list import EventList
from fixation_packages.export import create_timestamp_list, create_json, write_str_to_file
import numpy as np
import json

@pytest.fixture
def setup():
    event1 = Event(Event.Sample_Type.FIXATION, 0, 1)
    event2 = Event(Event.Sample_Type.GAP, 1, 2.0)
    event3 = Event(Event.Sample_Type.FIXATION, 2.0, 2.5)
    obj = EventList(np.array([event1, event2, event3]))
    yield obj

class TestExport:
    def test_generate_timestamp_list(self, setup):
        out_list = create_timestamp_list(setup)
        agh = np.array([(0, 1), (2.0, 2.5)])
        assert (out_list==agh).all()

    def test_generate_json_valid(self):
        test = "[[0.0, 1.0], [2.0, 2.5]]"
        out = create_json(np.array([(0, 1), (2.0, 2.5)]).tolist())
        write_str_to_file(out, "export.json")
        assert test == out

    def test_generate_json_no_input(setup):
        test = "[]"
        out = create_json(np.array([]).tolist())
        assert test == out
    # def test_generate_json_invalid_input(setup):
    #     test = "agsaphgsa]gh"
        
