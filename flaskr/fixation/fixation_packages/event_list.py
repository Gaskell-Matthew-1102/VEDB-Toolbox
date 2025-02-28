from fixation_packages.event import Event
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
        print(transition_list)
        left_i = 0
        new_event_list = np.array([])
        for i in range(len(transition_list)):
            new_event_list = np.concatenate((new_event_list, self.return_merge_event_list(left_i, transition_list[i]-1)))
            left_i = transition_list[i]
        new_event_list = np.concatenate((new_event_list, self.return_merge_event_list(left_i, self.list.size-1)))
        self.list = new_event_list
        return new_event_list

    # Merges two neightboring events, returns new array (len of 1) with the right and all middle events after merge
    def return_merge_event_list(self, left_event_i, right_event_i):
        if(self.list[left_event_i].type != self.list[right_event_i].type):
            raise ValueError
        left_event = self.list[left_event_i]
        right_event = self.list[right_event_i]
        new_event = Event(left_event.type, left_event.start_time_ms, right_event.end_time_ms)
        return np.array([new_event])
    
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