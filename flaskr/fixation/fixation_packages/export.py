import json
import numpy as np
from fixation_packages.event_list import EventList
from fixation_packages.event import Event

def create_timestamp_list(in_eventList: EventList) -> np.array:
    out = []

    for event in in_eventList:
        if event.type == Event.Sample_Type.FIXATION:
            guh = (event.start_time_ms, event.end_time_ms)
            print(type(guh))
            out.append(guh)
    print(out)
    print(len(out))
    return np.array(out)

def create_json(list: np.array) -> json:
    ret = json.dumps(list)
    return ret

def write_str_to_file(json: json, export_filename: str) -> None:
    with open(export_filename, "w") as f:
        f.write(json)