# SPDX-License-Identifier: MIT

import board
import displayio
import random
import time
from adafruit_hx8357 import HX8357

# Release any resources currently in use for the displays
displayio.release_displays()

# Pin definitions
SPI = board.SPI()
TFT_CS = board.D24
TFT_DC = board.D25
RST = board.D7

# Define screen dimensions in pixels
WIDTH = 480
HEIGHT = 320

# Particle Attributes
NUM_PARTICLES = 50
MAX_PARTICLE_SPEED = 20

# Display object
display_bus = displayio.FourWire(SPI, command=TFT_DC, chip_select=TFT_CS, reset=RST)
display = HX8357(display_bus, width=WIDTH, height=HEIGHT)

# Define a Particle class to represent individual particles
class Particle:
    def __init__(self, x: int, y: int, max_speed: int = 2):
        self.ppos = 0
        self.x = x
        self.y = y
        self.dx = -random.randint(1, max_speed)  # Negative x velocity for leftward movement

    def move(self):
        self.ppos = self.x
        self.x += self.dx

    def is_out_of_bounds(self):
        return self.x < 0

# Define a ParticleSystem class to manage the particles
class ParticleSystem(displayio.TileGrid):
    def __init__(self, num_particles: int, screen_height: int, screen_width: int):
        # Create a bitmap and a palette
        bitmap = displayio.Bitmap(screen_width, screen_height, 2)
        palette = displayio.Palette(2)
        palette[0] = 0x000000  # Background color (black)
        palette[1] = 0xFFFFFF  # Particle color (white)

        # Initialize the TileGrid using super()
        super().__init__(bitmap, pixel_shader=palette)

        # Initialize particles
        self.particles = [Particle(WIDTH - 1, random.randint(0, HEIGHT - 1), MAX_PARTICLE_SPEED) for _ in range(num_particles)]

    def update(self):
        for particle in self.particles:
            particle.move()
            if particle.x + particle.dx < 0 :
                self.bitmap[particle.ppos, particle.y] = 0
            else:
                self.bitmap[particle.x, particle.y] = 1
                self.bitmap[particle.ppos, particle.y] = 0

    def remove_out_of_bounds(self):
        num_stale_particles = len(self.particles)
        self.particles = [particle for particle in self.particles if not particle.is_out_of_bounds()]
        for dead_particle in range(0,num_stale_particles-len(self.particles)):
            self.particles.append(Particle(WIDTH - 1, random.randint(0, HEIGHT - 1), MAX_PARTICLE_SPEED))

    def print_particle_list(self):
        for particle in self.particles:
            print("{: >20} {: >20} {: >20} {: >20}".format(self.particles.index(particle), particle.x, particle.ppos, particle.dx))

particle_system = ParticleSystem(NUM_PARTICLES, HEIGHT, WIDTH)
group = displayio.Group()
group.append(particle_system)
display.show(group)

while True:
    # Update and draw particles
    particle_system.update()
    particle_system.remove_out_of_bounds()

    # Redraw the TileGrid to display the updated particles
    display.refresh()

    # Wait for a short time to control the speed of the effect
    time.sleep(0.01)
