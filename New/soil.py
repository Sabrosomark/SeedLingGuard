import time
import Adafruit_ADS1x15
import smbus
import RPi.GPIO as GPIO

# Use BCM GPIO references instead of physical pin numbers
GPIO.setmode(GPIO.BCM)
# Set up GPIO 21 as an output (Pin 40 in BOARD mode is GPIO 21 in BCM mode)
GPIO.setup(21, GPIO.OUT)
GPIO.output(21, GPIO.HIGH)

# Initialize I2C bus number (usually 1 on Raspberry Pi)
i2c_bus_number = 1
i2c = smbus.SMBus(i2c_bus_number)

# Create an ADS1115 ADC object
adc = Adafruit_ADS1x15.ADS1115(busnum=i2c_bus_number)

# Set the gain to ±4.096V (adjust if needed)
GAIN = 1

# Single threshold for wet/dry classification (adjust as needed)
THRESHOLD = 21000

# Function to determine the wet-dry level based on the soil moisture
def wet_dry_level(soil_moisture):
    if soil_moisture > THRESHOLD:
        return "DRY"
    else:
        return "WET"

# Main loop to read the analog values from the soil moisture sensors
try:
    while True:
        # Read the raw analog values from channel A2 and A3
        raw_value_1 = adc.read_adc(2, gain=GAIN)
        raw_value_2 = adc.read_adc(3, gain=GAIN)

        # Determine the wet-dry level based on the raw ADC values
        level_1 = wet_dry_level(raw_value_1)
        level_2 = wet_dry_level(raw_value_2)

        # Print the results
        print("Sensor 1 (P2) - Raw Value: {} \t Level: {}".format(raw_value_1, level_1))
        print("Sensor 2 (P3) - Raw Value: {} \t Level: {}".format(raw_value_2, level_2))

        # Check if either sensor indicates that the soil is dry enough to trigger water spraying
        if raw_value_1 > THRESHOLD or raw_value_2 > THRESHOLD:
            GPIO.output(21, GPIO.LOW)
            print("Spray Water")
        else:
            GPIO.output(21, GPIO.HIGH)  # Turn off water spraying if both are wet

        # Add a delay between readings (adjust as needed)
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
