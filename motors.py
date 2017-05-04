import time
import atexit

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

def initializeHat():
    mh = Adafruit_MotorHAT(addr=0x60)

    # recommended for auto-disabling motors on shutdown!
    def turnOffMotors():
        for i in range(4):
            mh.getMotor(i+1).run(Adafruit_MotorHAT.RELEASE)
    atexit.register(turnOffMotors)

    return mh




class MotorsController(object):

    mhat = None

    def __init__(self):
        if MotorsController.mhat is None:
            MotorsController.mhat = initializeHat()
        self.speed_motor = MotorsController.mhat.getMotor(1)
        self.steering_motor = MotorsController.mhat.getMotor(2)

    def do_step(self, direction, steering, duration, speed=200):
        if direction == "fwd":
            self.speed_motor.run(Adafruit_MotorHAT.FORWARD)
            self.speed_motor.setSpeed(speed)
        elif direction == "bwd":
            self.speed_motor.run(Adafruit_MotorHAT.BACKWARD)
            self.speed_motor.setSpeed(speed)


        if steering == "left":
            self.steering_motor.run(Adafruit_MotorHAT.FORWARD)
            self.steering_motor.setSpeed(255)
        elif steering == "right":
            self.steering_motor.run(Adafruit_MotorHAT.BACKWARD)
            self.steering_motor.setSpeed(255)

        time.sleep(duration)
