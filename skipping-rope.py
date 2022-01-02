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

#Initialization
COUNTER = 0
STAGE = "down"
TIME_ELAPSED = 0
PREV_COORDINATE=0
DIFF = 0.02
#Circles & Texts
CIRCLE_COLOR = (189, 158, 255)#I love pink, especially pastel pink
CENTER1 = (50, 50) #Counter
CENTER2 = (150, 50) #Stage
CENTER3 = (250, 50) #Duration
HEADER1 = [(20,30),"Counter"]
HEADER2 = [(130,30),"State"]
HEADER3 = [(216,30),"Duration"]

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
            if visibility>0.6:
                # Visualize
                cv2.putText(image, str(round(shoulder[1],3)), 
                                tuple(np.multiply(shoulder, [640, 480]).astype(int)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
                # Skipping rope Counter Logic   
                if shoulder[1]< PREV_COORDINATE-DIFF and STAGE == "down":
                    STAGE = "up"
                    #print("up")          
                if shoulder[1]> PREV_COORDINATE+DIFF and STAGE == "up":
                    STAGE = "down"
                    COUNTER +=1
                    #print("down")
                    #if counter % 100 == 0:
                    #    print("say sth")   
                PREV_COORDINATE = shoulder[1]  
        except BaseException as error:
            print('An exception occurred: {}'.format(error))
            
        if  COUNTER == 0:
            startTime = datetime.now()
        else:
            TIME_ELAPSED =(datetime.now() - startTime).total_seconds()
        
        circle(str(COUNTER),CENTER1,HEADER1)
        circle(STAGE,CENTER2,HEADER2)
        circle(sec_to_min(seconds=TIME_ELAPSED),CENTER3,HEADER3)

        # Detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(255, 134, 133), thickness=2, circle_radius=2), 
                                mp_drawing.DrawingSpec(color=(189, 158, 255), thickness=2, circle_radius=2) 
                                    )               
        cv2.imshow('Skipping Rope', image)
        cv2.imshow('Camera', frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            try:
                info = [datetime.now().strftime("%Y/%m/%d %H:%M:%S"),COUNTER,round(TIME_ELAPSED),round(COUNTER/(TIME_ELAPSED/60))]
                with open('tracking-progress.csv', mode='a',newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(info)
            except:
                pass
            break

    cap.release()
    cv2.destroyAllWindows()
