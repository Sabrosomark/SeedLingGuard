import RPi.GPIO as GPIO
import time

# Define BCM GPIO pins connected to the relay module
RELAY1 = 20  # Corresponds to physical pin 38
RELAY2 = 21  # Corresponds to physical pin 40

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY1, GPIO.OUT)
GPIO.setup(RELAY2, GPIO.OUT)


def activate_relay(relay):
    GPIO.output(relay, GPIO.LOW)

def deactivate_relay(relay):
    GPIO.output(relay, GPIO.HIGH)

try:
    while True:
        # Activate each relay in sequence
        activate_relay(RELAY1)
        time.sleep(2)
        deactivate_relay(RELAY1)

        activate_relay(RELAY2)
        time.sleep(2)
        deactivate_relay(RELAY2)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()

