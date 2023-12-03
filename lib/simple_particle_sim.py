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

    def is_out_of_bounds(self, bound_x, bound_y):
        """
        Check if the particles are out of bounds.
 
        Parameters:
            None

        Returns:
            list: A list of booleans if the particle is out of bounds in the x or y axis, respectively.
        """
        return [self.x < 0 or self.x > bound_x, self.y < 0 or self.y > bound_y]
    

# Define a ParticleSystem class to manage the particles
class ParticleSystem(displayio.TileGrid):
    """
    A kind of Adafruit displayio TileGrid to contain and manage particles.
 
    Attributes:
        num_particles (int): The number of particles in the particle system.
        p_behavior (list): A list of two elements that are used to define the x and y velocity of particles in pixels.
    """
    def __init__(self, num_particles: int, system_height: int, system_width: int, min_dx: int, min_dy: int, max_dx: int, max_dy: int, start_x: int, start_y: int, rand_x: bool = False, rand_y: bool = False):
        """
        Initializes a TileGrid that contains the particles and updates them.
 
        Parameters:
            num_particles (int):
            system_height (int):
            system_width (int):
            min_dx (int):
            min_dy (int):
            max_dx (int):
            max_dy (int):
            start_x (int):
            start_y (int):
            rand_x (bool):
            rand_y (bool):

        """
        bitmap = displayio.Bitmap(system_width, system_height, 2)
        self.system_width = system_width
        self.system_height = system_height
        palette = displayio.Palette(2)
        palette[0] = 0x000000  # Background color (black)
        palette[1] = 0xFFFFFF  # Particle color (white)

        # Initialize the TileGrid using super()
        super().__init__(bitmap, pixel_shader=palette)

        # Initialize particles
        if rand_x and rand_y:
            if min_dy and max_dy == 0:
                self.particles = [Particle(random.randrange(0, system_width - 1), random.randrange(0, system_height), random.randrange(min_dx, max_dx), 0) for _ in range(num_particles)]
            else:
                self.particles = [Particle(random.randrange(0, system_width - 1), random.randrange(0, system_height), random.randrange(min_dx, max_dx), random.randrange(min_dy, max_dy)) for _ in range(num_particles)]
        elif rand_x:
            if min_dy and max_dy == 0:
                self.particles = [Particle(random.randrange(0, system_width - 1), start_y, random.randrange(min_dx, max_dx), random.randrange(min_dy, max_dy)) for _ in range(num_particles)]
            else:
                self.particles = [Particle(random.randrange(0, system_width - 1), start_y, random.randrange(min_dx, max_dx), 0) for _ in range(num_particles)]
        elif rand_y:
            if min_dy and max_dy == 0:
                self.particles = [Particle(start_x, random.randrange(0, system_height), random.randrange(min_dx, max_dx), random.randrange(min_dy, max_dy)) for _ in range(num_particles)]
            else:
                self.particles = [Particle(start_x, random.randrange(0, system_height), random.randrange(min_dx, max_dx), 0) for _ in range(num_particles)]
        else:
            if min_dy and max_dy == 0:
                self.particles = [Particle(start_x, start_y, random.randrange(min_dx, max_dx), random.randrange(min_dy, max_dy)) for _ in range(num_particles)]
            else:
                self.particles = [Particle(start_x, start_y, random.randrange(min_dx, max_dx), 0) for _ in range(num_particles)]
        
        self.p_behavior = min_dx, max_dx, min_dy, max_dy

    def update(self):
        """
        Update each particle in the particle system, calling each particle's move() function. 
        This function updates pixels on the screen and the display should be refreshed soon after update.

        Parameters:
            None

        Returns:
            None
        """
        for particle in self.particles:
            particle.move()
            if particle.x + particle.dx < 0 or particle.y + particle.dy < 0:
                self.bitmap[particle.px, particle.py] = 0
            elif particle.x + particle.dx > (self.system_width - 1) or particle.y + particle.dy > (self.system_height - 1):
                self.bitmap[particle.px, particle.py] = 0
            else:
                self.bitmap[particle.x, particle.y] = 1
                self.bitmap[particle.px, particle.py] = 0

    def remove_out_of_bounds(self):
        """
        Check if each particle is out of bounds, and if so remove them from the system.

        Parameters:
            None

        Returns:
            None
        """
        num_stale_particles = len(self.particles)
        self.particles = [particle for particle in self.particles if not (particle.is_out_of_bounds(self.system_width, self.system_height)[0] or particle.is_out_of_bounds(self.system_width, self.system_height)[1])]
        for dead_particle in range(0,num_stale_particles-len(self.particles)):
            self.particles.append(Particle(self.system_width - 1, random.randint(0, self.system_height - 1), self.p_behavior[0], self.p_behavior[1]))

    def print_particle_list(self):
        """
        Print out the list of particles and their attributes.

        Parameters:
            None

        Returns:
            None
        """
        for particle in self.particles:
            print("Particle: {: >20} X: {: >20} Y: {: >20} Previous X: {: >20} Previous Y: {: >20} X Velocity: {: >20} Y Velocity{: >20}".format(
                self.particles.index(particle), particle.x, particle.y, particle.px, particle.py, particle.dx, particle.dy))