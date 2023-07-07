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
        self.debounce_time = 500

    def is_pressed(self):
        if utime.ticks_diff(utime.ticks_ms(), self.last_press) > self.debounce_time:
            self.last_press = utime.ticks_ms()
            return True
        return False

class ChangeState:
    def __init__(self):
        #Set_Time Parameters
        self.time = False
        self.hours = False
        self.minutes = False
        
        #Set_Date Parameters
        self.date = False
        self.day = False
        self.month = False
        self.year = False
        
        #Set_FM Parameters
        self.setFM = False
        self.prefFM = False
        self.postFM = False
        
        #Set_Alarm Parameters
        self.alarm = False
        self.alarmHours = False
        self.alarmMinutes = False
        self.alarmDay = False
        self.alarmMonth = False
        self.alarmYear = False
        
    def reset_all(self):
        self.time = False
        self.hours = False
        self.minutes = False
        self.date = False
        self.year = False
        self.month = False
        self.day = False
        self.setFM = False
        self.prefFM = False
        self.postFM = False
        self.alarm = False
        self.alarmYear = False
        self.alarmMonth = False
        self.alarmDay = False
        self.alarmHours = False
        self.alarmMinutes = False

class ClockRadio:
    modes = ["Clock", "Volume", "set Alarm", "set Time", "set Date","24h Format", "change FM"]

    def __init__(self):
        print("starting clockradio from src")
        utime.sleep(0.5)
        
        self.initialize_buttons()
        self.initialize_radio()
        self.initialize_oled_and_rtc()
        self.initialize_changing_states()
        self.initialize_alarm_settings()

    def initialize_buttons(self):
        # Initialize button handlers
        self.mode_button = Button(0, Pin.IRQ_FALLING, self.mode_handler)
        self.select_button = Button(1, Pin.IRQ_FALLING, self.select_handler)
        self.left_button = Button(2, Pin.IRQ_FALLING, self.left_handler)
        self.right_button = Button(3, Pin.IRQ_FALLING, self.right_handler)

    def initialize_radio(self):
        # Initialize radio settings
        self.radio = fm_radio.Radio(101.9, 0, False)
        self.volume = 5
        self.fm = 101.9

    def initialize_oled_and_rtc(self):
        # Initialize display and real-time clock
        self.oled = display.OLEDText()
        self.rtc = RTC()
        self.current_time = list(self.rtc.datetime())
        self.current_mode = 0

    def initialize_changing_states(self):
        # Initialize state changes
        self.changing = ChangeState()
        self.settings = 0
        self.inactivity_timer = utime.ticks_ms()
        self.hour_format = False

    def initialize_alarm_settings(self):
        # Initialize alarm settings
        self.alarm = list((2023, 7, 6, 3, 19, 11, 0,0))
        self.alarm_ringing = False
        self.alarm_delay_minutes = 5
        self.current_alarmtime = self.current_time
        
        
    def mode_handler(self, pin):
        if not self.mode_button.is_pressed():
            return

        self.current_mode = (self.current_mode + 1) % len(ClockRadio.modes)
        self.reset_timer()

        modes_functions = {
            "set Time": self.configure_for_time,
            "set Date": self.configure_for_date,
            "change FM": self.configure_for_fm,
            "set Alarm": self.configure_for_alarm,
        }

        mode_function = modes_functions.get(ClockRadio.modes[self.current_mode])
        if mode_function is not None:
            mode_function()

        print("Current mode: " + ClockRadio.modes[self.current_mode])
        
    def configure_for_time(self):
        self.changing.reset_all()  # A method to reset all changing flags
        self.changing.time = True
        self.changing.hours = True
        self.changing.minutes = False
        
    def configure_for_date(self):
        self.changing.reset_all()  # A method to reset all changing flags
        self.changing.date = True
        self.changing.year = True
        self.changing.month = False
        self.changing.day = False
        
    def configure_for_fm(self):
        self.changing.reset_all()
        self.changing.setFM = True
        self.changing.prefFM = True
        self.changing.postFM = False
        
    def configure_for_alarm(self):
        self.changing.reset_all()
        self.changing.alarm = True
        self.changing.alarmYear = True
        self.changing.alarmMonth = False
        self.changing.alarmDay = False
        self.changing.alarmHours = False
        self.changing.alarmMinutes = False
            
    def left_handler(self, pin):
        if not self.left_button.is_pressed():
            return

        modes_functions = {
            "set Time": self.handle_time_decrease,
            "set Date": self.handle_date_decrease,
            "Volume": self.handle_volume_decrease,
            "change FM": self.handle_fm_decrease,
            "24h Format": self.handle_format_change,
            "set Alarm": self.handle_alarm_decrease
        }

        mode_function = modes_functions.get(self.modes[self.current_mode])
        if mode_function is not None:
            mode_function()

        self.reset_timer()
        
    def handle_time_decrease(self):
        if self.changing.hours:
            self.current_time[4] = (self.current_time[4] - 1) % 24
            print("changing hours")
        elif self.changing.minutes:
            self.current_time[5] = (self.current_time[5] - 1) % 60
            print("changing minutes")
        self.oled.display_time(tuple(self.current_time), True)
        
    def handle_date_decrease(self):
        if self.changing.day:
            self.current_time[2] = ((self.current_time[2] % 31) - 1) # Restrict day value between 1 and 31
            print("changing day")
        elif self.changing.month:
            self.current_time[1] = ((self.current_time[1] % 12) - 1)
            print("changing month")
        elif self.changing.year:
            self.current_time[0] = self.current_time[0] - 1  # No restriction for year value
            print("changing year")
        self.oled.display_date(tuple(self.current_time))
        
    def handle_volume_decrease(self):
        self.volume -= 1  # increase volume
    
    def handle_fm_decrease(self):
        if self.changing.prefFM:
            if 80 < float(self.fm)<= 120:
                self.fm -= 1
            else:
                self.fm = 120.0
        elif self.changing.postFM:
            self.fm -= 0.1
            
    def handle_format_change(self):
        self.hour_format = not self.hour_format
        print(self.hour_format)
        
    def handle_alarm_decrease(self):
        if self.changing.alarmYear:
            self.alarm[0] -= 1
            print("changing year")
        elif self.changing.alarmMonth:
            self.alarm[1] = (self.alarm[1] % 12) - 1
            print("changing month")
        elif self.changing.alarmDay:
            self.alarm[2] = (self.alarm[2] % 31) - 1
            print("changing day")
        elif self.changing.alarmHours:
            self.alarm[4] = (self.alarm[4] - 1) % 24
            print("changing hours")
        elif self.changing.alarmMinutes:
            self.alarm[5] = (self.alarm[5] - 1) % 60    
            print("changing minutes")
        self.oled.display_datetime(tuple(self.alarm))        

    def right_handler(self, pin):
        if not self.right_button.is_pressed():
            return

        modes_functions = {
            "set Time": self.handle_time_increase,
            "set Date": self.handle_date_increase,
            "Volume": self.handle_volume_increase,
            "change FM": self.handle_fm_increase,
            "24h Format": self.handle_format_change,
            "set Alarm": self.handle_alarm_increase
        }

        mode_function = modes_functions.get(self.modes[self.current_mode])
        if mode_function is not None:
            mode_function()

        self.reset_timer()
        
    def handle_time_increase(self):
        if self.changing.hours:
            self.current_time[4] = (self.current_time[4] + 1) % 24
            print("changing hours")
        elif self.changing.minutes:
            self.current_time[5] = (self.current_time[5] + 1) % 60
            print("changing minutes")
        self.oled.display_time(tuple(self.current_time), True)
        
    def handle_date_increase(self):
        if self.changing.day:
            self.current_time[2] = ((self.current_time[2] % 31) + 1) # Restrict day value between 1 and 31
            print("changing day")
        elif self.changing.month:
            self.current_time[1] = ((self.current_time[1] % 12) + 1)
            print("changing month")
        elif self.changing.year:
            self.current_time[0] = self.current_time[0] + 1  # No restriction for year value
            print("changing year")
        self.oled.display_date(tuple(self.current_time))
        
    def handle_volume_increase(self):
        self.volume += 1  # increase volume
    
    def handle_fm_increase(self):
        if self.changing.prefFM:
            if 80 <= float(self.fm)<= 120:
                self.fm += 1
            else:
                self.fm = 80.0
        elif self.changing.postFM:
            self.fm += 0.1
        
    def handle_alarm_increase(self):
        if self.changing.alarmYear:
            self.alarm[0] += 1
            print("changing year")
        elif self.changing.alarmMonth:
            self.alarm[1] = (self.alarm[1] % 12) + 1
            print("changing month")
        elif self.changing.alarmDay:
            self.alarm[2] = (self.alarm[2] % 31) + 1
            print("changing day")
        elif self.changing.alarmHours:
            self.alarm[4] = (self.alarm[4] + 1) % 24
            print("changing hours")
        elif self.changing.alarmMinutes:
            self.alarm[5] = (self.alarm[5] + 1) % 60    
            print("changing minutes")
        self.oled.display_datetime(tuple(self.alarm))
 
            
    def select_handler(self, pin):
        if not self.select_button.is_pressed():
            return

        modes_functions = {
            "set Time": self.handle_set_time,
            "set Date": self.handle_set_date,
            "Volume": self.handle_volume,
            "change FM": self.handle_change_fm,
            "24h Format": self.handle_24h_format,
            "set Alarm": self.handle_set_alarm
        }

        if self.alarm_ringing:
            self.alarm_ringing = False
            self.reset_timer()
            return
        
        mode_function = modes_functions.get(self.modes[self.current_mode])
        if mode_function is not None:
            mode_function()

        self.reset_timer()
        
    def handle_set_time(self):
        if self.changing.hours:
            self.changing.hours = False
            print("save hours")
            self.changing.minutes = True
        elif self.changing.minutes:
            self.changing.minutes = False
            print("save minutes")
            self.changing.hours = True
            self.rtc.datetime(self.current_time)  # update the RTC with the new time
            
    def handle_set_date(self):
        if self.changing.year:
            self.changing.year = False
            print("save year")
            self.changing.month = True
        elif self.changing.month:
            self.changing.month = False
            print("save month")
            self.changing.day = True
        elif self.changing.day:
            self.changing.day = False
            print("save day")
            self.changing.year = True
            self.rtc.datetime(self.current_time)  # update the RTC with the new date
            
    def handle_volume(self):
        self.radio.SetVolume(self.volume)  # Set the volume on the radio
        self.radio.ProgramRadio()
        print(self.radio.GetSettings())
        
    def handle_change_fm(self):
        if self.changing.prefFM:
            self.changing.prefFM = False
            print("save prefFM")
            self.changing.postFM = True
        elif self.changing.postFM:
            self.changing.postFM = False
            print("save postFM")
            self.changing.prefFM = True
            self.radio.SetFrequency(self.fm)
            self.radio.ProgramRadio()
        print(self.radio.GetSettings())
        
    def handle_24h_format(self):
        print("save 24/12h Format")
        
    def handle_set_alarm(self):
        if self.changing.alarmYear:
            self.changing.alarmYear = False
            print("save year")
            self.changing.alarmMonth = True
        elif self.changing.alarmMonth:
            self.changing.alarmMonth = False
            print("save month")
            self.changing.alarmDay = True
        elif self.changing.alarmDay:
            self.changing.alarmDay = False
            print("save day")
            self.changing.alarmHours = True
        elif self.changing.alarmHours:
            self.changing.alarmHours = False
            print("save hours")
            self.changing.alarmMinutes = True
        elif self.changing.alarmMinutes:
            self.changing.alarmMinutes = False
            print("save minutes")
            self.changing.alarmYear = True
    
            
    def reset_timer(self):
        # Reset the inactivity timer to the current time
        self.inactivity_timer = utime.ticks_ms()

    def check_inactivity(self):
        # Check if the inactivity timer has passed the thresholdTrue
        if utime.ticks_diff(utime.ticks_ms(), self.inactivity_timer) > 10000:  # 10 seconds
            self.current_mode = 0  # switch back to clock mode
            self.reset_timer()  # reset the timer
            
    def check_alarm(self):
        self.current_time = list(self.rtc.datetime())
        # check if the current time matches the alarm time
        if self.alarm[4:6] == self.current_time[4:6] and not self.alarm_ringing:
            self.alarm_ringing = True
            print("Alarm is ringing!!!")
        elif self.alarm_ringing:
            self.alarm_stop()  # stop the alarm if it's already ringing
    
    def alarm_stop(self):
        if self.select_button.is_pressed() and self.alarm_ringing:
            self.alarm_ringing = False
            print("Alarm stopped.")
            
    def snooze(self):
        if self.right_button.is_pressed() and self.alarm_ringing:
            self.alarm[5] = (self.alarm[5] + 30) % 60  # add 30 seconds to the alarm time
            self.alarm_ringing = False
            print("Snooze activated. Alarm will ring again in 30 seconds.")    

            
    def display_clock(self):
        self.current_time = list(self.rtc.datetime())  # Update current time
        self.oled.set_text(ClockRadio.modes[self.current_mode], 0, 0)
        self.oled.display_datetime(tuple(self.current_time), self.hour_format)
        self.oled.set_text("Vol: " + str(self.volume),4)
        self.oled.set_text(" FM: " + str(self.fm),5)

    def display_time(self):
        self.oled.set_text(ClockRadio.modes[self.current_mode], 0, 0)
        self.oled.display_time(tuple(self.current_time), self.hour_format)

    def display_date(self):
        self.oled.set_text(ClockRadio.modes[self.current_mode], 0, 0)
        self.oled.display_date(tuple(self.current_time))

    def display_volume(self):
        self.oled.set_text("Volume: " + str(self.volume), 0, 0)  # Display the current volume

    def display_fm(self):
        self.oled.set_text("FM: " + str(self.fm),0,0)

    def display_hour_format(self):
        #self.oled.clear_display()
        self.oled.set_text(ClockRadio.modes[self.current_mode], 0, 0)
        self.oled.set_text("State: " + str(self.hour_format),1,0)

    def display_alarm(self):
        self.oled.set_text(ClockRadio.modes[self.current_mode], 0, 0)
        self.oled.display_datetime(tuple(self.alarm), self.hour_format)

    def display_mode(self):
        self.oled.set_text(ClockRadio.modes[self.current_mode], 0, 0)  # Display the current mode


    def run(self):
        while True:
            self.check_inactivity()
            self.oled.clear()
            #self.oled.update_display()

            # Check the specific conditions first
            if self.modes[self.current_mode] == "24h Format":
                self.display_hour_format()
            elif self.modes[self.current_mode] == "Volume":
                self.display_volume()
            elif self.modes[self.current_mode] == "change FM":
                self.display_fm()
            elif self.changing.time:
                self.display_time()
            elif self.changing.date:
                self.display_date()
            elif self.changing.alarm:
                self.display_alarm()
            # The generic condition should be checked last
            elif ClockRadio.modes[self.current_mode] == "Clock":
                self.display_clock()
            else:
                self.display_mode()

            self.oled.update_display()
            utime.sleep(1)
            


if __name__ == "__main__":
    clock_radio = ClockRadio()
    clock_radio.run()
