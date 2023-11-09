# SPDX-License-Identifier: MIT

import time
import board
import displayio
import math
from adafruit_hx8357 import HX8357
import adafruit_imageload

import displayio
import math

class RotatableTileGrid(displayio.TileGrid):
    def __init__(self, tileset, width, height, tile_width, tile_height, pixel_shader, max_cols, angle_degrees=0, x=0, y=0):
        super().__init__(
            tileset,
            width=width,
            height=height,
            tile_width=tile_width,
            tile_height=tile_height,
            pixel_shader=pixel_shader,
            x=x,
            y=y
        )
        # this is needed to get number of colors from the original tileset to pass in to the bitmap that is created procedurally
        self.max_cols = max_cols
        self.angle_degrees = angle_degrees
        self.rotate(angle_degrees)

    def rotate(self, angle_degrees):
        # Calculate the rotation in radians
        angle_radians = math.radians(angle_degrees)

        # Get the maximum value count from the tileset

        # Create a new Bitmap for the rotated TileGrid
        rotated_bitmap = displayio.Bitmap(self.width, self.height, self.max_cols)

        # Rotate the TileGrid by updating pixel data in the new Bitmap
        for y in range(self.height):
            for x in range(self.width):
                original_x = x - self.width // 2
                original_y = y - self.height // 2
                new_x = int(
                    original_x * math.cos(angle_radians)
                    - original_y * math.sin(angle_radians)
                    + self.width // 2
                )
                new_y = int(
                    original_x * math.sin(angle_radians)
                    + original_y * math.cos(angle_radians)
                    + self.height // 2
                )
                if 0 <= new_x < self.width and 0 <= new_y < self.height:
                    rotated_bitmap[x, y] = self[new_x, new_y]

        # Update the pixel data with the rotated Bitmap
        self.bitmap = rotated_bitmap

        # Update the angle attribute for future reference
        self.angle_degrees = angle_degrees

    def set_position(self, x, y):
        self.x = x
        self.y = y

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

display = HX8357(display_bus, width=480, height=320, rotation=180)

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
rocket_tile_grid = RotatableTileGrid(art_sprite, pixel_shader=art_palette, width = 2, height = 2, tile_width = TILE_WIDTH, tile_height = TILE_HEIGHT, max_cols=ROCKET_COLORS)

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
#rocket_tile_grid.x = int(SCREEN_WIDTH / 3)

# Set position of groups
planet_group.y = int(SCREEN_HEIGHT - (earth_tile_grid.height * TILE_HEIGHT * PLANET_SCALE))
#rocket_group.x = int(SCREEN_WIDTH / 6)
#rocket_group.y = int(SCREEN_HEIGHT / 2)

# Scale up the planet group so the planets are bigger
planet_group.scale = PLANET_SCALE

# Need to make a list of points for the rocket to follow. X, y, rotation
rocket_anim_pts = [(int((earth_tile_grid.width*PLANET_SCALE*TILE_WIDTH) - TWO_TILE_PAD), 
                    int(planet_group.y - TWO_TILE_PAD), 30), (int(SCREEN_WIDTH/3 + TWO_TILE_PAD),int(SCREEN_HEIGHT/5), 60), 
                    (int((moon_tile_grid.x * PLANET_SCALE) - TWO_TILE_PAD), int(planet_group.y - TWO_TILE_PAD), 40),(int(SCREEN_WIDTH/3 + TWO_TILE_PAD),int(SCREEN_HEIGHT/5), 140)]

# Main Display Context
screen = displayio.Group()

screen.append(planet_group)
screen.append(rocket_group)

display.show(screen)

while True:
    # Animate the rocket between the pts
    for pts in rocket_anim_pts:
        rocket_tile_grid.x = pts[0]
        rocket_tile_grid.y = pts[1]
        display.refresh()
        print("x: {x: > 5}\ty: {y: > 5}".format(x = pts[0], y = pts[1]))
        time.sleep(1.0)



