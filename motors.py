import time
import atexit
import threading

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
        self.thread = None
        self.movement_authority = 0
        self.current_direction = None
        self.desired_direction = None
        self.current_steering = None
        self.desired_steering = None
        self.speed = 180

    def _thread(self):
        while True:
            if time.time() <= self.movement_authority:
                if self.current_steering != self.desired_steering:
                    if self.desired_steering == "left":
                        self.steering_motor.run(Adafruit_MotorHAT.FORWARD)
                        self.steering_motor.setSpeed(255)
                    elif self.desired_steering == "right":
                        self.steering_motor.run(Adafruit_MotorHAT.BACKWARD)
                        self.steering_motor.setSpeed(255)
                    elif self.desired_steering == "none":
                        self.steering_motor.run(Adafruit_MotorHAT.RELEASE)
                    self.current_steering = self.desired_steering

                if self.current_direction != self.desired_direction:
                    if self.desired_direction == "fwd":
                        self.speed_motor.run(Adafruit_MotorHAT.FORWARD)
                        self.speed_motor.setSpeed(self.speed)
                    elif self.desired_direction == "bwd":
                        self.speed_motor.run(Adafruit_MotorHAT.BACKWARD)
                        self.speed_motor.setSpeed(self.speed)
                    elif self.desired_direction == "none":
                        self.speed_motor.run(Adafruit_MotorHAT.RELEASE)
                    self.current_direction = self.desired_direction
                time.sleep(0.2)
            else:
                self.steering_motor.run(Adafruit_MotorHAT.RELEASE)
                self.speed_motor.run(Adafruit_MotorHAT.RELEASE)
                self.current_direction = None
                self.current_steering = None
                break
        self.thread = None


    def do_step(self, direction, steering, duration, speed=200):
        self.desired_direction = direction
        self.desired_steering = steering
        self.speed = speed
        self.movement_authority = time.time() + duration
        if self.thread is None:
            threading.Thread(target=self._thread)
            self.thread.start()
