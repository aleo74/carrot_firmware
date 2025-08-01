from odb.lib import adafruit_mpu6050
import busio, time
from odb.modules import Module

_GRAVITY = 9.80665          # pour convertir m/s² → g si besoin
_ALPHA = 0.08               # coefficient du filtre passe-bas gyro

class Mpu6050(Module):
    name = "mpu"


    def __init__(self, scl, sda, waiting_time=100):
        self.i2c   = busio.I2C(scl, sda)
        self.mpu   = adafruit_mpu6050.MPU6050(self.i2c)
        self.waiting_time = waiting_time / 1000   # → secondes
        self._next_due = 0
        self.ready = False       # flag connu du scheduler

    def during_bootup(self):
        bias = [0.0, 0.0, 0.0]
        for _ in range(500):            # ~1/2 s à 1 kHz
            gx, gy, gz = self.mpu.gyro
            bias[0] += gx; bias[1] += gy; bias[2] += gz
        self.bias = [b / 500 for b in bias]

        # init filtre passe-bas avec la 1ʳᵉ valeur « offsettée »
        g0 = [g - b for g, b in zip(self.mpu.gyro, self.bias)]
        self._gxf, self._gyf, self._gzf = g0
        self.ready = True

    def before_handle(self, data=None):
        self._now = time.time()
        return self._now

    def handle(self, data=None):
        if self._now < self._next_due:          # respect de la cadence
            return None

        # ---- lecture brute ----
        ax, ay, az = self.mpu.acceleration      # m/s²
        gx_raw, gy_raw, gz_raw = self.mpu.gyro  # °/s
        temp = self.mpu.temperature

        # ---- compensation offset ----
        gx = gx_raw - self.bias[0]
        gy = gy_raw - self.bias[1]
        gz = gz_raw - self.bias[2]

        # ---- filtre passe-bas (anti-gigue) ----
        self._gxf = _ALPHA*gx + (1-_ALPHA)*self._gxf
        self._gyf = _ALPHA*gy + (1-_ALPHA)*self._gyf
        self._gzf = _ALPHA*gz + (1-_ALPHA)*self._gzf
        gx, gy, gz = self._gxf, self._gyf, self._gzf

        # ---- prochaine échéance ----
        self._next_due = self._now + self.waiting_time

        return {
            "acc_x": ax, "acc_y": ay, "acc_z": az,
            "gyro_x": gx, "gyro_y": gy, "gyro_z": gz,
            "temp": temp
        }
