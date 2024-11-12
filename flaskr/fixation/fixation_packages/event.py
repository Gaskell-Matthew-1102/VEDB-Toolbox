from constants import MIN_SACCADE_AMP, MIN_SACCADE_DUR_MS, MIN_FIXATION_DUR_MS

class Event:
    def __init__(self, type:str, start_time, end_time):
        self.type = type
        self.start_time = start_time
        self.end_time = end_time

