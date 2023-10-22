import time
import board
import displayio
import busio
import asyncio
import adafruit_pcf8523
import adafruit_pcf8523_timer
from adafruit_hx8357 import HX8357

# Release any resources currently in use for the displays
displayio.release_displays()

# Constants
TILE_WIDTH = 16 # Width of single tile in pixels
TILE_HEIGHT = 16 # Height of single tile in pixels
SCREEN_WIDTH = 480 # Width of screen in pixels
SCREEN_HEIGHT = 320 # Width of height in pixels
PLANET_SCALE = 4 # Scaling factor for planet group
TWO_TILE_PAD = 32 # The number of pixels in 2 tiles on one axis
ROCKET_COLORS = 6 # The number of unique colors in the rocket

# Component Pins
spi = board.SPI()
tft_cs = board.D24
tft_dc = board.D25
rst = board.D7
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=rst)
i2c = busio.I2C(board.SCL, board.SDA)

days = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")

# Component objects
display = HX8357(display_bus, width=480, height=320, rotation=180)
rtc = adafruit_pcf8523.PCF8523(i2c)
timer = adafruit_pcf8523_timer.Timer(rtc.i2c_device)

# Configure timer. Needs to fire at 3 seconds, and enable the interrupt pin when doing so
# The timer should have a frequency of 1Hz. A value of 3 counts at 1hz would give 3 seconds
timer.timer_enabled = False
timer.timer_frequency = timer.TIMER_FREQ_1HZ
timer.timer_value = 3
timer.timer_status = False
timer.timer_enabled = True
    
# October 12 2021 - Marriage Epoch
# September 11 2023 2:54 PM - 15451007141016.463 miles

async def on_timer(timer_status):
    if timer_status:
        print("timer went off")
        timer.timer_status = False
    else:
        pass
            

async def main():
    timer_task = asyncio.create_task(on_timer(timer.timer_status))
    await asyncio.gather(timer_task)

    t = rtc.datetime
    #print(t)     # uncomment for debugging

    print("The date is %s %d/%d/%d" % (days[t.tm_wday], t.tm_mon, t.tm_mday, t.tm_year))
    print("The time is %d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec))

    time.sleep(1) # wait a second

while True:
     asyncio.run(main())


