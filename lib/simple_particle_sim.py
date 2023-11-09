# SPDX-License-Identifier: MIT

import displayio
import random

class Particle:
    """
    A helper class representing individual particles in a particle system.
 
    Attributes:
        x (int): The screen space x position in pixels.
        y (int): The screen space y position in pixels.
        dx (int): The x axis velocity in pixels per update.
        dy (int): The y axis velocity in pixels per update.
        px (int): The previous screen space x position in pixels.
        py (int): The previous screen space y position in pixels.
    """
    def __init__(self, x: int, y: int, dx: int, dy: int):
        """
        Initializes a simple monochrome particle, displayed as a pixel.
 
        Parameters:
            x (int): The screen space x position in pixels.
            y (int): The screen space y position in pixels.
            dx (int): The x axis velocity in pixels per update.
            dy (int): The y axis velocity in pixels per update.
        """
        self.px = 0
        self.py = 0
        self.x = x
        self.y = y
        self.dx = dx 
        self.dy = dy
    
    def move(self):
        """
        Move the particle according to its velocity.
 
        Parameters:
            None
        """
        self.px = self.x
        self.py = self.y
        self.x += self.dx
        self.y += self.dy

    def is_out_of_bounds(self, screen_x, screen_y):
        """
        Check if the particles are .
 
        Parameters:
            None

        Returns:
            list: A list of booleans if the particle is out of bounds in the x or y axis, respectively.
        """
        return [self.x < 0 | self.x > screen_x, self.y < 0 | self.y > screen_y]
    

# Define a ParticleSystem class to manage the particles
class ParticleSystem(displayio.TileGrid):
    """
    A kind of Adafruit displayio TileGrid to contain and manage particles.
 
    Attributes:
        num_particles (int): The number of particles in the particle system.
        p_behavior (list): A list of two elements that are used to define the x and y velocity of particles in pixels.
    """
    def __init__(self, num_particles: int, screen_height: int, screen_width: int, p_behavior: list, start_x: int, start_y: int):
        """
        Initializes a TileGrid that contains the particles and updates them.
 
        Parameters:
            num_particles (int):
            screen_height (int):
            screen_width (int):
            p_behavior (list):
            start_x (int):
            start_y (int):

        """
        bitmap = displayio.Bitmap(screen_width, screen_height, 2)
        palette = displayio.Palette(2)
        palette[0] = 0x000000  # Background color (black)
        palette[1] = 0xFFFFFF  # Particle color (white)

        # Initialize the TileGrid using super()
        super().__init__(bitmap, pixel_shader=palette)

        # Initialize particles
        self.particles = [Particle(start_x, start_y, p_behavior[0], p_behavior[1]) for _ in range(num_particles)]

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
            print("Particle: {: >20} X: {: >20} {: >20} {: >20} {: >20}".format(self.particles.index(particle), particle.x, particle.y, particle.ppos, particle.dx))

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
