import cv2

def FindCameras():
    cameras = []

    for index in range(10):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            cameras.append(index)
            cap.release()

    if not cameras:
        print("ERROR NO CAMERAS CONNECTED!")
    else:
        print("Connected cameras:", [camera + 1 for camera in cameras])
        cam = cameras[-1]
        print("USE CAMERA: ", cam + 1)
        return cam
