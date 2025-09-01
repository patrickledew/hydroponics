from gpiozero import LED
import time
pin = 21

led = LED(pin)
print("Pin " + str(pin) + " on")
c = 1
while True:
    led.on()
    time.sleep(c)
    led.off()
    time.sleep(c)
    c = c / 1.1

