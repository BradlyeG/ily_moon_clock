import time
import board
import displayio
import busio
import asyncio
import adafruit_pcf8523
import adafruit_pcf8523_timer
import terminalio
from os import remove
from adafruit_hx8357 import HX8357
from adafruit_display_text import label

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
EPOCH_CYCLE = 1 # Number of times light has hit the moon and back from Marriage timestamp to program save

# Component Pins
spi = board.SPI()
tft_cs = board.D24
tft_dc = board.D25
rst = board.D7
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=rst)
i2c = busio.I2C(board.SCL, board.SDA)

# Component objects
display = HX8357(display_bus, width=480, height=320, rotation=180)
display.auto_refresh = False
rtc = adafruit_pcf8523.PCF8523(i2c)
timer = adafruit_pcf8523_timer.Timer(rtc.i2c_device)

# Display stuff (Images, Bitmaps, Sprites, Font, TileGrids, Groups)

# Label config
header_label_text = "I love you to the moon and back" 
font = terminalio.FONT
text_color = 0x0000FF
header = label.Label(font, text=header_label_text, color=text_color, scale = 2)
counter_label = label.Label(font, text="0 times!", color=text_color, scale = 2)
text_group = displayio.Group()
text_group.append(header)
text_group.append(counter_label)

# Set the label of the locations
header.x = 3 * TILE_WIDTH
header.y = 2 * TILE_HEIGHT

counter_label.x = 10 * TILE_WIDTH
counter_label.y = 14 * TILE_HEIGHT

# Show everything we need to show
display.show(text_group)


# Configure timer. Needs to fire at 3 seconds, and enable the interrupt pin when doing so
# The timer should have a frequency of 1Hz. A value of 3 counts at 1hz would give 3 seconds
timer.timer_enabled = False
timer.timer_frequency = timer.TIMER_FREQ_1HZ
timer.timer_value = 3
timer.timer_status = False
timer.timer_enabled = True

# Read timestamp to keep track of cycles and calculate the current cycle
current_cycle = 1

# What to do when the timer goes off
# First delete current time stamp file
# Write new timestamp
# Update cycle count
# Reset the alarm
async def on_timer(timer_status, clock, label):
    if timer_status:
        '''try:
            remove("/timestamp.txt")
        except:
            print("couldn't remove timestamp file")

        try:
            with open("/timestamp.txt", "a") as ts:
                t = clock.datetime
                ts.write("%d,%d,%d,%d,%d,%d" % (t.tm_mon, t.tm_mday, t.tm_year, t.tm_hour, t.tm_min, t.tm_sec))
                ts.flush()
        except OSError as e:  # Typically when the filesystem isn't writeable...
            print("error writing time stamp")'''
        global current_cycle
        current_cycle += 1
        label.text = "%d times!" % (current_cycle)
        timer.timer_status = False
    else:
        pass
            

async def main():
    # Create the timer task
    timer_task = asyncio.create_task(on_timer(timer.timer_status, rtc, counter_label))
    
    # Let it run 
    await asyncio.gather(timer_task)

    # doing other stuff
    time.sleep(3.0)
    display.refresh()


# refresh the display after everything is set up
display.refresh()

while True:
     asyncio.run(main())


