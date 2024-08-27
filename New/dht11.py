import RPi.GPIO as GPIO
import dht11
import time
import datetime

# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

# initialize DHT11 sensors
sensor_1 = dht11.DHT11(pin=17)
sensor_2 = dht11.DHT11(pin=18)

try:
    while True:
        # Read from first sensor
        result_1 = sensor_1.read()
        if result_1.is_valid():
            sensor_1_data = "Sensor 1 - Temperature: %-3.1f C" % result_1.temperature
            # sensor_1_data += " Humidity: %-3.1f %%" % result_1.humidity
        else:
            sensor_1_data = "Sensor 1 - Invalid Reading"

        # Read from second sensor
        result_2 = sensor_2.read()
        if result_2.is_valid():
            sensor_2_data = "Sensor 2 - Temperature: %-3.1f C" % result_2.temperature
            # sensor_2_data += " Humidity: %-3.1f %%" % result_2.humidity
        else:
            sensor_2_data = "Sensor 2 - Invalid Reading"

        # Print horizontally
        print(f"{datetime.datetime.now()} | {sensor_1_data} | {sensor_2_data}")

        time.sleep(1)

except KeyboardInterrupt:
    print("Cleanup")
    GPIO.cleanup()
