import sys
import time
import display
import utime
from machine import Pin, I2C, Timer, SPI


print("starting clockradio")
utime.sleep(0.5)

# Buttons
mode_button = Pin(0, Pin.IN, Pin.PULL_UP)  # Assuming button on GPIO pin 2
select_button = Pin(1, Pin.IN, Pin.PULL_UP)  # Assuming button on GPIO pin 3
left_button = Pin(2, Pin.IN, Pin.PULL_UP)  # Assuming button on GPIO pin 4
right_button = Pin(3, Pin.IN, Pin.PULL_UP)  # Assuming button on GPIO pin 5

oled = display.OLEDText()


try:
    # Start the display

    # Main loop
    while True:
        # Add tasks here
        utime.sleep(1)
        oled.display_time()

        

except Exception as e:
    print('Error:', e)
        
