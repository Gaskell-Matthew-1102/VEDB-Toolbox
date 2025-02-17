# All code in this file is our own work.
from constants import MIN_SACCADE_AMP, MIN_SACCADE_DUR_MS, MIN_FIXATION_DUR_MS
from enum import Enum

class Event:
    class Sample_Type(Enum):
        FIXATION = 1
        GAP = 2
    
    def __init__(self, type:str, start_time, end_time):
        self.type = type
        self.start_time = start_time
        self.end_time = end_time
    
def classify_event(relative_gaze_velocity, threshold):
    if relative_gaze_velocity < threshold:
        return Event.Sample_Type.FIXATION
    else:
        return Event.Sample_Type.GAP
