import time
import Adafruit_ADS1x15
import smbus
import RPi.GPIO as GPIO
import matplotlib.pyplot as plt

GPIO.setmode(GPIO.BOARD)
GPIO.setup(40, GPIO.OUT)
GPIO.output(40, GPIO.HIGH)

# Create the I2C bus
i2c_bus_number = 1  # Use 1 for Raspberry Pi 3 and below, 3 for Raspberry Pi 4
i2c = smbus.SMBus(i2c_bus_number)

# Create the ADS object
adc = Adafruit_ADS1x15.ADS1115(busnum=i2c_bus_number)
TDS_SENSOR_PIN = 0

# Initialize lists to store time and TDS readings
time_list = []
tds_list = []

def read_tds(voltage):
    # Adjust the formula based on your specific sensor calibration
    tds_value = voltage * 1000  # Example conversion, adjust as needed
    return tds_value

# Set up the plot
plt.ion()  # Interactive mode on
fig, ax = plt.subplots()
line, = ax.plot([], [], 'r-', label='TDS (ppm)')
ax.set_xlim(0, 10)  # Initial x-axis limit
ax.set_ylim(0, 1000)  # Adjust y-axis limit as needed
ax.set_xlabel('Time (s)')
ax.set_ylabel('TDS (ppm)')
ax.set_title('Real-time TDS Readings')
ax.legend()

start_time = time.time()

try:
    while True:
        # Read the analog voltage from the TDS sensor pin
        voltage = adc.read_adc(TDS_SENSOR_PIN) / 1000.0  # Convert to volts
        tds = (read_tds(voltage)* .005)
        current_time = time.time() - start_time

        print(f'TDS: {tds:.2f} ppm')

        if tds >= 3000:
            GPIO.output(40, GPIO.LOW)
            print("HIGH SALINITY")
            print("SPRAY LIQUID FERTILIZER")
        else:
            GPIO.output(40, GPIO.HIGH)
            print("LOW SALINITY")

        # Update lists with new data
        time_list.append(current_time)
        tds_list.append(tds)

        # Update the plot
        line.set_xdata(time_list)
        line.set_ydata(tds_list)
        ax.relim()
        ax.autoscale_view()

        plt.draw()
        plt.pause(1)  # Pause for the plot to update

        time.sleep(1)

except KeyboardInterrupt:
    print("Program interrupted by user")

finally:
    GPIO.cleanup()
    print("GPIO cleanup complete")
