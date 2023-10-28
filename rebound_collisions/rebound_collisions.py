"""
This is a module that implements a funny simulation called 'Rebound Collisions'
using Python and the Pygame and Pymunk libraries. In this simulation, the user
uses their mouse to creates new Circles of different colors that move across
the screen while colliding with each other.

The user is allowed to change the physics of the simulation.
More information can be found in 'rebound_collisions/config.yml'.

Pygame is a Python library that serves as a versatile framework for developing
2D games and multimedia applications. It provides a straightforward and
efficient way to manage graphics, sound, user input, and basic collision
detection.

PyMunk is a Python library that extends Pygame by adding robust 2D physics
simulation capabilities, allowing developers to create realistic physics
interactions within their 2D games and simulations. It provides functionality
for creating and managing physics objects such as rigid bodies, shapes,
constraints, and handling complex collision detection and response.

PyMunk's integration with Pygame simplifies the process of combining graphics
with dynamic physics, making it a valuable tool for those seeking to develop
games or simulations with compelling and lifelike physics behavior.

KEYWORDS: Pygame, Pymunk, YAML, Simulations, Physics using Python.
"""


import os
import random
from typing import Dict, Any, Tuple

import yaml
import pygame
import pymunk


class Circle:
    """
    Circle class. Implements the functionalities of a Circle that moves across
    the screen and collides with other Circles. Each Circle is represented as
    a pymunk circle, with the corresponding 'body' and 'shape' attributes.

    A Circle is not allowed to exit the screen. When it hits the limits of the
    screen, its direction of movement is changed.
    """

    def __init__(
            self,
            mass: int,
            moment: int,
            init_center: Tuple[int, int],
            radius: int,
            velocity: Tuple[int, int],
            color: Tuple[int, int, int]
    ) -> None:
        """
        Initialize a Circle class.

        :param mass: physical mass of the Circle object
        :param moment: moment of inertia
        :param init_center: (x,y) coordinates of the initial center
        :param radius: radius of the Circle
        :param velocity: (v_x, v_y) velocities in both X and Y directions
        :param color: Circle's color in RGB format
        :return: None
        """

        # Create the Circle using the Pymunk library:
        # - body: represents the Circle in the physical world and has
        #       properties like mass, position, velocity, and rotation.
        # -shape: attached to a body and defines the geometry of the object.
        #       They are used for collision detection and response.

        self.body = pymunk.Body(
            mass=mass, moment=moment, body_type=pymunk.Body.DYNAMIC
        )
        self.body.position = init_center  # initial center
        self.body.velocity = velocity  # (velocity_x, velocity_y)
        self.color = color  # in RBG format
        self.radius = radius

        self.shape = pymunk.Circle(body=self.body, radius=self.radius)
        # 'Elasticity' is how "bouncy" an object is when it collides with
        # another object. It represents the ability of an object to rebound or
        # bounce off another object after a collision.
        self.shape.elasticity = 1  # 1 represents perfectly elastic collision
        # 'Friction' is a property that determines how much two objects will
        # resist sliding against each other when they are in contact.
        self.shape.friction = 0  # zero resistance to sliding

    def update(self, screen_width: int, screen_height: int) -> None:
        """
        Updates the direction of the velocity when the Circle hits the screen
        limits.

        :param screen_width: screen's width (in pixels)
        :param screen_height: screen's height (in pixels)
        :return: None
        """

        velocity_x, velocity_y = self.body.velocity
        x, y = self.body.position
        if x + self.radius > screen_width or x - self.radius < 0:
            velocity_x = - velocity_x
        if y + self.radius > screen_height or y - self.radius < 0:
            velocity_y = - velocity_y
        self.body.velocity = (velocity_x, velocity_y)

    def draw(self, screen: pygame.surface):
        """
        Display the Circle on the given 'screen'.

        :param screen: pygame Surface where the Circle is displayed
        :return: None
        """

        pygame.draw.circle(
            surface=screen,
            color=self.color,
            center=self.body.position,
            radius=self.radius
        )


