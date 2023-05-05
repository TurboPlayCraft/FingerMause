import cv2
import keyboard
import mediapipe as mp
import pyautogui
from collections import deque
from Notification import *
import tkinter as tk
import time

#PlayerMode
Show = False
PlayerMode = True
OnlyUp = True

#MAUSEMODE Sensetivity
MauseFingerSensetivity = 0.3 
ClickSensetivity = 0.04
#MEDIAPLAYERMODE Sensetivity
PoseRecSensetivity = 0.3 #More for smaller hands and longer distances

# Constants
SMOOTHING_WINDOW_SIZE = 2 #More stable but high latency

# Set up video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

# Get screen size
screen_width, screen_height = pyautogui.size()

# create a hidden root window
root = tk.Tk()
root.withdraw()

# Set up MediaPipe hands
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

# Set up smoothing
index_finger_history = deque(maxlen=SMOOTHING_WINDOW_SIZE)
prew_wrist_x = None

# TIMER
timer = 0
def settimer(timervalue):
    global timer 
    timer = timervalue
    
# PROCESS FRAME
def process_frame():
    success, img = cap.read()
    global timer,PlayerMode
    timer-=1
    print(timer)
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
            color1 = (0,distancehand* 255,255 - (distancehand*255) * 2)
            color2 = (0,(distanceclick* 255)*3,255 - (distanceclick*255) * 2)
            color3 = (0,(distanceDoubleClick* 255)*3,255 - (distanceDoubleClick*255) * 2)
            color5 = (0,stophand2*255,255-(stophand2*255) * 2)
            color4 = (0,stophand3 *255,255 - (stophand3*255) * 2)
            cv2.line(img, (wrist_x, wrist_y), (index_finger_x, index_finger_y), color1, 2)
            cv2.line(img, (wrist_x, wrist_y), (middle_finger2_x, middle_finger2_y), color5, 2)
            cv2.line(img, (wrist_x, wrist_y), (ring_finger_x, ring_finger_y), color4, 2)
            cv2.line(img, (thumb_x, thumb_y), (middle_finger_x, middle_finger_y), color2, 2)
            cv2.line(img, (thumb_x, thumb_y), (middle_finger2_x, middle_finger2_y), color3, 2)

            # Add the current index finger position to the history
            index_finger_history.append((index_finger_x, index_finger_y))

            # Calculate the average position over the last few frames
            avg_index_finger_x = sum(p[0] for p in index_finger_history) // len(index_finger_history)
            avg_index_finger_y = sum(p[1] for p in index_finger_history) // len(index_finger_history)

            print(stophand1)
            print(stophand2)
            print(stophand3)
            #PlayerMode
            print(wrist_y)
            if PlayerMode:
                #if hands is up in air
                if OnlyUp:
                    minHight = 300
                else:
                    minHight = 1000

                if wrist_y < minHight:
                    if stophand1 > PoseRecSensetivity and stophand2 > PoseRecSensetivity and stophand3 > PoseRecSensetivity and timer<1: #Pause
                        show_notification(root,"Notification space", "Pause")
                        root.update()
                        print("pause")
                        pyautogui.press('space')
                        settimer(30)
                    elif stophand1 > PoseRecSensetivity  + 0.1 and stophand2 > PoseRecSensetivity + 0.1 and timer<1:
                        show_notification(root,"Notification Next", "Next")
                        root.update()
                        print('Next >>')     
                        pyautogui.keyDown('shift')
                        pyautogui.keyDown('n')
                        time.sleep(0.1)
                        pyautogui.keyUp('n')
                        pyautogui.keyUp('shift')
                        settimer(50)
                    elif index_finger.x < wrist.x and stophand2 < 0.6 and timer<1: #Right   
                        show_notification(root,"Notification Right", "Right")
                        root.update()
                        print("right >")
                        pyautogui.press('right')
                        settimer(5)
                    elif index_finger.x > wrist.x and stophand2 < 0.6 and timer<1: #Left 
                        show_notification(root,"Notification Left", "Left")      
                        root.update()
                        print("< left")  
                        pyautogui.press('left')
                        settimer(10)
            else:
                # Move the mouse cursor to the average position
                if distancehand > 0.3: # if index finger open
                    inverted_x = screen_width - (avg_index_finger_x * 4)
                    pyautogui.moveTo(inverted_x*2, avg_index_finger_y*4, 0.1,tween=pyautogui.easeInExpo)

                    # Perform a click if the distance between the fingers is below a threshold
                    if distanceclick < ClickSensetivity and timer<1:
                        pyautogui.mouseDown()
                        settimer(5)
                        pyautogui.mouseUp()
                    elif distanceDoubleClick < ClickSensetivity and timer<1:
                        pyautogui.doubleClick()
                        settimer(10)
    if Show:
        cv2.imshow("Image", img)
        cv2.waitKey(1)
      
    #check if pressed M key
    if keyboard.is_pressed('m') and timer<1:
        settimer(10)
        PlayerMode = not PlayerMode
        if PlayerMode:
            show_notification(root,"Notification Mode","PlayerMode is ON")
        else:
            show_notification(root,"Notification Mode","PlayerMode is OFF")

    # Schedule the next iteration of the main loop
    root.after(1, process_frame)

# Start the main loop
process_frame()
root.mainloop()