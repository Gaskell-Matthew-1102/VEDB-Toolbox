from multiprocessing import Manager, Process
from fixation.main import runner as fixation_main

def main():    
    fix_det_args = (
        "2023_06_01_18_47_34", "odometry.pldata", "gaze.npz",
        './fixation/test_data/videos/video.mp4',
        "./fixation/export/export_fixation.json",
        "./fixation/export/export_parameters.txt",
        300, 3, 750, 0.8, 30, 200, 2048, 1536, 90, 90, True
    )
    
    fix_det = Process(target=fixation_main, args=fix_det_args)
    fix_det.start()
    print('a'*5000)
    fix_det.join()

if __name__ == '__main__':
    main()