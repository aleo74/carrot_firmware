import board
from odb.odb_firmware import Odb
from odb.modules.mpu_6050 import Mpu6050
from odb.modules.gps import Gps
from odb.modules.nrf24 import Nfr24
from odb.modules.servo import Servo


mpu = Mpu6050(board.GP27, board.GP26, 10000)
gps = Gps(board.GP8, board.GP5,baudrate=9600, timeout=30, debug=False)
nrf24 = Nfr24(board.GP15, board.GP1, board.GP2, board.GP3, board.GP4)
servo = Servo()
my_odb = Odb()
# Odb.modules = [mpu, test]
# Odb.modules = [mpu, nrf24, gps]
Odb.modules = [mpu, nrf24, servo]
# Odb.modules = [nrf24]

if __name__ == '__main__':
	my_odb.go()
'''
"""
Simple example of using the library to transmit
and retrieve custom automatic acknowledgment payloads.
"""
import time
import board
from digitalio import DigitalInOut
import busio
from odb.lib.circuitpython_nrf24l01.rf24 import RF24
# if running this on a ATSAMD21 M0 based board
# from circuitpython_nrf24l01.rf24_lite import RF24


# invalid default values for scoping
SPI_BUS, CSN_PIN, CE_PIN = (None, None, None)

try:  # on Linux
    import spidev

    SPI_BUS = spidev.SpiDev()  # for a faster interface on linux
    CSN_PIN = 0  # use CE0 on default bus (even faster than using any pin)
    CE_PIN = DigitalInOut(board.D22)  # using pin gpio22 (BCM numbering)

except ImportError:  # on CircuitPython only
    # using board.SPI() automatically selects the MCU's
    # available SPI pins, board.SCK, board.MOSI, board.MISO
    SPI_BUS = busio.SPI(clock=board.GP2, MOSI=board.GP3, MISO=board.GP4)

    # change these (digital output) pins accordingly
    CE_PIN = DigitalInOut(board.GP15)
    CSN_PIN = DigitalInOut(board.GP1)


# initialize the nRF24L01 on the spi bus object
nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)
# On Linux, csn value is a bit coded
#                 0 = bus 0, CE0  # SPI bus 0 is enabled by default
#                10 = bus 1, CE0  # enable SPI bus 2 prior to running this
#                21 = bus 2, CE1  # enable SPI bus 1 prior to running this

# the custom ACK payload feature is disabled by default
# NOTE the the custom ACK payload feature will be enabled
# automatically when you call load_ack() passing:
# a buffer protocol object (bytearray) of
# length ranging [1,32]. And pipe number always needs
# to be an int ranging [0, 5]

# to enable the custom ACK payload feature
nrf.ack = True  # False disables again

# set the Power Amplifier level to -12 dBm since this test example is
# usually run with nRF24L01 transceivers in close proximity
nrf.pa_level = -12

# addresses needs to be in a buffer protocol object (bytearray)
address = [b"1Node", b"2Node"]

# to use different addresses on a pair of radios, we need a variable to
# uniquely identify which address this radio will use to transmit
# 0 uses address[0] to transmit, 1 uses address[1] to transmit
radio_number = 0

# set TX address of RX node into the TX pipe
nrf.open_tx_pipe(address[radio_number])  # always uses pipe 0

# set RX address of TX node into an RX pipe

# using the python keyword global is bad practice. Instead we'll use a 1 item
# list to store our integer number for the payloads' counter
counter = [0]


def master(count=5):  # count = 5 will only transmit 5 packets
    """Transmits a payload every second and prints the ACK payload"""
    nrf.listen = False  # put radio in TX mode

    while count:
        # construct a payload to send
        # add b"\0" as a c-string NULL terminating char
        buffer = b"Hello \0" + bytes([counter[0]])
        start_timer = time.monotonic_ns()  # start timer
        result = nrf.send(buffer)  # save the response (ACK payload)
        end_timer = time.monotonic_ns()  # stop timer
        if result:
            # print the received ACK that was automatically
            # fetched and saved to "result" via send()
            # print timer results upon transmission success
            print(
                "Transmission successful! Time to transmit:",
                int((end_timer - start_timer) / 1000),
                "us. Sent: {}{}".format(buffer[:6].decode("utf-8"), counter[0]),
                end=" ",
            )
            if isinstance(result, bool):
                print("Received an empty ACK packet")
            else:
                # result[:6] truncates c-string NULL termiating char
                # received counter is a unsigned byte, thus result[7:8][0]
                print(
                    "Received: {}{}".format(result[:6].decode("utf-8"), result[7:8][0])
                )
            counter[0] += 1  # increment payload counter
        elif not result:
            print("send() failed or timed out")
        time.sleep(1)  # let the RX node prepare a new ACK payload
        count -= 1


def set_role():
    """Set the role using stdin stream. Timeout arg for slave() can be
    specified using a space delimiter (e.g. 'R 10' calls `slave(10)`)
    """
    user_input = "T"
    if user_input[0].upper().startswith("T"):
        master(*[int(x) for x in user_input[1:2]])
        return True



print("    nRF24L01 ACK Payload test")

if __name__ == "__main__":
    try:
        while set_role():
            pass  # continue example until 'Q' is entered
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
else:
    print("    Run slave() on receiver\n    Run master() on transmitter")
'''