#!/usr/bin/env python

import time
import io
import threading
import cv

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
        cam = cv.CaptureFromCAM(0)
        while True:
            image = cv.QueryFrame(cam)
            cv.SaveImage("/dev/shm/frame.jpg", image)
            with open("/dev/shm/frame.jpg") as f:
                cls.frame = f.read()

                # if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread
                if time.time() - cls.last_access > 10:
                    break
            time.sleep(1.0 / 30.0)
        cls.thread = None
