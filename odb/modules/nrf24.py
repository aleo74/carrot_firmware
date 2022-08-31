from odb.lib.circuitpython_nrf24l01.rf24 import RF24
import busio
from odb.modules import Module
import digitalio
import json


#FIXME
class Nfr24(Module):

    name = 'nrf24'
    address = [b"1Node", b"2Node"]

    def __init__(self, CE, CSN, CLK, MOSI, MISO, PA_LEVEL = -12):
        self.ce = digitalio.DigitalInOut(CE)
        self.csn = digitalio.DigitalInOut(CSN)
        self.spi = busio.SPI(clock=CLK, MOSI=MOSI, MISO=MISO)
        self.pa_level = PA_LEVEL

    def during_bootup(self):
        # initialize the nRF24L01 on the spi bus object
        self.nrf = RF24(self.spi, self.csn, self.ce)
        self.nrf.pa_level = self.pa_level
        self.nrf.open_tx_pipe(self.address[0])
        self.nrf.listen = False
        self.nrf.ack = True
        self.ready = True
        self.send_data({'state': 'booting'})

    def before_handle(self, data=None):
        received_data = []
        return {'received': received_data}

    def handle(self, data=None):

        return None

    def after_handle(self, data=None):
        receveid = self.send_data(data)
        if receveid:
            return receveid

    def make_buffers(self, size):
        """return a list of payloads"""
        buffers = []

        for i in range(0, len(size) - 1, 32):  # range(start, end, step)
            buffers.append(b"" + size[i:i + 32])
        return buffers

    def send_data(self, data=None):
        """Transmits multiple payloads using `RF24.send()` and `RF24.resend()`."""
        buffers = self.make_buffers(json.dumps(data))  # make a list of payloads
        received_data = ''
        counter = [0]
        result = self.nrf.send(buffers)#, force_retry=1)  # result is a list
        if result:
                if not isinstance(result[0], bool):
                # result[:6] truncates c-string NULL termiating char
                # received counter is a unsigned byte, thus result[7:8][0]
                    received_data = json.loads(result[0].decode("utf-8"))
        return received_data
