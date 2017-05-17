import time
import threading

try:
    import usb.core

    class LauncherController(object):

        def __init__(self):
            self.dev = usb.core.find(idVendor=0x2123, idProduct=0x1010)
            if self.dev is None:
                raise ValueError('Launcher not connected!')

            if self.dev.is_kernel_driver_active(0) is True:
                self.dev.detach_kernel_driver(0)

            self.dev.set_configuration()
            self.current_status = "stop"
            self.desired_status = "stop"
            self.movement_authority = 0

            self.thread = None


        def _thread(self):
            while True:
                if time.time() <= self.movement_authority:
                    if self.current_status != self.desired_status:
                        if self.current_status != "stop":
                            self.stop()
                        self.current_status = "stop"
                        if self.desired_status == "stop":
                            self.stop()
                        elif self.desired_status == "left":
                            self.left()
                        elif self.desired_status == "right":
                            self.right()
                        elif self.desired_status == "up":
                            self.up()
                        elif self.desired_status == "down":
                            self.down()
                        self.current_status = self.desired_status
                    time.sleep(0.2)
                else:
                    self.stop()
                    break
            self.thread = None

        def up(self):
            self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x02,0x00,0x00,0x00,0x00,0x00,0x00])

        def down(self):
            self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x01,0x00,0x00,0x00,0x00,0x00,0x00])

        def left(self):
            self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x04,0x00,0x00,0x00,0x00,0x00,0x00])

        def right(self):
            self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x08,0x00,0x00,0x00,0x00,0x00,0x00])

        def stop(self):
            self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x20,0x00,0x00,0x00,0x00,0x00,0x00])

        def fire(self):
            self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x10,0x00,0x00,0x00,0x00,0x00,0x00])

        def step(self, status, duration):
            self.desired_status = status
            self.movement_authority = time.time() + duration
            if self.thread is None:
                self.thread = threading.Thread(target=self._thread)
                self.thread.start()

        def step_up(self, duration=0.05):
            self.step("up", duration)

        def step_down(self, duration=0.05):
            self.step("down", duration)

        def step_left(self, duration=0.05):
            self.step("left", duration)

        def step_right(self, duration=0.05):
            self.step("right", duration)


except ImportError:

    class LauncherController(object):

        def up(self):
            print("RocketLauncher UP!")

        def down(self):
            print("RocketLauncher DOWN!")

        def left(self):
            print("RocketLauncher LEFT!")

        def right(self):
            print("RocketLauncher RIGHT!")

        def stop(self):
            print("RocketLauncher STOP!")

        def fire(self):
            print("RocketLauncher FIRE!")

        def step_up(self):
            self.up()
            time.sleep(0.05)
            self.stop()

        def step_down(self):
            self.down()
            time.sleep(0.05)
            self.stop()

        def step_left(self):
            self.left()
            time.sleep(0.05)
            self.stop()

        def step_right(self):
            self.right()
            time.sleep(0.05)
            self.stop()

        def step(self, command, duration=0.05):
            print("Launcher: doing %s for %s" % (command, duration))

if __name__ == "__main__":
    print("Demoing Launcher")
    lc = LauncherController()
    for f in [lc.step_up, lc.step_down, lc.step_left, lc.step_right]:
        for i in range(10):
            f()
            time.sleep(0.5)
    lc.fire()
