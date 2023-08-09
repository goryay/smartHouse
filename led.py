import RPi.GPIO as GPIO
from time import sleep 

LED_PIN = 17
BUTTON_PIN = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(LED_PIN, 0)
GPIO.output(LED_PIN, 1)

sleep(3)

while True:
    if (GPIO.input(BUTTON_PIN) == False):
        GPIO.output(LED_PIN, 1)
    else:
        GPIO.output(LED_PIN, 0)
    sleep(1);

GPIO.cleanup()
