
import numpy as np 
import cv2 
  

def do_it():

    cap = cv2.VideoCapture('flaskr/fixation/test/videos/video.mp4')
    cap.set(cv2.CAP_PROP_POS_FRAMES, 25000)
    frame_count = 0
    
    # params for corner detection 
    feature_params = dict( maxCorners = 250, 
                        qualityLevel = 0.3, 
                        minDistance = 7, 
                        blockSize = 7 ) 
    
    # Parameters for lucas kanade optical flow 
    lk_params = dict( winSize = (100, 100), 
                    maxLevel = 2, 
                    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 
                                10, 0.03)) 
    
    # Create some random colors 
    color = np.random.randint(0, 255, (100, 3)) 
    
    # Take first frame and find corners in it 
    ret, old_frame = cap.read() 
    old_gray = cv2.cvtColor(old_frame, 
                            cv2.COLOR_BGR2GRAY) 
    p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, 
                                **feature_params) 
    
    # Create a mask image for drawing purposes 
    mask = np.zeros_like(old_frame) 

    vec_list = []
    while(frame_count <= 1500): 
        
        ret, frame = cap.read() 
        frame_gray = cv2.cvtColor(frame, 
                                cv2.COLOR_BGR2GRAY) 
    
        # calculate optical flow 
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, 
                                            frame_gray, 
                                            p0, None, 
                                            **lk_params) 
        
        if(p1 is None):
            break
    
        # Select good points 
        good_new = p1[st == 1] 
        good_old = p0[st == 1] 
    
        # draw the tracks 
        for i, (new, old) in enumerate(zip(good_new,  
                                        good_old)): 
            a, b = new.ravel() 
            c, d = old.ravel() 

            vec_list.append( np.column_stack((c-a, d-b)) )

            mask = cv2.line(mask, (int(a), int(b)), (int(c), int(d)), 
                            color[i].tolist(), 2) 
            
            frame = cv2.circle(frame, (int(a), int(b)), 5, 
                            color[i].tolist(), -1) 
            
        img = cv2.add(frame, mask) 
    
        cv2.putText(frame, f"{frame_count}", (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)
        cv2.imshow('frame', img) 
        
        k = cv2.waitKey(25) 
        if k == 27: 
            break
    
        # Updating Previous frame and points  
        old_gray = frame_gray.copy() 
        p0 = good_new.reshape(-1, 1, 2) 
        frame_count += 1
    
    cv2.destroyAllWindows() 
    cap.release() 
    return vec_list