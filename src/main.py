import sys
import time
import display
import radio
import clock
import utime

print("starting clockradio")
utime.sleep(0.5)

try:
    # Start the display
    display.update_display()

    # Main loop
    while True:
        # Add tasks here
        utime.sleep(1)

except Exception as e:
    print('Error:', e)
        
