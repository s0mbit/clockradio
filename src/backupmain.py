import sys
import display
import utime
import fm_radio
from machine import Pin,RTC,Timer


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
current_time = list(rtc.datetime())
# Mode setup
modes = ["Clock", "Volume", "set Alarm", "set Time", "set Date", "12/24h format", "change FM"]
current_mode = 0

# Button debounce setup
debounce_time = 400  # debounce time in milliseconds
last_button_press = utime.ticks_ms()



changing_date = False
changing_day = False
changing_month = False
changing_year = False

def mode_handler(pin):
    global current_mode, last_button_press, changing_time, changing_date, changing_hours, changing_minutes, changing_month, changing_year, changing_day
    if utime.ticks_diff(utime.ticks_ms(), last_button_press) > debounce_time:
        current_mode = (current_mode + 1) % len(modes)
        if modes[current_mode] == "set Time":
            changing_time = True
            changing_hours = True  # initially set to change hours
            changing_minutes = False
        else:
            changing_time = False
            changing_hours = False
            changing_minutes = False
        #changing_date = (modes[current_mode] == "set Date")
        if modes[current_mode] == "set Date":
            changing_date = True
            changing_year = True
            changing_month = False
            changing_day = False
        else:
            changing_date = False
            changing_year = False
            changing_month = False
            changing_day = False
        print("Current mode: " + modes[current_mode])  # For debugging on console
    last_button_press = utime.ticks_ms()


def left_handler(pin):
    global last_button_press, current_time
    if utime.ticks_diff(utime.ticks_ms(), last_button_press) > debounce_time:
        if changing_time:
            if changing_hours:
                current_time[4] = (current_time[4] - 1) % 24
                print("changing hours")
            elif changing_minutes:
                current_time[5] = (current_time[5] - 1) % 60
                print("changing minutes")
            oled.display_time(tuple(current_time), True)
        elif changing_date:
            if changing_day:
                current_time[2] = max(1, (current_time[2] - 1))
                print("changing day")
            elif changing_month:
                current_time[1] = max(1, (current_time[1] - 1))
            elif changing_year:
                current_time[0] -= 1
            oled.display_time(tuple(current_time), True)  
        last_button_press = utime.ticks_ms()


def right_handler(pin):
    global last_button_press, current_time
    if utime.ticks_diff(utime.ticks_ms(), last_button_press) > debounce_time:
        if changing_time:
            if changing_hours:
                current_time[4] = (current_time[4] + 1) % 24
                print("changing hours")
            elif changing_minutes:
                current_time[5] = (current_time[5] + 1) % 60
                print("changing minutes")
            oled.display_time(tuple(current_time), True)
        elif changing_date:
            if changing_day:
                current_time[2] = max(1, min(current_time[2] + 1, 31))  # Restrict day value between 1 and 31
                print("changing day")
            elif changing_month:
                current_time[1] = max(1, min(current_time[1] + 1, 12))  # Restrict month value between 1 and 12
                print("changing month")
            elif changing_year:
                current_time[0] = current_time[0] + 1  # No restriction for year value
                print("changing year")
            oled.display_time(tuple(current_time), True)
        last_button_press = utime.ticks_ms()


def select_handler(pin):
    global last_button_press, changing_time, changing_hours, changing_minutes, changing_date, changing_day, changing_month, changing_year
    if utime.ticks_diff(utime.ticks_ms(), last_button_press) > debounce_time:
        if changing_time:
            if changing_hours:
                changing_hours = False
                changing_minutes = True
            elif changing_minutes:
                changing_minutes = False
                changing_hours = True  # start changing hours again
                rtc.datetime(current_time)  # update the RTC with the new time
        elif changing_date:
            if changing_year:
                changing_year = False
                changing_month = True
            elif changing_month:
                changing_month = False
                changing_day = True
            elif changing_day:
                changing_day = False
                changing_year = True  # done changing date
                rtc.datetime(current_time)  # update the RTC with the new date
        else:
            if modes[current_mode] == "set Time":
                changing_hours = True
                changing_minutes = False
            else:
                changing_hours = False
                changing_minutes = False
                changing_date = True
                changing_day = True
                changing_month = False
                changing_year = False
        last_button_press = utime.ticks_ms()




# Attach interrupts
mode_button.irq(trigger=Pin.IRQ_FALLING, handler=mode_handler)
select_button.irq(trigger=Pin.IRQ_FALLING, handler=select_handler)
left_button.irq(trigger=Pin.IRQ_FALLING, handler=left_handler)
right_button.irq(trigger=Pin.IRQ_FALLING, handler=right_handler)


while True:
    if modes[current_mode] == "Clock":
        current_time = list(rtc.datetime())  # Update current time
    oled.clear()
    if changing_time or changing_date or modes[current_mode] == "Clock":
        oled.display_time(tuple(current_time), True)
    else:
        oled.set_text(modes[current_mode], 0, 0)  # Display the current mode
    oled.update_display()
    utime.sleep(1)

