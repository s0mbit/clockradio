import sys
import time
from machine import Pin,I2C,Timer,SPI
from ssd1306 import SSD1306_SPI

print("hello")

SCREEN_WIDTH = 128 #number of columns
SCREEN_HEIGHT = 64 #number of rows

spi_sck = Pin(10) # sck stands for serial clock; always be connected to SPI SCK pin of the Pico
spi_sda = Pin(11) # sda stands for serial data;  always be connected to SPI TX pin of the Pico; this is the MOSI
spi_res = Pin(12) # res stands for reset; to be connected to a free GPIO pin
spi_dc  = Pin(14) # dc stands for data/command; to be connected to a free GPIO pin
spi_cs  = Pin(13) # chip select; to be connected to the SPI chip select of the Pico 

SPI_DEVICE = 1 # Because the peripheral is connected to SPI 0 hardware lines of the Pico

oled_spi = SPI( SPI_DEVICE, baudrate= 100000, sck= spi_sck, mosi= spi_sda )
oled = SSD1306_SPI( SCREEN_WIDTH, SCREEN_HEIGHT, oled_spi, spi_dc, spi_res, spi_cs, True )


while ( True ):

        oled.fill(0)

        oled.text("Pineapple Ltd.", 0, 0) # Print the text starting from 0th column and 0th row
        oled.text("BlaBlaBla", 45, 10) # Print the number 299 starting at 45th column and 10th row
        
        oled.rect( 0, 50, 128, 5, 1  )        

        oled.show()
