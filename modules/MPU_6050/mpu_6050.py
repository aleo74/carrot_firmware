from odb.lib import adafruit_mpu6050
import busio
from odb.modules import Module
import time

class Mpu6050(Module):

    name = 'mpu'
    _time = 0
    acc_x = 0
    acc_y = 0
    acc_z = 0

    gyro_x = 0
    gyro_y = 0
    gyro_z = 0

    temp = 0

    _i2c = None

    def __init__(self, scl, sda, waiting_time=100):
        self._i2c = busio.I2C(scl, sda)
        self.mpu = adafruit_mpu6050.MPU6050(self._i2c)

        self.waiting_time = waiting_time

    def during_bootup(self):
        self.ready = True

    def before_handle(self, data=None):
        self._now = time.time()
        return self._now

    def handle(self, data=None):
        if time.time() < self._now + self.waiting_time :
            self.acc_x, self.acc_y, self.acc_z = self.mpu.acceleration
            self.gyro_x, self.gyro_y, self.gyro_z = self.mpu.gyro
            self.temp = self.mpu.temperature
            data = {
                'acc_x' : self.acc_x, 'acc_y': self.acc_y, 'acc_z' : self.acc_z,
                'gyro_x' :self.gyro_x, 'gyro_y' : self.gyro_y, 'gyro_z' : self.gyro_z,
                'temp' : self.temp
            }
            return data

