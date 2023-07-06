import sys
import display
import utime
import fm_radio
from machine import Pin,RTC,Timer

class Button:
    def __init__(self, pin_number, trigger, handler):
        self.pin = Pin(pin_number, Pin.IN, Pin.PULL_UP)
        self.pin.irq(trigger=trigger, handler=handler)
        self.last_press = utime.ticks_ms()
        self.debounce_time = 400

    def is_pressed(self):
        if utime.ticks_diff(utime.ticks_ms(), self.last_press) > self.debounce_time:
            self.last_press = utime.ticks_ms()
            return True
        return False

class ChangeState:
    def __init__(self):
        self.time = False
        self.date = False
        self.hours = False
        self.minutes = False
        self.day = False
        self.month = False
        self.year = False

class ClockRadio:
    modes = ["Clock", "Volume", "set Alarm", "set Time", "set Date", "12/24h format", "change FM"]

    def __init__(self):
        print("starting clockradio from src")
        utime.sleep(0.5)
        
        self.mode_button = Button(0, Pin.IRQ_FALLING, self.mode_handler)
        self.select_button = Button(1, Pin.IRQ_FALLING, self.select_handler)
        self.left_button = Button(2, Pin.IRQ_FALLING, self.left_handler)
        self.right_button = Button(3, Pin.IRQ_FALLING, self.right_handler)

        self.radio = fm_radio.Radio(101.9, 0, False)
        utime.sleep(1)
        self.oled = display.OLEDText()
        self.rtc = RTC()
        self.current_time = list(self.rtc.datetime())
        self.current_mode = 0
        self.changing = ChangeState()

    def mode_handler(self, pin):
        if self.mode_button.is_pressed():
            self.current_mode = (self.current_mode + 1) % len(ClockRadio.modes)
            self.changing.time = ClockRadio.modes[self.current_mode] == "set Time"
            self.changing.hours = self.changing.time
            self.changing.minutes = not self.changing.time
            self.changing.date = ClockRadio.modes[self.current_mode] == "set Date"
            self.changing.year = self.changing.date
            self.changing.month = not self.changing.date
            self.changing.day = not self.changing.date
            print("Current mode: " + ClockRadio.modes[self.current_mode])

    def left_handler(self, pin):
        if self.left_button.is_pressed():
            if self.changing.time:
                if self.changing.hours:
                    self.current_time[4] = (self.current_time[4] - 1) % 24
                    print("changing hours")
                elif self.changing.minutes:
                    self.current_time[5] = (self.current_time[5] - 1) % 60
                    print("changing minutes")
                self.oled.display_time(tuple(self.current_time), True)
            elif self.changing.date:
                if self.changing.day:
                    self.current_time[2] = max(1I apologize for the truncation of the code in the previous message. Here's the continuation of the code:

```python
                    self.current_time[2] = max(1, (self.current_time[2] - 1))
                    print("changing day")
                elif self.changing.month:
                    self.current_time[1] = max(1, (self.current_time[1] - 1))
                    print("changing month")
                elif self.changing.year:
                    self.current_time[0] -= 1
                    print("changing year")
                self.oled.display_time(tuple(self.current_time), True)

    def right_handler(self, pin):
        if self.right_button.is_pressed():
            if self.changing.time:
                if self.changing.hours:
                    self.current_time[4] = (self.current_time[4] + 1) % 24
                    print("changing hours")
                elif self.changing.minutes:
                    self.current_time[5] = (self.current_time[5] + 1) % 60
                    print("changing minutes")
                self.oled.display_time(tuple(self.current_time), True)
            elif self.changing.date:
                if self.changing.day:
                    self.current_time[2] = max(1, min(self.current_time[2] + 1, 31))  # Restrict day value between 1 and 31
                    print("changing day")
                elif self.changing.month:
                    self.current_time[1] = max(1, min(self.current_time[1] + 1, 12))  # Restrict month value between 1 and 12
                    print("changing month")
                elif self.changing.year:
                    self.current_time[0] = self.current_time[0] + 1  # No restriction for year value
                    print("changing year")
                self.oled.display_time(tuple(self.current_time), True)

    def select_handler(self, pin):
        if self.select_button.is_pressed():
            if self.changing.time:
                if self.changing.hours:
                    self.changing.hours = False
                    self.changing.minutes = True
                elif self.changing.minutes:
                    self.changing.minutes = False
                    self.changing.hours = True
                    self.rtc.datetime(self.current_time)  # update the RTC with the new time
            elif self.changing.date:
                if self.changing.year:
                    self.changing.year = False
                    self.changing.month = True
                elif self.changing.month:
                    self.changing.month = False
                    self.changing.day = True
                elif self.changing.day:
                    self.changing.day = False
                    self.changing.year = True
                    self.rtc.datetime(self.current_time)  # update the RTC with the new date

    def run(self):
        while True:
            if ClockRadio.modes[self.current_mode] == "Clock":
                self.current_time = list(self.rtc.datetime())  # Update current time
            self.oled.clear()
            if self.changing.time or self.changing.date or ClockRadio.modes[self.current_mode] == "Clock":
                self.oled.display_time(tuple(self.current_time), True)
            else:
                self.oled.set_text(ClockRadio.modes[self.current_mode], 0, 0)  # Display the current mode
            self.oled.update_display()
            utime.sleep(1)


if __name__ == "__main__":
    clock_radio = ClockRadio()
    clock_radio.run()
