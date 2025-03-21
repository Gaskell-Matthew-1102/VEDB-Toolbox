from fixation_packages.event import Event
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
            new_event_list = np.concatenate((new_event_list, self.return_merge_event_list(left_i, transition_list[i]-1)))
            left_i = transition_list[i]
        new_event_list = np.concatenate((new_event_list, self.return_merge_event_list(left_i, self.list.size-1)))
        self.list = new_event_list
        return new_event_list

    # Merges two neightboring events, returns new array (len of 1) with the right and all middle events after merge
    def return_merge_event_list(self, left_event_i, right_event_i):
        # if(self.list[left_event_i].type != self.list[right_event_i].type):
        #     raise ValueError
        left_event = self.list[left_event_i]
        right_event = self.list[right_event_i]
        new_event = Event(left_event.type, left_event.start_time_s, right_event.end_time_s, left_event.start_pos, right_event.end_pos)
        return np.array([new_event])
    
    # Applies the microsaccade filter on all events, merging any removed gap events
    def microsaccade_filter(self, min_saccade_amp_deg, min_saccade_dur_ms):
        arr = self.list
        # new_arr = np.array([])
        bitarr = bitarray.bitarray(arr.size)
        
        for event_i in range(arr.size):
            bitarr[event_i] = arr[event_i].microsaccade_filter(min_saccade_amp_deg, min_saccade_dur_ms)
        # [print(x, end='') for x in bitarr]
        
        # Iteration variable for bitmap, initializing out here so we can account for first case
        i = 0
        # Case where first bit is 1
        if bitarr[0] == 1:
            i = 1
        # Case where the last bit is 1
        if bitarr[len(bitarr)-1]:
            bitarr = bitarr[0:-1]

        new_arr = np.array([])
        for i in range(i, len(bitarr)):
            if(bitarr[i] == 1):
                append_event = self.return_merge_event_list(i-1, i+1)
                i += 1
            else:
                append_event = np.array([arr[i]])
            new_arr = np.concatenate((new_arr[:-1], append_event))

            for x in range(new_arr.size):
                print(i, x, new_arr[x])
            print()

        # print('a ', [print(type(x)) for x in new_arr])
        self.list = new_arr


            # print(i, bitarr[i], arr[i])



        
        # event_i = 0
        # while event_i < arr_len:
        #     event = arr[event_i]
        #     remove = event.microsaccade_filter(min_saccade_amp_deg, min_saccade_dur_ms)
        #     print(event_i, event, remove)
        #     if not remove:
        #         new_arr = np.concatenate((new_arr, np.array([event])))
        #         event_i += 1
        #         continue
        #     first_event_i = -1
        #     second_event_i = -1
        #     # edge cases (first or last event is gap which needs to be removed) (currently just removes those samples, no merging)
        #     if event_i == 0:
        #         first_event_i = 0
        #         second_event_i = 1
        #         event_i += 1
        #         # arr_len -= 1
        #         continue
        #     elif event_i == arr_len-1:
        #         # first_event_i = event_i-1
        #         # second_event_i = event_i
        #         break
        #     else:
        #         # normal case
        #         first_event_i = event_i-1
        #         second_event_i = event_i+1
        #     len_change = abs(second_event_i - first_event_i)
        #     merged_event = self.return_merge_event_list(first_event_i, second_event_i)
        #     merged_event[0].Sample_Type = Event.Sample_Type.FIXATION       # manually label as fixation in the case of the first event being a removed gap

        #     new_arr = np.concatenate((new_arr[:new_arr.size-1], merged_event))       
        #     arr_len -= 1
        #     event_i += 2
        # self.list = new_arr                
            

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