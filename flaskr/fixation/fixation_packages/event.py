# All code in this file is our own work.
from constants import MIN_SACCADE_AMP, MIN_SACCADE_DUR_MS, MIN_FIXATION_DUR_MS
from enum import Enum

class Event:
    class Sample_Type(Enum):
        FIXATION = 1
        GAP = 2
        UNDEFINED = 3     # this is used in steps 8.1 and 8.2, as I don't know what happens to "removed" events
    
    def __init__(self, type:Sample_Type, start_time_ms:float, end_time_ms:float):
        self.type = type
        self.start_time_ms = start_time_ms
        self.end_time_ms = end_time_ms

    def build_event(relative_gaze_velocity:float, threshold:float, start_time_ms:float, end_time_ms:float):
        return Event(classify_event(relative_gaze_velocity, threshold), start_time_ms, end_time_ms)
    
def classify_event(relative_gaze_velocity, threshold):
    if relative_gaze_velocity < threshold:
        return Event.Sample_Type.FIXATION
    else:
        return Event.Sample_Type.GAP
