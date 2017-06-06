#!/usr/bin/env python

import os.path
import time
import threading
import base64

import pygame
import pygame.camera
from pygame.locals import *

from cStringIO import StringIO
from PIL import Image, ImageDraw, ImageFont
resources_path = os.path.join(os.path.dirname(__file__), "resources")

pygame.camera.init()

DEVICE = '/dev/video%s'
SIZE = (640, 480)

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
        try:
            camera = pygame.camera.Camera(DEVICE % self.dev_id, SIZE)
            camera.start()
            while True:
                surf = camera.get_image()
                data = pygame.image.tostring(surf, 'RGBA')
                img = Image.frombytes('RGBA', SIZE, data)
                buf = StringIO()
                img.save(buf, format='JPEG')
                self.frame = buf.getvalue()

                # if there hasn't been any clients asking for frames in
                # the last 30 seconds stop the thread
                if time.time() - self.last_access > 30:
                    break
                time.sleep(1.0 / 30.0)
            camera.stop()
        except SystemError as ex:
            print(ex)

            x, y = (0, 0)
            font = ImageFont.truetype(os.path.join(resources_path, "Helvetica.ttf"), 35)
            while True:
                x = (x + 1) % 620
                y = (y + 1) % 460
                im = Image.new('RGB', (640, 480))
                draw = ImageDraw.Draw(im)
                draw.ellipse([int(x), int(y), int(x)+20, int(y)+20], fill='white')
                draw.text((310, 100), str(self.dev_id), font=font, fill=(255, 255, 255, 255))
                buf = StringIO()
                im.save(buf, format='JPEG')
                self.frame = buf.getvalue()
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
