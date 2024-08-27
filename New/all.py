import RPi.GPIO as GPIO
import dht11
import time
from time import sleep
import datetime
import busio
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# GPIO Setup
in1 = 24
in2 = 23
en = 25

RELAY1 = 20
RELAY2 = 21

BLINDS_OPEN_PIN = 22
BLINDS_CLOSE_PIN = 27

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(en, GPIO.OUT)
GPIO.setup(RELAY1, GPIO.OUT)
GPIO.setup(RELAY2, GPIO.OUT)
GPIO.setup(BLINDS_OPEN_PIN, GPIO.OUT)
GPIO.setup(BLINDS_CLOSE_PIN, GPIO.OUT)

GPIO.output(in1, GPIO.LOW)
GPIO.output(in2, GPIO.LOW)
p = GPIO.PWM(en, 1000)
p.start(75)

# Read data using pin 17 (BCM numbering)
instance = dht11.DHT11(pin=17)

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADS object
adc = ADS.ADS1115(i2c)

# Create analog inputs for soil moisture and TDS sensors
chan_soil_moisture = AnalogIn(adc, ADS.P3)
chan_tds = AnalogIn(adc, ADS.P0)

# Thresholds for classifications
SOIL_MOISTURE_THRESHOLD = 5
TDS_THRESHOLD = 300

# Temperature thresholds for blinds control
TEMP_THRESHOLD_OPEN = 30
TEMP_THRESHOLD_CLOSE = 20

blinds_status = "CLOSED"  # Initial blinds status

# Function to determine the wet-dry level based on soil moisture
def wet_dry_level(soil_moisture):
    if soil_moisture > SOIL_MOISTURE_THRESHOLD:
        activate_relay(RELAY1)
        return "DRY", soil_moisture
    else:
        deactivate_relay(RELAY1)
        return "WET", soil_moisture

# Function to read TDS value and determine salinity level
def read_tds(voltage):
    if voltage < 300:
        activate_relay(RELAY2)
        return "Low Salinity", voltage
    elif 300 <= voltage <= 800:
        deactivate_relay(RELAY2)
        return "Moderate Salinity", voltage
    else:
        deactivate_relay(RELAY2)
        return "High Salinity", voltage

# Function to calculate average soil moisture over multiple readings
def average_soil_moisture(num_readings):
    total = 0
    for _ in range(num_readings):
        total += chan_soil_moisture.value
        time.sleep(0.1)
    return ((total / num_readings) * 0.0005) - 3

# Function to calculate average TDS voltage over multiple readings
def average_tds_voltage(num_readings):
    total = 0
    for _ in range(num_readings):
        total += chan_tds.voltage
        time.sleep(0.1)
    return (total / num_readings) * 100

# Function to read and average temperature data from DHT11 sensor
def average_DHT11_temperature(num_readings):
    total_temperature = 0
    valid_readings = 0
    while valid_readings < num_readings:
        result = instance.read()
        if result.is_valid():
            total_temperature += (result.temperature * 9/5) + 15
            valid_readings += 1
        time.sleep(0.1)
    return total_temperature / valid_readings

def activate_relay(relay):
    GPIO.output(relay, GPIO.LOW)
    
def deactivate_relay(relay):
    GPIO.output(relay, GPIO.HIGH)

def open_blinds():
    global blinds_status
    if blinds_status != "OPEN":
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        sleep(5)  # Motor runs for 5 seconds to open blinds
        GPIO.output(in1, GPIO.LOW)
        blinds_status = "OPEN"

def close_blinds():
    global blinds_status
    if blinds_status != "CLOSED":
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        sleep(5)  # Motor runs for 5 seconds to close blinds
        GPIO.output(in2, GPIO.LOW)
        blinds_status = "CLOSED"

try:
    print("{:<20} | {:<15} | {:<15} | {:<15} | {:<15} | {:<15} | {:<10}".format("Time", "Soil Moisture", "Moisture Value", "TDS Level", "TDS Value", "Temperature (C)", "Blinds"))
    print("-" * 130)

    while True:
        # Record the current time
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Read the average soil moisture over 5 readings
        avg_soil_moisture = average_soil_moisture(5)

        # Read the average TDS voltage over 5 readings
        avg_tds_voltage = average_tds_voltage(5)

        # Determine the wet-dry level based on the average soil moisture
        soil_moisture_level, soil_moisture_value = wet_dry_level(avg_soil_moisture)

        # Determine TDS level based on the average voltage
        tds_level, tds_value = read_tds(avg_tds_voltage)

        # Read and average temperature data from DHT11 sensor
        temperature = average_DHT11_temperature(5)

        # Control the blinds based on the temperature
        if temperature > TEMP_THRESHOLD_OPEN and blinds_status != "OPEN":
            open_blinds()
        elif temperature < TEMP_THRESHOLD_CLOSE and blinds_status != "CLOSED":
            close_blinds()

        # Print formatted data with timestamp
        print("{:<20} | {:<15} | {:.2f}           | {:<15} | {:.2f}           | {:.2f}           | {:<10}".format(current_time, soil_moisture_level, soil_moisture_value, tds_level, tds_value, temperature, blinds_status))

        time.sleep(1)  # Adjust delay between readings

except KeyboardInterrupt:
    print("Program interrupted by user")

finally:
    GPIO.cleanup()
    print("GPIO cleanup complete")
