import sys
import display
import utime
import fm_radio
from machine import Pin,RTC


print("starting clockradio from src")
utime.sleep(0.5)

# Buttons
mode_button = Pin(0, Pin.IN, Pin.PULL_UP)  # Assuming button on GPIO pin 2
select_button = Pin(1, Pin.IN, Pin.PULL_UP)  # Assuming button on GPIO pin 3
left_button = Pin(2, Pin.IN, Pin.PULL_UP)  # Assuming button on GPIO pin 4
right_button = Pin(3, Pin.IN, Pin.PULL_UP)  # Assuming button on GPIO pin 5

radio = fm_radio.Radio(101.9,0,False) 
utime.sleep(1)
oled = display.OLEDText()
rtc = RTC()


i = 0


# Main loop
while True:
    # Add tasks here
    #utime.sleep(1)
    dt = rtc.datetime()
    oled.clear()
    oled.display_time(dt,True)
    oled.update_display()
    


        

