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

    def set_text(self, text, row=0, center=False):
        if center:
            text_width = self.oled.width - len(text) * 6  # Assuming each character is 6 pixels wide
            text_x = max((0, (self.oled.width - text_width) // 2))  # Calculate the x-coordinate to center the text
        else:
            text_x = 0
        
        self.oled.text(text, text_x, row * 10)  # Assumes each row is 10 pixels high
        self.update_display()


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
        self.oled.fill(0)
        self.oled.show()
        
    def display_time(self,dt):
        #self.clear()
        dt_str1 = "{}-{}-{}".format(dt[0], dt[1], dt[2])
        dt_str2 = "{}:{}:{}".format(dt[4], dt[5], dt[6])
        self.set_text(dt_str1, 2,True)
        self.set_text(dt_str2, 3,True)
        
        
        
