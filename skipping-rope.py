# Wow I'm glad that you are interested in my code :) I wonder who you are
# If we ever meet in the future, I would like to invite you for a coffee to discuss further possibilites of AI and automation
# Now enjoy finding bugs and helping me improve my code!

import time,csv
from datetime import datetime

import cv2
import mediapipe as mp
import numpy as np

def sec_to_min(seconds):
    mmss = time.strftime('%M:%S', time.gmtime(seconds))
    return mmss

def circle(text,center,header):
    cv2.circle(image, center, 48, CIRCLE_COLOR , -1)
    text_size, _ = cv2.getTextSize(text, TEXT_FACE, TEXT_SCALE, TEXT_THICKNESS)
    text_origin = (center[0] - text_size[0] // 2, center[1] + text_size[1] // 2) 
    cv2.putText(image, header[1], header[0] , 1, 1, (0,0,0), TEXT_THICKNESS, cv2.LINE_AA)
    cv2.putText(image, text, text_origin, 
                    TEXT_FACE, TEXT_SCALE, (0,0,0), TEXT_THICKNESS, cv2.LINE_AA)

def counter_to_txt(Counter):
    with open('counter.txt', 'w') as f:
        f.write(str(Counter))

def write_to_tracking_progress():
    try:
        info = [datetime.now().strftime("%Y/%m/%d %H:%M:%S"),COUNTER,round(TIME_ELAPSED),round(COUNTER/(TIME_ELAPSED/60))]
        with open('tracking-progress.csv', mode='a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(info)
    except:
        pass

def right_hand_up():
    global START_LIST_RIGHT
    right_hand_y = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y
    right_eye_y = landmarks[mp_pose.PoseLandmark.RIGHT_EYE.value].y
    START_LIST_RIGHT.append(right_hand_y-right_eye_y)
    if right_hand_y-right_eye_y <0: #len(START_LIST_RIGHT)>10 and all(i < 0 for i in START_LIST_RIGHT[-10:]):
        START_LIST_RIGHT.clear()
        return True
    else:
        #START_LIST_RIGHT = START_LIST_RIGHT[-30:]
        return False
def left_hand_up():
    global START_LIST_LEFT
    left_hand_y = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y
    left_eye_y = landmarks[mp_pose.PoseLandmark.LEFT_EYE.value].y
    START_LIST_LEFT.append(left_hand_y-left_eye_y)
    if left_hand_y-left_eye_y <0: #len(START_LIST_LEFT)>10 and all(i < 0 for i in START_LIST_LEFT[-10:]):
        START_LIST_LEFT.clear()
        return True
    else: 
        #START_LIST_LEFT = START_LIST_LEFT[-30:]
        return False

#Initialization
COUNTER = 0
TOTAL_COUNTER = 0
STATE = "Rest"
TIME_ELAPSED = 0
PREV_COORDINATE=0
DIFF = 0.02
START_LIST_RIGHT = []
START_LIST_LEFT = []
RIGHT_LIST = []
LEFT_LIST = []
#Circles & Texts
CIRCLE_COLOR = (189, 158, 255)#I love pink, especially pastel pink
CENTER1 = (50, 50) #Counter
CENTER2 = (50, 150) #STATE
CENTER3 = (50, 250) #Duration
CENTER4 = (50, 350) #Total_Counter
HEADER1 = [(20,30),"Counter"]
HEADER2 = [(26,130),"State"]
HEADER3 = [(20,230),"Duration"]
HEADER4 = [(28,330),"Total"]

TEXT_SCALE = 1
TEXT_FACE = cv2.FONT_HERSHEY_DUPLEX
TEXT_THICKNESS = 1

## Setup mediapipe instance
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        
        # Recolor image to RGB for better detection
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
      
        # Make detection
        results = pose.process(image)

        # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
       
        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark         
            # Get coordinates of left shoulder, it can be any point on body
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            visibility = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].visibility
            RIGHT_LIST.append(right_hand_up())
            LEFT_LIST.append(left_hand_up())
            Righthandup = all(i==True for i in RIGHT_LIST[-10:])
            Lefthandup = all(i==True for i in LEFT_LIST[-10:])
            if Righthandup and Lefthandup: #or (cv2.waitKey(10) & 0xFF == ord('q')):
                counter_to_txt("FINISH")
                break
            elif STATE == "Rest" and Righthandup and not Lefthandup : # User hasn't started the exercise
                COUNTER = 0 #Start counting
                STATE = "down"           
                counter_to_txt("START")
            elif STATE == "Pause" and Righthandup and not Lefthandup:
                COUNTER = 0 #Start counting
                STATE = "down"           
                counter_to_txt("CONTINUE")
            elif STATE == "up" or STATE == "down":
                if Lefthandup and not Righthandup:
                    STATE = "Pause"        
                    counter_to_txt("Pause")
                    write_to_tracking_progress()
                elif visibility>0.6:
                    # Visualize
                    cv2.putText(image, str(round(shoulder[1],3)), 
                                    tuple(np.multiply(shoulder, [640, 480]).astype(int)), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
                    # Skipping rope Counter Logic   
                    if shoulder[1]< PREV_COORDINATE-DIFF and STATE == "down":
                        STATE = "up"
                        print("up")          
                    if shoulder[1]> PREV_COORDINATE+DIFF and STATE == "up":
                        STATE = "down"
                        COUNTER +=1
                        TOTAL_COUNTER +=1
                        print("down")
                        if COUNTER % 10 == 0:
                            #write Counter to txt
                            counter_to_txt(COUNTER)
                            # say sth
                    PREV_COORDINATE = shoulder[1]  
        except BaseException as error:
            #print('An exception occurred: {}'.format(error))
            pass
        if  COUNTER == 0:
            startTime = datetime.now()
        else:
            TIME_ELAPSED =(datetime.now() - startTime).total_seconds()
        
        circle(str(COUNTER),CENTER1,HEADER1)
        circle(STATE,CENTER2,HEADER2)
        circle(sec_to_min(seconds=TIME_ELAPSED),CENTER3,HEADER3)
        circle(str(TOTAL_COUNTER),CENTER4,HEADER4)

        # Detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(255, 134, 133), thickness=2, circle_radius=2), 
                                mp_drawing.DrawingSpec(color=(189, 158, 255), thickness=2, circle_radius=2) 
                                    )               
        cv2.imshow('Skipping Rope', image)
        cv2.imshow('Camera', frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    counter_to_txt(0)