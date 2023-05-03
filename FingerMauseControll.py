import cv2
import mediapipe as mp
import pyautogui
from collections import deque
import time

# Constants
SMOOTHING_WINDOW_SIZE = 2

#PlayerMode
Show = False
PlayerMode = False
OnlyUp = True

#Sensetivity
MauseFingerSensetivity = 0.3 
ClickSensetivity = 0.04

# Set up video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
pyautogui.PAUSE = 0

# Get screen size
screen_width, screen_height = pyautogui.size()
pyautogui.FAILSAFE = False

# Set up MediaPipe hands
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

# Set up smoothing
index_finger_history = deque(maxlen=SMOOTHING_WINDOW_SIZE)
prew_wrist_x = None

while True:
    success, img = cap.read()

    # Convert the image to RGB for processing
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    # Check if any hands are detected
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:

            # Draw landmarks on the hands
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

            # Get the index and middle finger landmarks
            middle_finger = handLms.landmark[mpHands.HandLandmark.MIDDLE_FINGER_DIP]
            middle_finger2 = handLms.landmark[mpHands.HandLandmark.MIDDLE_FINGER_PIP]
            ring_finger = handLms.landmark[mpHands.HandLandmark.RING_FINGER_DIP]
            index_finger = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
            thumb = handLms.landmark[mpHands.HandLandmark.THUMB_TIP]
            wrist = handLms.landmark[mpHands.HandLandmark.WRIST]

            # Convert the normalized landmark coordinates to pixel coordinates
            index_finger_x, index_finger_y = int(index_finger.x * img.shape[1]), int(index_finger.y * img.shape[0])
            thumb_x, thumb_y = int(thumb.x * img.shape[1]), int(thumb.y * img.shape[0])
            wrist_x, wrist_y = int(wrist.x * img.shape[1]), int(wrist.y * img.shape[0])
            middle_finger2_x,  middle_finger2_y = int(middle_finger2.x * img.shape[1]), int(middle_finger2.y * img.shape[0])
            middle_finger_x, middle_finger_y = int(middle_finger.x * img.shape[1]), int(middle_finger.y * img.shape[0])
            ring_finger_x, ring_finger_y = int(ring_finger.x * img.shape[1]), int(ring_finger.y * img.shape[0])

            # Calculate the distance between the two fingers
            distanceDoubleClick = ((middle_finger2.x - thumb.x)**2 + (middle_finger2.y - thumb.y)**2)**0.5 # double clicks
            distanceclick = ((middle_finger.x - thumb.x)**2 + (middle_finger.y - thumb.y)**2)**0.5 # clicks
            distancehand = ((wrist.x - index_finger.x)**2 + (wrist.y - index_finger.y)**2)**0.5 # is index is open
            stophand1 = ((index_finger.x - wrist.x)**2 + (index_finger.y - wrist.y)**2)**0.5
            stophand2 = ((middle_finger.x - wrist.x)**2 + (middle_finger.y - wrist.y)**2)**0.5
            stophand3 = ((ring_finger.x - wrist.x)**2 + (ring_finger.y - wrist.y)**2)**0.5

            # Draw a line between the fingers
            color1 = (0,distancehand* 255,255 - (distancehand*255))
            color2 = (0,distanceclick* 255,255 - (distanceclick*255))
            color3 = (0,distanceDoubleClick* 255,255 - (distanceDoubleClick*255))
            cv2.line(img, (index_finger_x, index_finger_y), (wrist_x, wrist_y), color1, 2)
            cv2.line(img, (thumb_x, thumb_y), (middle_finger_x, middle_finger_y), color2, 2)
            cv2.line(img, (thumb_x, thumb_y), (middle_finger2_x, middle_finger2_y), color3, 2)

            # Add the current index finger position to the history
            index_finger_history.append((index_finger_x, index_finger_y))

            # Calculate the average position over the last few frames
            avg_index_finger_x = sum(p[0] for p in index_finger_history) // len(index_finger_history)
            avg_index_finger_y = sum(p[1] for p in index_finger_history) // len(index_finger_history)

            
            print(stophand2)
            #PlayerMode
            print(wrist_y)
            if PlayerMode:
                #if hands is up in air
                if OnlyUp:
                    if wrist_y < 300:
                        #if hand moves right
                        if prew_wrist_x == None:
                            prew_wrist_x = wrist_x
                        if stophand1 > 0.4 and stophand2 > 0.4 and stophand3 > 0.3: #Pause
                            print("pause")
                            pyautogui.press('space')
                            time.sleep(2)
                        elif stophand1 > 0.4 and stophand2 > 0.4:
                            print('hand moved right')     
                            pyautogui.keyDown('shift')
                            pyautogui.keyDown('n')
                            time.sleep(2)
                            pyautogui.keyUp('n')
                            pyautogui.keyUp('shift')
                        elif index_finger.x < wrist.x and stophand2 < 0.6: #Right
                                print("right")
                                pyautogui.press('right')
                                time.sleep(1)
                        elif index_finger.x > wrist.x and stophand2 < 0.6: #Left
                            print("left")  
                            pyautogui.press('left')
                            time.sleep(1)
                        prew_wrist_x = wrist_x
            else:
                # Move the mouse cursor to the average position
                if distancehand > 0.3: # if index finger open
                    inverted_x = screen_width - (avg_index_finger_x * 4)
                    pyautogui.moveTo(inverted_x*2, avg_index_finger_y*4, 0.1,tween=pyautogui.easeInExpo)

                    # Perform a click if the distance between the fingers is below a threshold
                    if distanceclick < ClickSensetivity:
                        pyautogui.mouseDown()
                        time.sleep(1)
                        pyautogui.mouseUp()
                    elif distanceDoubleClick < ClickSensetivity:
                        pyautogui.doubleClick()
                        time.sleep(1)

            
    if Show:
        cv2.imshow("Image", img)
        cv2.waitKey(1)