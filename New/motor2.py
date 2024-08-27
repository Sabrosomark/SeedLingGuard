import RPi.GPIO as GPIO          
from time import sleep

# Motor 1 pins
in1 = 24
in2 = 23
en = 25

# Motor 2 pins
in3 = 5
in4 = 6
en2 = 13

temp1 = 1
temp2 = 1

# Setup GPIO
GPIO.setmode(GPIO.BCM)

# Motor 1 setup
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(en, GPIO.OUT)
GPIO.output(in1, GPIO.LOW)
GPIO.output(in2, GPIO.LOW)
p1 = GPIO.PWM(en, 1000)
p1.start(100)

# Motor 2 setup
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
GPIO.setup(en2, GPIO.OUT)
GPIO.output(in3, GPIO.LOW)
GPIO.output(in4, GPIO.LOW)
p2 = GPIO.PWM(en2, 1000)
p2.start(100)

print("\n")
print("The default speed & direction of motors is LOW & Forward.....")
print("r1-run Motor 1 r2-run Motor 2")
print("s1-stop Motor 1 s2-stop Motor 2")
print("f1-forward Motor 1 f2-forward Motor 2")
print("b1-backward Motor 1 b2-backward Motor 2")
print("l1-low Motor 1 l2-low Motor 2")
print("m1-medium Motor 1 m2-medium Motor 2")
print("h1-high Motor 1 h2-high Motor 2")
print("e-exit")
print("\n")    

while True:

    x = input()
    
    # Motor 1 controls
    if x == 'r1':
        print("run Motor 1")
        if temp1 == 1:
            GPIO.output(in1, GPIO.HIGH)
            GPIO.output(in2, GPIO.LOW)
            print("Motor 1 forward")
        else:
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.HIGH)
            print("Motor 1 backward")
        x = 'z'

    elif x == 's1':
        print("stop Motor 1")
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        x = 'z'

    elif x == 'f1':
        print("forward Motor 1")
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        temp1 = 1
        x = 'z'

    elif x == 'b1':
        print("backward Motor 1")
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        temp1 = 0
        x = 'z'

    elif x == 'l1':
        print("low Motor 1")
        p1.ChangeDutyCycle(25)
        x = 'z'

    elif x == 'm1':
        print("medium Motor 1")
        p1.ChangeDutyCycle(50)
        x = 'z'

    elif x == 'h1':
        print("high Motor 1")
        p1.ChangeDutyCycle(75)
        x = 'z'
    
    # Motor 2 controls
    elif x == 'r2':
        print("run Motor 2")
        if temp2 == 1:
            GPIO.output(in3, GPIO.HIGH)
            GPIO.output(in4, GPIO.LOW)
            print("Motor 2 forward")
        else:
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.HIGH)
            print("Motor 2 backward")
        x = 'z'

    elif x == 's2':
        print("stop Motor 2")
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.LOW)
        x = 'z'

    elif x == 'f2':
        print("forward Motor 2")
        GPIO.output(in3, GPIO.HIGH)
        GPIO.output(in4, GPIO.LOW)
        temp2 = 1
        x = 'z'

    elif x == 'b2':
        print("backward Motor 2")
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.HIGH)
        temp2 = 0
        x = 'z'

    elif x == 'l2':
        print("low Motor 2")
        p2.ChangeDutyCycle(25)
        x = 'z'

    elif x == 'm2':
        print("medium Motor 2")
        p2.ChangeDutyCycle(50)
        x = 'z'

    elif x == 'h2':
        print("high Motor 2")
        p2.ChangeDutyCycle(75)
        x = 'z'

    # Exit
    elif x == 'e':
        GPIO.cleanup()
        print("GPIO Clean up")
        break
    
    else:
        print("<<<  wrong data  >>>")
        print("please enter the defined data to continue.....")
