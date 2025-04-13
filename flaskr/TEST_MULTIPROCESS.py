from multiprocessing import Manager, Process
from fixation import main as fixation_main

from file_upload import get_video_list, get_graph_file_list

graph_files = get_graph_file_list()
video_files = get_video_list()

odometry_file = ""
video_file = ""

for file in graph_files:
    if "odometry" in file:
        odometry_file = file

for file in video_files:
    if "world" in file:
        video_file = file

# video file and graph file now point to the dynamically uploaded files, run all this code after uploading video files

def main():
    fix_det_args = ("2023_06_01_18_47_34", "odometry.pldata", "gaze.npz", './flaskr/fixation/test_data/videos/video.mp4', "./flaskr/fixation/export.json", 55, 3, 700, 0.8, 30, 200)
    fix_det = Process(target=fixation_main, args=fix_det_args)
    fix_det.start()

if __name__ == '__main__':
    main()