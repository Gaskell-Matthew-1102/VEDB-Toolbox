# from fixation_packages.event import Event
from .event import Event
import bitarray
import numpy as np

class EventList:
    def __init__(self, in_arr:np.array):
        self.list = in_arr

    def print_list_contents(self):
        for item in self.list:
            print(item, sep=" ")

    def return_list_summary(self):
        gap_count = 0
        fixation_count = 0
        for item in self.list:
            match item.type:
                case Event.Sample_Type.FIXATION:
                    fixation_count += 1
                case Event.Sample_Type.GAP:
                    gap_count += 1
                case _:
                    print("Error")
        return (fixation_count, gap_count)
    
    # Goes through the event list, automatically merging and consolidating all neighoring events. Used before (and after?) classification
    def consolidate_list(self):
        transition_list = []
        # Build a list of transition events
        current_event_type = self.list[0].type
        for i in range(1, self.list.size):
            if self.list[i].type != current_event_type:
                transition_list.append(i)
                current_event_type = self.list[i].type
        # print(transition_list)
        left_i = 0
        new_event_list = np.array([])
        for i in range(len(transition_list)):
            new_event_list = np.concatenate((new_event_list, self.return_merge_event_list(self.list[left_i], self.list[transition_list[i]-1])))
            left_i = transition_list[i]
        new_event_list = np.concatenate((new_event_list, self.return_merge_event_list(self.list[left_i], self.list[-1])))
        self.list = new_event_list
        return new_event_list

    # Merges two neightboring events, returns new array (len of 1) with the right and all middle events after merge
    def return_merge_event_list(self, left_event, right_event):
        # if(self.list[left_event_i].type != self.list[right_event_i].type):
        #     raise ValueError
        new_event = Event(left_event.type, left_event.start_time_s, right_event.end_time_s, left_event.start_pos, right_event.end_pos)
        return np.array([new_event])
    
    # Applies the microsaccade filter on all events, merging any removed gap events
    def apply_filter(self, filter, **kwargs):
        arr = self.list
        # new_arr = np.array([])
        bitarr = bitarray.bitarray(arr.size)

        if(filter == Event.microsaccade_filter):
            for event_i in range(arr.size):
                bitarr[event_i] = arr[event_i].microsaccade_filter(kwargs["min_saccade_amp_deg"], kwargs["min_saccade_dur_ms"], kwargs["width_of_image_px"], kwargs["hfov"])
        elif(filter == Event.short_fixation_filter):
            for event_i in range(arr.size):
                bitarr[event_i] = arr[event_i].short_fixation_filter(kwargs["min_fixation_dur_ms"])
        
        # Iteration variable for bitmap, initializing out here so we can account for first case
        # Case where first bit is 1
        i = 0
        if bitarr[0] == 1:
            i = 1
        # Case where the last bit is 1
        if bitarr[len(bitarr)-1]:
            bitarr = bitarr[:-1]


        new_arr = np.array([])
        while i < len(bitarr):
            if(bitarr[i] == 1):
                append_event = self.return_merge_event_list(new_arr[-1], self.list[i+1])
                new_arr = np.concatenate((new_arr[:-1], append_event))
                i += 1
            else:
                append_event = np.array([arr[i]])
                new_arr = np.concatenate((new_arr, append_event))
            i += 1
        self.list = new_arr


    def __str__(self):
        working_string = ""
        for item in self.list:
            working_string += f"{item}\n"
        return working_string
    
    def __eq__(self, value):
        if self.list.size != value.list.size:
            return False
        for i in range(self.list.size):
            if self.list[i] != value.list[i]:
                return False
        return True
    
    def __iter__(self):
        return iter(self.list)  # Makes EventList iterable