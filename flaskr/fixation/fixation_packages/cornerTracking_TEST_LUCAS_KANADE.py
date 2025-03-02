import cv2
import numpy as np

# Parameters for corner detection 
feature_params = dict(maxCorners=250, qualityLevel=0.3, minDistance=7, blockSize=7)

# Parameters for Lucas-Kanade optical flow
lk_params = dict(winSize=(21, 21), maxLevel=3,
                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    # cap.set(cv2.CAP_PROP_POS_FRAMES, 10000)

    # Read the first frame and detect features
    ret, old_frame = cap.read()
    if not ret:
        print("Error: Could not read video.")
        return
    
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)

    vec_list = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate optical flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
        
        if p1 is not None:
            good_new = p1[st == 1]
            good_old = p0[st == 1]

            frame_vec_list = []
            # Draw flow vectors
            for i, (new, old) in enumerate(zip(good_new, good_old)):
                a, b = new.ravel()
                c, d = old.ravel()
                frame = cv2.line(frame, (int(a), int(b)), (int(c), int(d)), (0, 255, 0), 2)
                frame = cv2.circle(frame, (int(a), int(b)), 5, (0, 0, 255), -1)
                frame_vec_list.append( np.column_stack((c-a, d-b)) )

            # Update previous frame and points
            vec_list.append( frame_vec_list )
            old_gray = frame_gray.copy()
            p0 = good_new.reshape(-1, 1, 2)

        if len(p0) < 15:
            print("Reacquiring points")
            p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)

        cv2.imshow('Optical Flow', frame)
        if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
            break

    cap.release()
    cv2.destroyAllWindows()
    return vec_list



# Run the function
if __name__ == "__main__":
    process_video("test_data/videos/video.mp4")
