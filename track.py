
import cv2
import numpy as np
from google.colab.patches import cv2_imshow
from IPython.display import display, Javascript


def start_webcam():
    display(Javascript("""
        const video = document.createElement('video');
        video.width = 640;
        video.height = 480;
        document.body.appendChild(video);

        const stream = await navigator.mediaDevices.getUserMedia({video: true});
        video.srcObject = stream;
        video.play();

        window.videoElement = video;  
    """))


start_webcam()


def capture_webcam_frame():
    import time
    time.sleep(2)  

    while True:
        
        frame = None
        try:
            frame = cv2.VideoCapture(0).read()[1]  
        except Exception as e:
            print("Error capturing frame:", e)

        if frame is not None:
            
            cv2_imshow(frame)

        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


capture_webcam_frame()