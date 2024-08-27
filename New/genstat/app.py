from flask import Flask, jsonify, render_template
import RPi.GPIO as GPIO
import dht11
import time
from time import sleep
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import logging

app = Flask(__name__)

# Initialize I2C and ADC
i2c = busio.I2C(board.SCL, board.SDA)
adc = ADS.ADS1115(i2c)

# GPIO Setup (Ensure this matches your hardware setup)
in1 = 24
in2 = 23
en = 25
in3 = 5  # Define actual pin number
in4 = 6  # Define actual pin number
en2 = 13  # Define actual pin number
RELAY1 = 20
RELAY2 = 21
BLINDS_OPEN_PIN = 22
BLINDS_CLOSE_PIN = 27
DHT11_PIN1 = 17
DHT11_PIN2 = 18

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Initialize GPIO and other hardware components
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(en, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
GPIO.setup(en2, GPIO.OUT)
GPIO.setup(RELAY1, GPIO.OUT)
GPIO.setup(RELAY2, GPIO.OUT)
GPIO.setup(BLINDS_OPEN_PIN, GPIO.OUT)
GPIO.setup(BLINDS_CLOSE_PIN, GPIO.OUT)
GPIO.output(in1, GPIO.LOW)
GPIO.output(in2, GPIO.LOW)
GPIO.output(in3, GPIO.LOW)
GPIO.output(in4, GPIO.LOW)
p = GPIO.PWM(en, 1000)
p.start(100)
p2 = GPIO.PWM(en2, 1000)
p2.start(100)

# Create analog inputs for soil moisture and TDS sensors
try:
    chan_soil_moisture1 = AnalogIn(adc, ADS.P2)
    chan_soil_moisture2 = AnalogIn(adc, ADS.P3)  # Second soil moisture sensor
    chan_tds = AnalogIn(adc, ADS.P0)
    chan_tds2 = AnalogIn(adc, ADS.P1)  # Second TDS sensor
except Exception as e:
    logging.error(f"Error initializing analog inputs: {e}")

# Initialize DHT11 sensor instances
dht11_instance1 = dht11.DHT11(pin=DHT11_PIN1)
dht11_instance2 = dht11.DHT11(pin=DHT11_PIN2)

# Thresholds for classifications
SOIL_MOISTURE_THRESHOLD = 5
TDS_LOW_THRESHOLD = 200
TDS_MODERATE_THRESHOLD = 800

# Temperature thresholds for blinds control
TEMP_THRESHOLD_OPEN = 29
TEMP_THRESHOLD_CLOSE = 31

blinds_status_left = "OPEN"  # Initial left blinds status
blinds_status_right = "OPEN"  # Initial right blinds status
water_pump_status = "IDLE"  # Initial water pump status
fertilizer_pump_status = "IDLE"  # Initial liquid fertilizer pump status

# Function to determine wet-dry level based on soil moisture
def wet_dry_level(soil_moisture):
    if soil_moisture > SOIL_MOISTURE_THRESHOLD:
        activate_relay(RELAY1)
        return "DRY", soil_moisture
    else:
        deactivate_relay(RELAY1)
        return "WET", soil_moisture

# Function to read TDS value and determine salinity level
def read_tds(voltage):
    if voltage < TDS_LOW_THRESHOLD:
        activate_relay(RELAY2)
        return "Low Salinity", voltage
    elif TDS_LOW_THRESHOLD <= voltage <= TDS_MODERATE_THRESHOLD:
        deactivate_relay(RELAY2)
        return "Moderate Salinity", voltage
    else:
        deactivate_relay(RELAY2)
        activate_relay(RELAY1)
        return "High Salinity", voltage

# Function to calculate average soil moisture over multiple readings
def average_soil_moisture(channel, num_readings):
    total = 0
    for _ in range(num_readings):
        total += channel.value
        time.sleep(0.1)
    avg_moisture = ((total / num_readings) * 0.0005) - 4
    return avg_moisture

# Function to calculate average TDS voltage over multiple readings
def average_tds_voltage(num_readings, channel):
    total = 0
    for _ in range(num_readings):
        total += channel.voltage
        time.sleep(0.1)
    return (total / num_readings) * 100

# Function to read and return current temperature data from DHT11 sensor
def current_DHT11_temperature(sensor_instance):
    result = sensor_instance.read()
    while not result.is_valid():
        result = sensor_instance.read()
        time.sleep(1)  # Adjust sleep time as needed
    return (result.temperature) + 15  # Correctly return the temperature without additional conversion

def activate_relay(relay):
    GPIO.output(relay, GPIO.LOW)

def deactivate_relay(relay):
    GPIO.output(relay, GPIO.HIGH)

def open_left_blind():
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    p.ChangeDutyCycle(100)
    sleep(1)  # Motor runs for 1.5 seconds to open left blind
    GPIO.output(in1, GPIO.LOW)

def close_left_blind():
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.HIGH)
    p.ChangeDutyCycle(100)
    sleep(1)  # Motor runs for 1.4 seconds to close left blind
    GPIO.output(in2, GPIO.LOW)

