from multiprocessing import Manager, Process
from fixation import main as fixation_main

def main():
    fix_det_args = ("2023_06_01_18_47_34", "odometry.pldata", "gaze.npz", './flaskr/fixation/test_data/videos/video.mp4', "./flaskr/fixation/export.json", 55, 3, 700, 0.8, 30, 200)
    fix_det = Process(target=fixation_main, args=fix_det_args)
    fix_det.start()

if __name__ == '__main__':
    main()