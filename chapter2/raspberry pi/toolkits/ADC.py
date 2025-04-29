"""
ADC module.
func1: read digital output from ADC
func2: convert digital output into resisdance
"""

import spidev
# import time

# Define Variables
# freq = 1  # frequency / sec
pad_channel = 0  # channal of pressure pad

# SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz=1000000


def readADC(channel):
    """
    Read SPI digital output from the MCP3008.
    """
    if channel > 7 or channel < 0:
        return -1
    r = spi.xfer2([1, 8 + channel << 4, 0])
    digital_output = ((r[1] & 3) << 8) + r[2]
    return digital_output


def calR(digital_output, V=3.3, R1=10000):
    """
    calculate resistance of pressure pad according to the digital output
    """
    V_in = digital_output * 3.3 / 1024
    if V_in == 0:
        return float('inf')
    else:
        return (V - V_in) * R1 / V_in

# try:
#     while True:
#         pad_value = readADC(pad_channel)
#         pad_resistance = calR(pad_value)
#         print("---------------------------------------")
#         print("Digital Output: %d; Pad Resistance: %.1f Ω" % (pad_value, pad_resistance))
#         time.sleep(freq)
# except KeyboardInterrupt:
#     pass