class ReboundCollisions:
    """
    ReboundCollisions class. This class builds the environment in which several
    Circles move across. This class deals with the coordination of the
    different elements involved in the simulation, and with the collision
    between Circles. This class allows the user to create new Circles by
    clicking the mouse.

    In PyMunk, a "space" (used here in this class) is a fundamental concept and
    object that represents the environment or the physics simulation world.
    Think of it as the container that holds and manages all the physical
    entities, including bodies, shapes, constraints, and the rules governing
    their behavior.
    """

    def __init__(self) -> None:
        """
        Initialize a ReboundCollision instance.
        """

        # Read the configuration file
        self._config = self._get_config()

        self._mouse_pos = None  # (x,y) coordinates of mouse clicks (if any)

        # Initialize the Pygame elements
        pygame.init()
        self._screen = pygame.display.set_mode(
            (self._config['screen_width'], self._config['screen_height'])
        )
        self._clock = pygame.time.Clock()

        # Create a Pymunk Space
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)  # (x,y) direction of gravity (disable it)

        # Create a list to store the different Circles, and create a random
        # circles in the center of the screen
        self.circle_list = []
        self._create_and_add_a_new_circle(
            center=(
                self._config['screen_width'] // 2,
                self._config['screen_height'] // 2
            )
        )

    @staticmethod
    def _get_config() -> Dict[str, Any]:
        """
        Read the configuration file and return it as a python dictionary.
        The configuration file is called 'rebound_collisions/config.yml'

        :return: configuration dictionary
        """

        this_file_path = os.path.abspath(__file__)
        this_project_dir_path = '/'.join(this_file_path.split('/')[:-1])
        config_path = this_project_dir_path + '/config.yml'

        with open(config_path, 'r') as yml_file:
            config = yaml.safe_load(yml_file)[0]['config']
        return config

    def _create_and_add_a_new_circle(self, center: Tuple[int, int]) -> None:
        """
        Creates and adds a new random circle to the simulation environment.
        The random characteristics of this circle are bounded (min and max
        values) following the 'config.yml' file.

        :param center: (x,y) where the new Circle is placed
        :return: None. The attribute 'circle_list' is updated.
        """

        random_mass = random.randrange(
            start=self._config['min_mass'],
            stop=self._config['max_mass']
        )
        random_moment = random.randrange(
            start=self._config['min_moment'],
            stop=self._config['max_moment']
        )
        random_radius = random.randrange(
            start=self._config['min_radius'],
            stop=self._config['max_radius']
        )
        random_velocity_x = random.randrange(
            start=self._config['min_velocity_x'],
            stop=self._config['max_velocity_x']
        ) * random.choice(seq=(-1, 1))  # randomly select either left or right
        random_velocity_y = random.randrange(
            start=self._config['min_velocity_y'],
            stop=self._config['max_velocity_y']
        ) * random.choice(seq=(-1, 1))  # randomly select either up or down
        random_color = random.choices(population=range(255), k=3)

        # Create a new Circle with the random characteristic defined above
        new_circle = Circle(
            mass=random_mass,
            moment=random_moment,
            init_center=center,
            radius=random_radius,
            velocity=(random_velocity_x, random_velocity_y),
            color=random_color
        )
        # Add the new Circle to the list of circles and to the pymunk space
        self.circle_list.append(new_circle)
        self.space.add(new_circle.body, new_circle.shape)

    def process_events(self) -> bool:
        """
        Process the actions carried out by the user.
            - Mouse click: create a new random Circle in that mouse position

        :return: whether the simulation is running
        """

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                self._mouse_pos = pygame.mouse.get_pos()

        return True

    def run_logic(self) -> None:
        """
        Update every Circle instance:
            - the space physics' move forward in time
            - change velocities for those Circles which are getting out of the
                screen limits.
            - create new Circles if the computer mouse is pressed
            - update the screen caption with the current number of circles

        :return: None
        """

        # Pymunk Spaces update the positions and velocities of objects
        # accordingly in discrete time step using the 'step' method
        self.space.step(1/60)

        # Update every Circle (change direction of velocity if they hit the
        # limits of the screen
        for circle in self.circle_list:
            circle.update(
                screen_width=self._config['screen_width'],
                screen_height=self._config['screen_height']
            )

        # If the mouse is pressed, create a new random Circle class instance at
        # the click position.
        if self._mouse_pos:
            self._create_and_add_a_new_circle(center=self._mouse_pos)
            self._mouse_pos = None  # wait for the next mouse click

        # Update the screen caption. Show the number of active Circles.
        pygame.display.set_caption(
            self._config['screen_caption'].format(
                n_circles=len(self.circle_list)
            )
        )

    def draw(self) -> None:
        """
        Display the elements of the simulation on the '_screen' attribute.

        :return: None
        """

        self._screen.fill(self._config['background_color'])
        for circle in self.circle_list:
            circle.draw(self._screen)
        pygame.display.update()

    def clock_tick(self) -> None:
        """
        Updates the pygame clock (attribute '_clock')

        :return: None
        """

        self._clock.tick(self._config['pygame_clock_tick'])


if __name__ == '__main__':
    rebound_collisions = ReboundCollisions()

    running = True
    while running:
        running = rebound_collisions.process_events()
        rebound_collisions.run_logic()
        rebound_collisions.draw()
        rebound_collisions.clock_tick()

    pygame.quit()
