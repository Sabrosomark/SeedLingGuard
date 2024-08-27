import time
import Adafruit_ADS1x15
import smbus
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(40, GPIO.OUT)
GPIO.output(40, GPIO.HIGH)

# Create the I2C bus
i2c_bus_number = 1  # Use 1 for Raspberry Pi 3 and below, 3 for Raspberry Pi 4
i2c = smbus.SMBus(i2c_bus_number)

# Create the ADS object
adc = Adafruit_ADS1x15.ADS1115(busnum=i2c_bus_number)
TDS_SENSOR_PIN = 1

def read_tds(voltage):
    # Adjust the formula based on your specific sensor calibration
    tds_value = voltage * 1000  # Example conversion, adjust as needed
    return tds_value

try:
    while True:
        # Read the analog voltage from the TDS sensor pin
        voltage = adc.read_adc(TDS_SENSOR_PIN) / 1000.0  # Convert to volts
        tds = read_tds(voltage)
        print(f'TDS: {tds:.2f} ppm')

        if tds >= 3000:
            GPIO.output(40, GPIO.LOW)
            print("HIGH SALINITY")
            print("SPRAY LIQUID FERTILIZER")
        else:
            GPIO.output(40, GPIO.HIGH)
            print("LOW SALINITY")

        time.sleep(1)

except KeyboardInterrupt:
    print("Program interrupted by user")

finally:
    GPIO.cleanup()
    print("GPIO cleanup complete")

