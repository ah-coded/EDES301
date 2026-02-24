import Adafruit_BBIO.GPIO as GPIO
import time

test_pin = "P2_04" # Try P2_04 instead of P2_02
GPIO.setup(test_pin, GPIO.IN)

print(f"Success! Pin {test_pin} is now an input.")
print(f"Current Value: {GPIO.input(test_pin)}")
GPIO.cleanup()