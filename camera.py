#!/usr/bin/env python

import time
import io
import threading
import cv2


class Camera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera

    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return self.frame

    @classmethod
    def _thread(cls):
        cam = cv2.VideoCapture(0)
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
                        cls.frame = jpeg.tostring()

                # if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread
                if time.time() - cls.last_access > 10:
                    break
            time.sleep(1.0 / 30.0)
        cam.release()
        cls.thread = None
