import RPi.GPIO as GPIO
import time

GPIO_PINs = [5, 6, 13, 19]
# For key 1, 2, 3, 4 respectively
count = 50

GPIO.setmode(GPIO.BCM)
for GPIO_PIN in GPIO_PINs:
    GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while count > 0:
    for GPIO_PIN in GPIO_PINs:
        if(GPIO.input(GPIO_PIN) == 0):
            count = count - 1
            print(f"{GPIO_PIN} pin pressed")
    time.sleep(0.1)

print("exit...")
GPIO.cleanup()