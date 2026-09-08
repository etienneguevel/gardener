import board
import adafruit_bh1750
from adafruit_bme280 import basic as adafruit_bme280


def read_captors() -> tuple[float, float, float]:

    i2c = board.I2C()  # uses board.SCL and board.SDA
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    bh1750 = adafruit_bh1750.BH1750(i2c)

    return bme280.temperature, bme280.humidity, bh1750.lux

