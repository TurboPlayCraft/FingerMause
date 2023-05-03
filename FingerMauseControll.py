import cv2
import mediapipe as mp
import pyautogui
from collections import deque
import time

# Constants
SMOOTHING_WINDOW_SIZE = 2

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
            index_finger = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
            thumb = handLms.landmark[mpHands.HandLandmark.THUMB_TIP]
            wrist = handLms.landmark[mpHands.HandLandmark.WRIST]

            # Convert the normalized landmark coordinates to pixel coordinates
            index_finger_x, index_finger_y = int(index_finger.x * img.shape[1]), int(index_finger.y * img.shape[0])
            thumb_x, thumb_y = int(thumb.x * img.shape[1]), int(thumb.y * img.shape[0])
            wrist_x, wrist_y = int(wrist.x * img.shape[1]), int(wrist.y * img.shape[0])
            middle_finger_x, middle_finger_y = int(middle_finger.x * img.shape[1]), int(middle_finger.y * img.shape[0])

            # Calculate the distance between the two fingers
            distanceclick = ((middle_finger.x - thumb.x)**2 + (middle_finger.y - thumb.y)**2)**0.5 # clicks
            distancehand = ((wrist.x - index_finger.x)**2 + (wrist.y - index_finger.y)**2)**0.5 # is index is open

            # Draw a line between the fingers
            color1 = (0,distancehand* 255,255 - (distancehand*255))
            color2 = (0,distanceclick* 255,255 - (distanceclick*255))
            cv2.line(img, (index_finger_x, index_finger_y), (wrist_x, wrist_y), color1, 2)
            cv2.line(img, (thumb_x, thumb_y), (middle_finger_x, middle_finger_y), color2, 2)

            # Add the current index finger position to the history
            index_finger_history.append((index_finger_x, index_finger_y))

            # Calculate the average position over the last few frames
            avg_index_finger_x = sum(p[0] for p in index_finger_history) // len(index_finger_history)
            avg_index_finger_y = sum(p[1] for p in index_finger_history) // len(index_finger_history)

            # Move the mouse cursor to the average position
            #print(distancehand)
            if distancehand > 0.3: # if index finger open
                inverted_x = screen_width - (avg_index_finger_x * 4)
                pyautogui.moveTo(inverted_x*2, avg_index_finger_y*3, 0.1,tween=pyautogui.easeInExpo)

                # Perform a click if the distance between the fingers is below a threshold
                #print(distanceclick)
                if distanceclick < ClickSensetivity:
                    #print("Clicked")
                    pyautogui.mouseDown()
                    time.sleep(0.1)
                    pyautogui.mouseUp()

    cv2.imshow("Image", img)
    cv2.waitKey(1)