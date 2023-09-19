import board
import displayio
from adafruit_hx8357 import HX8357

# Release any resources currently in use for the displays
displayio.release_displays()

# Component Pins
spi = board.SPI()
tft_cs = board.D24
tft_dc = board.D25
rst = board.D7
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=rst)

display = HX8357(display_bus, width=480, height=320)

# Main Display Context
screen = displayio.Group()
display.show(screen)