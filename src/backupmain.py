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

class ClockRadio:
    modes = ["Clock", "Volume", "set Alarm", "set Time", "set Date","24h Format", "change FM"]

    def __init__(self):
        print("starting clockradio from src")
        utime.sleep(0.5)
        
        self.mode_button = Button(0, Pin.IRQ_FALLING, self.mode_handler)
        self.select_button = Button(1, Pin.IRQ_FALLING, self.select_handler)
        self.left_button = Button(2, Pin.IRQ_FALLING, self.left_handler)
        self.right_button = Button(3, Pin.IRQ_FALLING, self.right_handler)

        self.radio = fm_radio.Radio(101.9, 0, False)
        self.volume = 5
        self.fm = 101.9
        #utime.sleep(1)
        self.oled = display.OLEDText()
        self.rtc = RTC()
        self.current_time = list(self.rtc.datetime())
        self.current_mode = 0
        self.changing = ChangeState()
        self.settings = 0
        self.inactivity_timer = utime.ticks_ms()
        self.hour_format = False
        self.alarm = list((2023, 7, 6, 3, 19, 11, 0,0))
        self.alarm_ringing = False
        self.alarm_delay_minutes = 5
        self.current_alarmtime = self.current_time
        

    def mode_handler(self, pin):
        if self.mode_button.is_pressed():
            self.current_mode = (self.current_mode + 1) % len(ClockRadio.modes)
            self.reset_timer()
            self.changing.time = ClockRadio.modes[self.current_mode] == "set Time"
            self.changing.hours = self.changing.time
            self.changing.minutes = not self.changing.time
            self.changing.date = ClockRadio.modes[self.current_mode] == "set Date"
            self.changing.year = self.changing.date
            self.changing.month = not self.changing.date
            self.changing.day = not self.changing.date
            self.changing.setFM = ClockRadio.modes[self.current_mode] == "change FM"
            self.changing.prefFM = self.changing.setFM
            self.changing.postFM = not self.changing.setFM
            self.changing.alarm = ClockRadio.modes[self.current_mode] == "set Alarm"
            #self.alarm = list(self.current_time)
            self.changing.alarmYear = self.changing.alarm
            self.changing.alarmMonth = not self.changing.alarm
            self.changing.alarmDay = not self.changing.alarm
            self.changing.alarmHours = not self.changing.alarm
            self.changing.alarmMinutes = not self.changing.alarm
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
                    self.current_time[2] = ((self.current_time[2] - 2) % 31) + 1
                    print("changing day")
                elif self.changing.month:
                    self.current_time[1] = ((self.current_time[1] - 2) % 12) + 1
                    print("changing month")
                elif self.changing.year:
                    self.current_time[0] -= 1
                    print("changing year")
                self.oled.display_date(tuple(self.current_time))
            elif self.modes[self.current_mode] == "Volume":
                self.volume -= 1  # decrease volume
            elif self.changing.setFM:
                if self.changing.prefFM:
                    if 80 < float(self.fm)<= 120:
                        self.fm -= 1
                    else:
                        self.fm = 120.0
                elif self.changing.postFM:
                    self.fm -= 0.1
            elif self.modes[self.current_mode] == "24h Format":
                self.hour_format = False 
                
            elif self.changing.alarm:
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
                    print("changing hour")
                elif self.changing.alarmMinutes:
                    self.alarm[5] = (self.alarm[5] - 1) % 60  
                    print("changing minutes") 
                self.oled.display_datetime(tuple(self.alarm))

            self.reset_timer()

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
                    self.current_time[2] = ((self.current_time[2] % 31) + 1) # Restrict day value between 1 and 31
                    print("changing day")
                elif self.changing.month:
                    self.current_time[1] = ((self.current_time[1] % 12) + 1)
                    print("changing month")
                elif self.changing.year:
                    self.current_time[0] = self.current_time[0] + 1  # No restriction for year value
                    print("changing year")
                self.oled.display_date(tuple(self.current_time))
            elif self.modes[self.current_mode] == "Volumself.alarm = list(self.current_time)e":
                self.volume += 1  # increase volume
            elif self.changing.setFM:
                if self.changing.prefFM:
                    if 80 <= float(self.fm)<= 120:
                        self.fm += 1
                    else:
                        self.fm = 80.0
                elif self.changing.postFM:
                    self.fm += 0.1
            elif self.modes[self.current_mode] == "24h Format":
                self.hour_format = True 
                
            elif self.changing.alarm:
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
            
            self.reset_timer()

    def select_handler(self, pin):
        if self.select_button.is_pressed():
            
            if self.changing.time:
                if self.changing.hours:
                    self.changing.hours = False
                    print("save hours")
                    self.changing.minutes = True
                elif self.changing.minutes:
                    self.changing.minutes = False
                    print("save minutes")
                    self.changing.hours = True
                    self.rtc.datetime(self.current_time)  # update the RTC with the new time
            elif self.changing.date:
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
            elif self.modes[self.current_mode] == "Volume":
                self.radio.SetVolume(self.volume)  # Set the volume on the radio
                self.radio.ProgramRadio()
                print(self.radio.GetSettings())
            elif self.modes[self.current_mode] == "change FM":
                if self.changing.setFM:
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
            elif self.modes[self.current_mode] == "24h Format":
                print("save 24/12h Format")
            elif self.changing.alarm:
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
            elif self.alarm_ringing:
                self.alarm_ringing = False
                        
 
            self.reset_timer()
            
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
            
    

    def run(self):
        while True:
            self.check_inactivity()

            # Always clear the display at the beginning of each cycle
            self.oled.clear()

            if ClockRadio.modes[self.current_mode] == "Clock":
                self.current_time = list(self.rtc.datetime())  # Update current time
                self.oled.set_text(ClockRadio.modes[self.current_mode], 0, 0)
                self.oled.display_datetime(tuple(self.current_time), self.hour_format)
                self.oled.set_text("Vol: " + str(self.volume),4)
                self.oled.set_text(" FM: " + str(self.fm),5)

            elif self.changing.time:
                self.oled.set_text(ClockRadio.modes[self.current_mode], 0, 0)
                self.oled.display_time(tuple(self.current_time), self.hour_format)
                
            elif self.changing.date:
                self.oled.set_text(ClockRadio.modes[self.current_mode], 0, 0)
                self.oled.display_date(tuple(self.current_time))

            elif self.modes[self.current_mode] == "Volume":
                self.oled.set_text("Volume: " + str(self.volume), 0, 0)  # Display the current volume

            elif self.modes[self.current_mode] == "change FM":
                self.oled.set_text("FM: " + str(self.fm),0,0)
                
            elif self.modes[self.current_mode] == "24h Format":
                self.oled.set_text(ClockRadio.modes[self.current_mode], 0, 0)
                self.oled.set_text("State: " + str(self.hour_format),1,0)
                
            elif self.changing.alarm:
                self.oled.set_text(ClockRadio.modes[self.current_mode], 0, 0)
                self.oled.display_datetime(tuple(self.alarm), self.hour_format)

            else:
                self.oled.set_text(ClockRadio.modes[self.current_mode], 0, 0)  # Display the current mode

            self.oled.update_display()
            utime.sleep(1)
            
            


if __name__ == "__main__":
    clock_radio = ClockRadio()
    clock_radio.run()