def open_right_blind():
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)
    p2.ChangeDutyCycle(100)
    sleep(1)  # Motor runs for 1.5 seconds to open right blind
    GPIO.output(in3, GPIO.LOW)

def close_right_blind():
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.HIGH)
    p2.ChangeDutyCycle(100)
    sleep(1)  # Motor runs for 1.4 seconds to close right blind
    GPIO.output(in4, GPIO.LOW)

def read_sensors():
    try:
        avg_moisture1 = average_soil_moisture(chan_soil_moisture1, 5)
        avg_moisture2 = average_soil_moisture(chan_soil_moisture2, 5)
        avg_tds_voltage = average_tds_voltage(5, chan_tds)
        avg_tds_voltage2 = average_tds_voltage(5, chan_tds2) * 2
        current_temperature1 = current_DHT11_temperature(dht11_instance1)
        current_temperature2 = current_DHT11_temperature(dht11_instance2)
    except Exception as e:
        logging.error(f"Failed to read sensors: {e}")
        return None, None, None, None, None, None
    return avg_moisture1, avg_moisture2, avg_tds_voltage, avg_tds_voltage2, current_temperature1, current_temperature2

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sensor_data')
def sensor_data():
    avg_soil_moisture1, avg_soil_moisture2, avg_tds_voltage, avg_tds_voltage2, current_temperature1, current_temperature2 = read_sensors()

    if avg_soil_moisture1 is None or avg_soil_moisture2 is None or avg_tds_voltage is None or avg_tds_voltage2 is None or current_temperature1 is None or current_temperature2 is None:
        return jsonify({"error": "Failed to read sensor data"}), 500

    soil_moisture_level1, soil_moisture_value1 = wet_dry_level(avg_soil_moisture1)
    soil_moisture_level2, soil_moisture_value2 = wet_dry_level(avg_soil_moisture2)
    tds_level1, tds_value1 = read_tds(avg_tds_voltage)
    tds_level2, tds_value2 = read_tds(avg_tds_voltage2)

    # Control the blinds based on the temperature of both sensors
    control_blinds(current_temperature1, current_temperature2)

    global water_pump_status, fertilizer_pump_status

    # Adjust water pump status based on soil moisture readings
    if soil_moisture_level1 == 'WET' and soil_moisture_level2 == 'WET':
        deactivate_relay(RELAY1)  # Ensure water pump relay is off
        water_pump_status = "IDLE"
    elif soil_moisture_level1 == 'DRY' or soil_moisture_level2 == 'DRY':
        activate_relay(RELAY1)  # Ensure water pump relay is on
        water_pump_status = "DISPENSING"
    else:
        deactivate_relay(RELAY1)  # Ensure water pump relay is off
        water_pump_status = "IDLE"

    # Adjust fertilizer pump status based on TDS readings
    if tds_level1 == 'Moderate Salinity' and tds_level2 == 'Moderate Salinity':
        deactivate_relay(RELAY2)  # Ensure fertilizer pump relay is off
        fertilizer_pump_status = "IDLE"
    elif tds_level1 == 'Low Salinity' or tds_level2 == 'Low Salinity':
        activate_relay(RELAY2)  # Ensure fertilizer pump relay is on
        fertilizer_pump_status = "DISPENSING"
    else:
        deactivate_relay(RELAY2)  # Ensure fertilizer pump relay is off
        fertilizer_pump_status = "IDLE"

    # Determine temperature status
    temperature_status1 = "Critical"
    temperature_status2 = "Critical"
    if current_temperature1 < 20:
        temperature_status1 = "COOL"
    elif 20 <= current_temperature1 <= 30:
        temperature_status1 = "Normal"
    if current_temperature2 < 20:
        temperature_status2 = "COOL"
    elif 20 <= current_temperature2 <= 30:
        temperature_status2 = "Normal"

    # Determine status for all sensor 1 data (Status Left)
    status_left = "SUBOPTIMAL"
    if (
        temperature_status1 == "Normal" and
        soil_moisture_level1 == "WET" and
        tds_level1 == "Moderate Salinity"
    ):
        status_left = "OPTIMAL"
    elif (
        temperature_status1 == "Critical" or
        soil_moisture_level1 == "DRY" or
        tds_level1 in ["Low Salinity", "High Salinity"]
    ):
        status_left = "SUBOPTIMAL"

    # Determine status for all sensor 2 data (Status Right)
    status_right = "SUBOPTIMAL"
    if (
        temperature_status2 == "Normal" and
        soil_moisture_level2 == "WET" and
        tds_level2 == "Moderate Salinity"
    ):
        status_right = "OPTIMAL"
    elif (
        temperature_status2 == "Critical" or
        soil_moisture_level2 == "DRY" or
        tds_level2 in ["Low Salinity", "High Salinity"]
    ):
        status_right = "SUBOPTIMAL"

    data = {
        'temperature1': current_temperature1,
        'temperature2': current_temperature2,
        'temperature_status1': temperature_status1,
        'temperature_status2': temperature_status2,
        'soil_moisture_level1': soil_moisture_level1,
        'soil_moisture_value1': soil_moisture_value1,
        'soil_moisture_level2': soil_moisture_level2,
        'soil_moisture_value2': soil_moisture_value2,
        'tds_level1': tds_level1,
        'tds_value1': tds_value1,
        'tds_level2': tds_level2,
        'tds_value2': tds_value2,
        'blinds_status_left': blinds_status_left,
        'blinds_status_right': blinds_status_right,
        'water_pump_status': water_pump_status,
        'fertilizer_pump_status': fertilizer_pump_status,
        'status_left': status_left,
        'status_right': status_right
    }

    return jsonify(data)

def control_blinds(temperature1, temperature2):
    global blinds_status_left, blinds_status_right

    if temperature1 > TEMP_THRESHOLD_CLOSE:
        if blinds_status_left != "CLOSED":
            close_left_blind()
            blinds_status_left = "CLOSED"
    elif temperature1 < TEMP_THRESHOLD_OPEN:
        if blinds_status_left != "OPEN":
            open_left_blind()
            blinds_status_left = "OPEN"

    if temperature2 > TEMP_THRESHOLD_CLOSE:
        if blinds_status_right != "CLOSED":
            close_right_blind()
            blinds_status_right = "CLOSED"
    elif temperature2 < TEMP_THRESHOLD_OPEN:
        if blinds_status_right != "OPEN":
            open_right_blind()
            blinds_status_right = "OPEN"


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        logging.info("Program interrupted by user")
    finally:
        GPIO.cleanup()
        logging.info("GPIO cleanup complete")
