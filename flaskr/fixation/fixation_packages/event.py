# All code in this file is our own work.
from constants import MIN_SACCADE_AMP, MIN_SACCADE_DUR_MS, MIN_FIXATION_DUR_MS
from enum import Enum
import numpy as np
import math

class Event:
    class Sample_Type(Enum):
        FIXATION = 1
        GAP = 2
    
    def __init__(self, type:Sample_Type, start_time_ms:float, end_time_ms:float):
        self.type = type
        self.start_time_ms = start_time_ms
        self.end_time_ms = end_time_ms

    def build_event(relative_gaze_velocity:float, threshold:float, start_time_ms:float, end_time_ms:float):
        return Event(classify_event(relative_gaze_velocity, threshold), start_time_ms, end_time_ms)
    
    def calculate_gap_amplitude(self, start_pix:np.ndarray[2], end_pix:np.ndarray[2]):
        pixel_difference_length = np.linalg.norm(end_pix-start_pix)
        angle = self.__black_box_pixels_to_angle(pixel_difference_length)
        return angle

    # CHECK ACCURACY. this equation assumes the start point is the center. lenses could make this calculation inaccurate
    def __black_box_pixels_to_angle(pixel_diff, HFOV, width_of_image_px):
        theta = HFOV / 2
        numerator = pixel_diff * math.tan(theta)
        denominator = width_of_image_px / 2
        return math.atan(numerator/denominator)


    # Returns True if the fixation acted upon is less than the minimum fixation length threshold. This fixation should then be removed, and neighboring gaps merged
    def short_fixation_filter(self, MIN_FIX_LEN:float=MIN_FIXATION_DUR_MS):
        remove = self.end_time_ms-self.start_time_ms < MIN_FIX_LEN
        if(remove):
            self.type = Event.Sample_Type.GAP
        return remove
    
    def __str__(self):
        working_string = ""
        match self.type:
            case Event.Sample_Type.FIXATION:
                working_string += "FIXATION"
            case Event.Sample_Type.GAP:
                working_string += "GAP"
        working_string += f", start: {self.start_time_ms}, end: {self.end_time_ms}"
        return working_string
    
    def __eq__(self, value):
        return (self.type == value.type) and (self.start_time_ms == value.start_time_ms) and (self.end_time_ms == value.end_time_ms)
    
def classify_event(relative_gaze_velocity, threshold):
    if relative_gaze_velocity < threshold:
        return Event.Sample_Type.FIXATION
    else:
        return Event.Sample_Type.GAP
