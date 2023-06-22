from machine import Pin, I2C, Timer, SPI
from lib.ssd1306 import SSD1306_SPI
import utime

SCREEN_WIDTH = 128  # number of columns
SCREEN_HEIGHT = 64  # number of rows

spi_sck = Pin(10)  # sck stands for serial clock; always be connected to SPI SCK pin of the Pico
spi_sda = Pin(11)  # sda stands for serial data;  always be connected to SPI TX pin of the Pico; this is the MOSI
spi_res = Pin(12)  # res stands for reset; to be connected to a free GPIO pin
spi_dc  = Pin(14)  # dc stands for data/command; to be connected to a free GPIO pin
spi_cs  = Pin(13)  # chip select; to be connected to the SPI chip select of the Pico 

SPI_DEVICE = 1  # Because the peripheral is connected to SPI 0 hardware lines of the Pico

oled_spi = SPI( SPI_DEVICE, baudrate= 100000, sck= spi_sck, mosi= spi_sda )
oled = SSD1306_SPI( SCREEN_WIDTH, SCREEN_HEIGHT, oled_spi, spi_dc, spi_res, spi_cs, True)

# State machine states
CLOCK_DISPLAY = 0
FORMAT_SETTING = 1
ALARM_SETTING = 2
VOLUME_SETTING = 3
RADIO_STATION_SETTING = 4
SETTINGS = [
    "Time",
    "Format",
    "Alarm",
    "Volume",
    "Station"
]
NUM_SETTINGS = len(SETTINGS)

# Buttons
mode_button = Pin(2, Pin.IN, Pin.PULL_UP)  # Assuming button on GPIO pin 2
select_button = Pin(3, Pin.IN, Pin.PULL_UP)  # Assuming button on GPIO pin 3
left_button = Pin(4, Pin.IN, Pin.PULL_UP)  # Assuming button on GPIO pin 4
right_button = Pin(5, Pin.IN, Pin.PULL_UP)  # Assuming button on GPIO pin 5

# Settings
format_24h = True
alarm_time = '06:00'
volume = 5
radio_station = '100.0 FM'
settings_values = [
    utime.localtime(),
    format_24h,
    alarm_time,
    volume,
    radio_station
]

# State
state = CLOCK_DISPLAY
changing_setting = False

def mode_button_pressed(_):
    global state, changing_setting
    if not changing_setting:
        state = (state + 1) % NUM_SETTINGS
    oled.fill(0)
    update_display()

def select_button_pressed(_):
    global changing_setting
    changing_setting = not changing_setting
    oled.fill(0)
    update_display()

def left_button_pressed(_):
    if changing_setting:
        change_setting(-1)
    oled.fill(0)
    update_display()

def right_button_pressed(_):
    if changing_setting:
        change_setting(1)
    oled.fill(0)
    update_display()

def change_setting(delta):
    global format_24h, alarm_time, volume, radio_station
    if state == FORMAT_SETTING:
        format_24h = not format_24h
    elif state == ALARM_SETTING:
        # Implement logic for changing alarm time
        pass
    elif state == VOLUME_SETTING:
        volume = max(0, volume + delta)
    elif state == RADIO_STATION_SETTING:
        # Implement logic for changing radio station
        pass
    settings_values[state] = format_24h if state == FORMAT_SETTING else settings_values[state]
    settings_values[state] = alarm_time if state == ALARM_SETTING else settings_values[state]
    settings_values[state] = volume if state == VOLUME_SETTING else settings_values[state]
    settings_values[state] = radio_station if state == RADIO_STATION_SETTING else settings_values[state]

def update_display():
    if changing_setting:
        oled.text("Change {} to {}".format(SETTINGS[state], settings_values[state]), 0, 0)
    else:
        oled.text("Time: {}".format(settings_values[0]), 0, 0)
        for i in range(1, NUM_SETTINGS):
            oled.text("{}: {}".format(SETTINGS[i], settings_values[i]), 0, (i * 10) % SCREEN_HEIGHT)
    oled.show()

mode_button.irq(mode_button_pressed, Pin.IRQ_FALLING)
select_button.irq(select_button_pressed, Pin.IRQ_FALLING)
left_button.irq(left_button_pressed, Pin.IRQ_FALLING)
right_button.irq(right_button_pressed, Pin.IRQ_FALLING)

timer = Timer()
timer.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:update_display())  # Update every second
