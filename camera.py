import cv

class Camera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv.CaptureFromCAM(0)
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = cv.QueryFrame(self.video)
        cv.SaveImage("/dev/shm/frame.jpg", image)
        with open("/dev/shm/frame.jpg") as f:
            return f.read()
