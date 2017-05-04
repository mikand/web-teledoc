#!/usr/bin/env python

import time
import io
import threading
import base64

CV_VER = 2
try:
    import cv2
except ImportError:
    import cv
    CV_VER = 1


class Camera(object):

    def __init__(self, dev_id=0):
        self.dev_id = dev_id
        self.thread = None  # background thread that reads frames from camera
        self.frame = None  # current frame is stored here by background thread
        self.last_access = 0  # time of last client access to the camera

    def initialize(self):
        if self.thread is None:
            # start background frame thread
            self.thread = threading.Thread(target=self._thread)
            self.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        self.last_access = time.time()
        self.initialize()
        return self.frame

    def get_frame_base64(self):
        f = self.get_frame()
        return base64.b64encode(f)

    def _thread(self):
        if CV_VER == 2:
            cam = cv2.VideoCapture(self.dev_id)
            while True:
                if cam.isOpened():
                    success, image = cam.read()
                    if success:
                        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
                        # so we must encode it into JPEG in order to correctly display the
                        # video stream.
                        small = cv2.resize(image, (0,0), fx=0.5, fy=0.5)
                        ret, jpeg = cv2.imencode('.jpg', small)
                        if ret:
                            self.frame = jpeg.tostring()

                    # if there hasn't been any clients asking for frames in
                    # the last 10 seconds stop the thread
                    if time.time() - self.last_access > 10:
                        break
                time.sleep(1.0 / 30.0)
            cam.release()

        else:
            cam = cv.CaptureFromCAM(self.dev_id)
            while True:
                image = cv.QueryFrame(cam)
                cv.SaveImage("/dev/shm/frame.jpg", image)
                with open("/dev/shm/frame.jpg") as f:
                    self.frame = f.read()

                    # if there hasn't been any clients asking for frames in
                    # the last 10 seconds stop the thread
                    if time.time() - self.last_access > 10:
                        break
                time.sleep(1.0 / 30.0)
        self.thread = None


if __name__ == "__main__":
    print("Testing Camera connection...")
    c = Camera()
    print(c.get_frame_base64())
    exit(0)
