import cv2
import numpy as np

def create_grid(shape, step=10):
    """Create a grid of points over the image."""
    h, w = shape
    y, x = np.mgrid[step//2:h:step, step//2:w:step]  # Generate grid points
    return np.float32(np.stack((x, y), axis=-1).reshape(-1, 1, 2))  # Reshape to (N, 1, 2)

def do_it(filepath: str):

    cap = cv2.VideoCapture(filepath)  # Load video
    # cap.set(cv2.CAP_PROP_POS_FRAMES, 10000)
    ret, old_frame = cap.read()
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)

    # Create initial grid
    step_size = min(old_gray.shape) // 100  # Adjust step size dynamically
    p0 = create_grid(old_gray.shape, step=step_size)
    initial_point_count = len(p0)

    # Lucas-Kanade parameters
    lk_params = dict(winSize=(15, 15), maxLevel=2,
                    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    frame_count = 0
    vec_list = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate optical flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

        # Keep only points that were successfully tracked
        good_new = p1[st == 1]
        good_old = p0[st == 1]

        frame_vec_list = []
        # Draw flow vectors
        for (new, old) in zip(good_new, good_old):
            a, b = new.ravel()
            c, d = old.ravel()
            frame_vec_list.append( np.column_stack((c-a, d-b)) )
            cv2.arrowedLine(frame, (int(c), int(d)), (int(a), int(b)), (0, 255, 0), 1, tipLength=0.3)

        vec_list.append( frame_vec_list )

        cv2.imshow("Optical Flow", frame)
        cv2.putText(frame, f"{len(p0)}", (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)

        # Check if the number of tracked points has dropped too low
        if len(good_new) < 0.25 * initial_point_count:  # If less than 25% remain
            p0 = create_grid(old_gray.shape, step=step_size)  # Reset grid
            print("Resetting grid...")
        else:
            p0 = good_new.reshape(-1, 1, 2)  # Update points

        old_gray = frame_gray.copy()

        if cv2.waitKey(30) & 0xFF == 27:
            break
        frame_count += 1
        if frame_count >= 50:       # FOR THE DEMO
            break
    cap.release()
    cv2.destroyAllWindows()
    return vec_list

if __name__ == '__main__':
    do_it('test_data/videos/video.mp4')