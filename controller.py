import usb.core
import time

class LauncherController(object):

    def __init__(self):
        self.dev = usb.core.find(idVendor=0x2123, idProduct=0x1010)
        if self.dev is None:
            raise ValueError('Launcher not connected!')

        if self.dev.is_kernel_driver_active(0) is True:
            self.dev.detach_kernel_driver(0)

        self.dev.set_configuration()

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

if __name__ == "__main__":
    print("Demoing Launcher")
    lc = LauncherController()
    for f in [lc.step_up, lc.step_down, lc.step_left, lc.step_right]:
        for i in xrange(10):
            f()
            time.sleep(0.5)
    lc.fire()
