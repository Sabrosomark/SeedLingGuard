import time
import Adafruit_ADS1x15
import smbus
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)  # Using BCM pin 21 instead of BOARD pin 40
GPIO.output(21, GPIO.HIGH)
GPIO.setup(20, GPIO.OUT)  # Using BCM pin 20 instead of BOARD pin 38
GPIO.output(20, GPIO.HIGH)

# Create the I2C bus
i2c_bus_number = 1  # Use 1 for Raspberry Pi 3 and below, 3 for Raspberry Pi 4
i2c = smbus.SMBus(i2c_bus_number)

# Create the ADS object
adc = Adafruit_ADS1x15.ADS1115(busnum=i2c_bus_number)

# Define the TDS sensor pins
TDS_SENSOR_PIN_1 = 1
TDS_SENSOR_PIN_2 = 2

def read_tds(voltage):
    # Adjust the formula based on your specific sensor calibration
    tds_value = voltage * 1000  # Example conversion, adjust as needed
    return tds_value

try:
    while True:
        # Read the analog voltage from the first TDS sensor pin
        voltage_1 = adc.read_adc(TDS_SENSOR_PIN_1) / 1000.0 * 0.0005  # Convert to volts
        tds_1 = read_tds(voltage_1)

        # Read the analog voltage from the second TDS sensor pin
        voltage_2 = adc.read_adc(TDS_SENSOR_PIN_2) / 1000.0 * 0.0005  # Convert to volts
        tds_2 = read_tds(voltage_2)

        # Display the TDS values and status horizontally
        status_1 = "HIGH SALINITY - SPRAY LIQUID FERTILIZER" if tds_1 >= 3000 else "LOW SALINITY"
        status_2 = "HIGH SALINITY - SPRAY LIQUID FERTILIZER" if tds_2 >= 3000 else "LOW SALINITY"

        print(f'TDS Sensor 1: {tds_1:.2f} ppm ({status_1}) | TDS Sensor 2: {tds_2:.2f} ppm ({status_2})')

        # Set the GPIO outputs based on the TDS levels
        GPIO.output(21, GPIO.LOW if tds_1 >= 3000 else GPIO.HIGH)
        GPIO.output(20, GPIO.LOW if tds_2 >= 3000 else GPIO.HIGH)

        time.sleep(1)

except KeyboardInterrupt:
    print("Program interrupted by user")

finally:
    GPIO.cleanup()
    print("GPIO cleanup complete")
