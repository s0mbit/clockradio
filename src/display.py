from machine import Pin, SPI
from ssd1306 import SSD1306_SPI
import utime

class OLEDText:
    def __init__(self, width=128, height=64, spi_device=1, sck=10, mosi=11, res=12, dc=14, cs=13):
        self.width = width
        self.height = height
        self.spi_device = spi_device
        
        # Initialize the SPI
        spi_sck = Pin(sck)  
        spi_sda = Pin(mosi)
        spi_res = Pin(res) 
        spi_dc  = Pin(dc)
        spi_cs  = Pin(cs)
        
        self.oled_spi = SPI(spi_device, baudrate=100000, sck=spi_sck, mosi=spi_sda)
        self.oled = SSD1306_SPI(self.width, self.height, self.oled_spi, spi_dc, spi_res, spi_cs, True)

    def set_text(self, text, row=0):
        self.oled.text(text, 0, row * 10)  # Assumes each row is 10 pixels high

    def display_text_value(self, text, value, row=0):
        full_text = "{}: {}".format(text, value)
        self.clear()  # Clear the display first
        self.set_text(full_text, row)  # Set the full text
        self.update_display()  # Update the display

    def update_display(self):
        self.oled.show()

    def clear(self):
        self.oled.fill(0)

    def clear_display(self):
        self.fill(0)
        self.show()
        
    def display_time(self):
        current_time = utime.localtime()
        time_str = "{:02d}:{:02d}:{:02d}".format(current_time[3], current_time[4], current_time[5])
        self.display_text_value("Time", time_str)
