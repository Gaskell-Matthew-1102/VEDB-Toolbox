# All code in this file is our own work.
from enum import Enum
import numpy as np
import math

def build_event(relative_gaze_velocity:float, threshold:float, start_time_s:float, end_time_s:float, start_pos:np.ndarray[2], end_pos:np.ndarray[2]):
    return Event(classify_event(relative_gaze_velocity, threshold), start_time_s, end_time_s, start_pos, end_pos)

class Event:
    class Sample_Type(Enum):
        FIXATION = 1
        GAP = 2
    
    def __init__(self, type:Sample_Type, start_time_s:float, end_time_s:float, start_pos:np.ndarray[2], end_pos:np.ndarray[2]):
        self.type = type
        self.start_time_s = start_time_s
        self.end_time_s = end_time_s

        if isinstance(start_pos, np.ndarray):
            self.start_pos = start_pos
        elif isinstance(start_pos, list):
            self.start_pos = np.array(start_pos)
        else:
            raise TypeError
        
        if isinstance(end_pos, np.ndarray):
            self.end_pos = end_pos
        elif isinstance(end_pos, list):
            self.end_pos = np.array(end_pos)
        else:
            raise TypeError

    
    def calculate_gap_amplitude(self, start_pix, end_pix, width_of_image_px, hfov):
        angle = self.__black_box_pixels_to_angle(start_pix, end_pix, width_of_image_px, hfov)
        return angle

    def __black_box_pixels_to_angle(self, start_pix, end_pix, width_of_image_px, hfov):
    # CHECK ACCURACY. this equation below assumes the start point is the center. lenses could make this calculation inaccurate
        theta = hfov / 2
        numerator = (np.linalg.norm(end_pix - start_pix)) * math.tan(math.radians(theta))
        denominator = width_of_image_px / 2
        return math.degrees(math.atan(numerator/denominator))
        # dy = end_pix[1] - start_pix[1]
        # dx = end_pix[0] - start_pix[0]
        # return math.degrees(math.atan2(dy,dx))
    
    # Returns True if the gap is a micro-saccade and should be removed. The gap, if True is returned, should be treated as a fixation
    def microsaccade_filter(self, min_saccade_amp_deg, min_saccade_dur_ms, width_of_image_px, hfov) -> bool:
        flag = False
        gap_amp = self.calculate_gap_amplitude(self.start_pos, self.end_pos, width_of_image_px, hfov)
        if( (gap_amp < min_saccade_amp_deg) and (self.end_time_s - self.start_time_s < min_saccade_dur_ms / 1000) ):
            flag = True
        return flag

    # Returns True if the fixation acted upon is less than the minimum fixation length threshold. This fixation should then be removed, and neighboring gaps merged
    def short_fixation_filter(self, min_fix_len_ms:float):
        remove = self.end_time_s-self.start_time_s < (min_fix_len_ms / 1000)
        return remove
    
    def __str__(self):
        working_string = ""
        match self.type:
            case Event.Sample_Type.FIXATION:
                working_string += "FIXATION"
            case Event.Sample_Type.GAP:
                working_string += "GAP"
        working_string += f", start: {self.start_time_s}, end: {self.end_time_s}"
        return working_string
    
    def __eq__(self, value):
        return (self.type == value.type) and (self.start_time_s == value.start_time_s) and (self.end_time_s == value.end_time_s) and (np.array_equal(self.start_pos, value.start_pos)) and (np.array_equal(self.end_pos, value.end_pos))
    
def classify_event(relative_gaze_velocity, threshold):
    if relative_gaze_velocity < threshold:
        return Event.Sample_Type.FIXATION
    else:
        return Event.Sample_Type.GAP
