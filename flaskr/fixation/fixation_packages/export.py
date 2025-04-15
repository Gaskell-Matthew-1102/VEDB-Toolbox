import json
import numpy as np
from .event_list import EventList
# from fixation_packages.event_list import EventList
from .event import Event
# from fixation_packages.event import Event

def create_timestamp_list(in_eventList: EventList) -> np.array:
    out = []

    for event in in_eventList:
        if event.type == Event.Sample_Type.FIXATION:
            guh = (event.start_time_s, event.end_time_s)
            out.append(guh)
    return np.array(out)

def create_json(list: np.array) -> json:
    ret = json.dumps(list.tolist())
    return ret

def write_json_to_file(json: json, export_filename: str) -> None:
    with open(export_filename, "w") as f:
        f.write(json)

def write_constants_to_file(constants:list[tuple[str, any]], export_filename: str) -> None:
    with open(export_filename, "w") as f:
        for arg_pair in constants:
            f.write(f"{arg_pair[0]}: {arg_pair[1]}")
            f.write('\n')