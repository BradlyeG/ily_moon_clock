# SPDX-License-Identifier: MIT

from random import randrange
import time
import board
import displayio
import busio
import asyncio
import adafruit_pcf8523
import adafruit_pcf8523_timer
import simple_particle_sim
import adafruit_imageload
from os import remove
from adafruit_hx8357 import HX8357
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

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
NUM_PARTICLES = 50 # Number of particles to maintain in the particle sim
MAX_PARTICLE_SPEED = -35 # Max speed of particles in pixels per update

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
font = bitmap_font.load_font("art/pp_opt-16.bdf")
text_color = 0x0000FF
header = label.Label(font, text=header_label_text, color=text_color, scale = 1)
counter_label = label.Label(font, text="0 times!", color=text_color, scale = 1)
text_group = displayio.Group()
text_group.append(header)
text_group.append(counter_label)

# Set the label of the locations
header.x = int(4.75 * TILE_WIDTH)
header.y = 2 * TILE_HEIGHT

counter_label.x = 12 * TILE_WIDTH
counter_label.y = 8 * TILE_HEIGHT

# Particle system config
particle_system = simple_particle_sim.ParticleSystem(NUM_PARTICLES, SCREEN_HEIGHT, SCREEN_WIDTH, MAX_PARTICLE_SPEED, 0, 0, 0, SCREEN_WIDTH - 1, 0, rand_y=True)

# Planet and Rocket config
# Create list for tile indicies from sprite sheet
earth_index = (0, 1, 2, 3)
moon_index = (4, 5, 6, 7)
rocket_index = (8, 9, 10, 11)

# Create main sprite sheet
art_sprite, art_palette = adafruit_imageload.load("art/sprite_sheet.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
art_palette.make_transparent(0)

# Create tile grids for earth, moon, rocket
earth_tile_grid = displayio.TileGrid(art_sprite, pixel_shader=art_palette, width = 2, height = 2, tile_width = TILE_WIDTH, tile_height = TILE_HEIGHT)
moon_tile_grid = displayio.TileGrid(art_sprite, pixel_shader=art_palette, width = 2, height = 2, tile_width = TILE_WIDTH, tile_height = TILE_HEIGHT) 
rocket_tile_grid = displayio.TileGrid(art_sprite, pixel_shader=art_palette, width = 2, height = 2, tile_width = TILE_WIDTH, tile_height = TILE_HEIGHT)

# Set the tiles of each tile grid from the sprite sheet
for index in range(len(earth_index)):
    earth_tile_grid[index] = earth_index[index]

for index in range(len(moon_index)):
    moon_tile_grid[index] = moon_index[index]

for index in range(len(rocket_index)):
    rocket_tile_grid[index] = rocket_index[index]

# Create group for earth, and moon, then separate for rocket and append TGs to groups
planet_group = displayio.Group()
rocket_group = displayio.Group()
planet_group.append(earth_tile_grid)
planet_group.append(moon_tile_grid)
rocket_group.append(rocket_tile_grid)


# Set position of tile grids within their group
earth_tile_grid.x = 0
moon_tile_grid.x = int((SCREEN_WIDTH/PLANET_SCALE) - (moon_tile_grid.width * TILE_WIDTH)) # Because the layer is scaled up we effectively have less screen space in the x direction - divide width by scale then subtract the width of the object to get to other corner

# Set the rotation of the rocket
rocket_tile_grid.transpose_xy = True
rocket_tile_grid.flip_y = True

# Set position of groups
planet_group.y = int(SCREEN_HEIGHT - (earth_tile_grid.height * TILE_HEIGHT * PLANET_SCALE))
rocket_group.x = 8 * TILE_WIDTH
rocket_group.y = 15 * TILE_HEIGHT

# Scale up the planet group so the planets are bigger
planet_group.scale = PLANET_SCALE

# Need to make a list of points for the rocket to follow - x direction only
#rocket_anim_pts = [8,12,16,20]

planet_rocket = displayio.Group()
planet_rocket.append(planet_group)
planet_rocket.append(rocket_group)

# Show everything we need to show
# Root layer - Particle System
# 2 - Planet
# 3 - Rocket
# 4 - Label
display_group = displayio.Group()
display_group.append(particle_system)
display_group.append(planet_rocket)
display_group.append(text_group)

# Display groups
display.show(display_group)

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
            

async def main(rtg):
    # Create the timer task
    timer_task = asyncio.create_task(on_timer(timer.timer_status, rtc, counter_label))
    
    # Let it run 
    await asyncio.gather(timer_task)

    # Update particles
    particle_system.remove_out_of_bounds()
    particle_system.update()

    if rtg.x < (12 * TILE_WIDTH) and rtg.flip_y:
        rtg.x += (4 * TILE_WIDTH)
    elif rtg.x == (12 * TILE_WIDTH) and rtg.flip_y:
        rtg.flip_y = False
    elif not rtg.flip_y and rtg.x > (2 * TILE_WIDTH):
        rtg.x -= (4 * TILE_WIDTH)
    elif rtg.x == (0) and not rtg.flip_y:
        rtg.flip_y  = True

    display.refresh()

    time.sleep(0.25)


# refresh the display after everything is set up
display.refresh()

while True:
     asyncio.run(main(rocket_tile_grid))



