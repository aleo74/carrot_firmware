from odb.lib.circuitpython_nrf24l01.rf24 import RF24
import busio, digitalio, json
from odb.modules import Module
import time

class Nrf24(Module):
    name = "nrf24"
    address = [b"1Node", b"2Node"]

    def __init__(self, CE, CSN, CLK, MOSI, MISO, pa_level=-12):
        self.ce  = digitalio.DigitalInOut(CE)
        self.csn = digitalio.DigitalInOut(CSN)
        self.spi = busio.SPI(clock=CLK, MOSI=MOSI, MISO=MISO)
        self.pa_level = pa_level
        self.tx_queue = []          #  ← file d’attente des messages à émettre


    def during_bootup(self):
        # initialize the nRF24L01 on the spi bus object
        self.nrf = RF24(self.spi, self.csn, self.ce)
        self.nrf.pa_level = self.pa_level
        self.nrf.open_tx_pipe(self.address[0])
        self.nrf.listen  = False
        self.nrf.ack     = True
        self.ready = True
        self.enqueue({"state": "booting"})

    def enqueue(self, payload: dict) -> None:
        """Ajoute un message JSON (dict) à la file d’envoi."""
        self.tx_queue.append(payload)

    def _drain_fifo(self):
        """Vide le FIFO RX et retourne une liste de paquets décodés."""
        packets = []
        while self.nrf.any():
            raw = self.nrf.recv()
            try:
                packets.append(json.loads(raw.decode("utf-8")))
            except Exception:        # paquet non-JSON
                packets.append({"raw": list(raw)})
        return packets

    def _make_buffers(self, txt: str):
        """Découpe une chaîne en segments ≤32 octets pour nRF24."""
        return [txt[i : i + 32].encode() for i in range(0, len(txt), 32)]

    def _send_one(self, obj: dict):
        """Encode + envoie un seul objet JSON."""
        buffers = self._make_buffers(json.dumps(obj))
        self.nrf.send(buffers)

    def before_handle(self, data=None):
        # aucune donnée produite à cette étape
        return None

    def handle(self, data=None):
        # rien de périodique à faire : tout est géré dans after_handle()
        return None

    def after_handle(self, data=None):
        # 1) émettre les messages en attente (au plus un par boucle)
        if self.tx_queue:
            self._send_one(self.tx_queue.pop(0))

        # 2) rendre disponibles les paquets reçus
        packets = self._drain_fifo()
        if packets:
            last = packets[-1]
            return {"rf_packets": last}   # clé consommable par les autres
        return None

    def make_buffers(self, size):
        buffers = []

        for i in range(0, len(size) - 1, 32):  # range(start, end, step)
            buffers.append(b"" + size[i:i + 32])
        return buffers

    def send_data(self, data=None):
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
