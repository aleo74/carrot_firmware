from odb.lib import adafruit_gps
import busio
from odb.modules import Module
import time

class Gps(Module):

    name='GPS'

    talkers = {
        "GA": "Galileo",
        "GB": "BeiDou",
        "GI": "NavIC",
        "GL": "GLONASS",
        "GP": "GPS",
        "GQ": "QZSS",
        "GN": "GNSS",
    }

    latitute = 0
    longitude = 0
    altitude_m = 0
    PDOP = 0
    HDOP = 0
    VDOP = 0
    sat_fix = 0

    ready = False

    def __init__(self, rx, tx, baudrate=9600, timeout=30, debug=False):
        uart = busio.UART(rx, tx, baudrate=baudrate, timeout=timeout)
        self.gps = adafruit_gps.GPS(uart, debug)
        self.gps.send_command(b'PMTK220,500')
        self.gps.send_command(b'PMTK314,1,1,5,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0')


    def during_bootup(self, *args, **kwargs):
        if not self.gps.update() or not self.gps.has_fix:
            time.sleep(0.1)
            print('fixing...')
        else:
            print('fixed')
            self.ready = True

    def before_handle(self, *args, **kwargs):
        self.gps.update()


    def handle(self, *args, **kwargs):
        if self.ready:
            local_time = time.time()
            self.longitude = self.gps.longitude
            self.latitude = self.gps.latitude
            self.altitude_m = self.gps.altitude_m
            if self.gps.nmea_sentence[3:6] == "GSA":
                self.PDOP = self.format_dop(self.gps.pdop)
                self.HDOP = self.format_dop(self.gps.hdop)
                self.VDOP = self.format_dop(self.gps.vdop)
                self.sat_fix = len(self.gps.sat_prns)
            return {
                'time': local_time,
                'longitude': self.longitude,
                'latitude': self.latitude,
                'altitude_m': self.altitude_m,
                '2D_fix': self.gps.has_fix,
                '3D_fix': self.gps.has_3d_fix,
                'PDOP': self.PDOP,
                'HDOP': self.HDOP,
                'VDOP': self.VDOP,
                'sat_fix': self.sat_fix,
            }
        else:
            return {}


    def format_dop(self, dop):
        # https://en.wikipedia.org/wiki/Dilution_of_precision_(navigation)
        if dop > 20:
            msg = "Poor"
        elif dop > 10:
            msg = "Fair"
        elif dop > 5:
            msg = "Moderate"
        elif dop > 2:
            msg = "Good"
        elif dop > 1:
            msg = "Excellent"
        else:
            msg = "Ideal"
        return f"{dop} - {msg}"

