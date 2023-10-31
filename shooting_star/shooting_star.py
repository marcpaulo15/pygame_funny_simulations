"""
This is a module that implements a funny simulation called 'Shooting Star'
using Python and the Pygame and Pymunk libraries. In this simulation, you
use your mouse to creates a colorful shooting star. You have to hold down
your mouse while moving it in order to create the shooting star effect.

You are allowed to change the physics of the simulation.
More information can be found in 'shooting_star/config.yml'.

Pygame is a Python library that serves as a versatile framework for developing
2D games and multimedia applications. It provides a straightforward and
efficient way to manage graphics, sound, user input, and basic collision
detection.

Pymunk is a Python library that extends Pygame by adding robust 2D physics
simulation capabilities, allowing developers to create realistic physics
interactions within their 2D games and simulations. It provides functionality
for creating and managing physics objects such as rigid bodies, shapes,
constraints, and handling complex collision detection and response.

Pymunk's integration with Pygame simplifies the process of combining graphics
with dynamic physics, making it a valuable tool for those seeking to develop
games or simulations with compelling and lifelike physics behavior.

KEYWORDS: Pygame, Pymunk, YAML, Simulation, Physics using Python, Shooting Star
"""

import os
import random
from typing import Any, Dict

import pygame
import pymunk
import yaml
from typing import Tuple


class Spark:
    """
    Spark class. Implements the functionalities of a Spark that is created when
    the user clicks the computer mouse. Once created, the Spark gets smaller
    over time until it disappears. Each Spark is represented as a pymunk circle
    with the corresponding 'body' and 'shape' attributes.
    """

    def __init__(
            self,
            mouse_pos: Tuple[int, int],
            color: Tuple[int, int, int],
            radius: int,
            lifespan: int
    ) -> None:
        """
        Initialize a Spark instance.

        :param mouse_pos: (x,y) coordinates where the Spark is placed (mouse)
        :param color: color of the Spark in RGB format
        :param radius: initial radius of the Spark, it decreases over time
        :param lifespan: number of time-steps in which the Spark is visible
        :return: None
        """

        self.color = color
        self.radius = radius
        self._init_radius = radius
        self.lifespan = lifespan
        self._time_steps_left = lifespan
        self.spark_list = []

        # Create the Spark using the Pymunk library:
        # - body: represents the Spark in the physical world and has
        #       properties like mass, position, velocity, and rotation.
        # -shape: attached to a body and defines the geometry of the object.
        #       They are used for collision detection and response.
        self.body = pymunk.Body(mass=10, moment=10)
        self.body.position = mouse_pos  # (x,y) coordinates of the mouse click
        self.shape = pymunk.Circle(self.body, self.radius)

    def zero_radius(self) -> bool:
        """
        Reduces the 'radius' based on the 'lifespan' and the 'time_steps_left'
        Returns whether the radius is zero. When the radius is zero, the Spark
        is no longer visible in the screen, so it should be removed to free the
        memory.

        :return: Whether the radius is zero
        """

        self._time_steps_left -= 1
        self.radius = (
                (self._init_radius * self._time_steps_left) // self.lifespan
        )
        return self.radius == 0

    def draw(self, screen: pygame.surface) -> None:
        """
        Display the Spark on the given 'screen'.

        :return: None
        """

        pygame.draw.circle(
            surface=screen,
            color=self.color,
            center=self.body.position,
            radius=self.radius
        )


class ShootingStar:
    """
    ShootingStar class. This class enables the user to use their mouse to
    create a shooting star effect. This class deals with the coordination of
    the different Sparks involved in visual effect, and with the correct
    reception of the mouse position at each time step.

    In Pymunk, a "space" (used here in this class to simulate gravity) is a
    fundamental concept and object that represents the environment or the
    physics simulation world. Think of it as the container that holds and
    manages all the physical entities, including bodies, shapes, constraints,
    and the rules governing their behavior.
    """

    def __init__(self) -> None:
        """
        Initialize a ShootingStar instance.
        """

        # Read the configuration file
        self._config = self._get_config()

        self._mouse_pos = None  # (x,y) coordinates of mouse clicks (if any)
        self._is_mouse_still_pressed = False  # If True, create more Sparks
        self.spark_list = []  # list of Sparks with non-zero radius

        # Initialize the Pygame elements
        pygame.init()
        self._screen = pygame.display.set_mode(
            (self._config['screen_width'], self._config['screen_height'])
        )
        pygame.display.set_caption(self._config['screen_caption'])
        self._clock = pygame.time.Clock()

        # Create a Pymunk Space with vertical gravity
        self.space = pymunk.Space()
        self.space.gravity = (0, self._config['gravity'])  # (X,Y) directions

    @staticmethod
    def _get_config() -> Dict[str, Any]:
        """
        Read the configuration file and return it as a python dictionary.
        The configuration file is called 'shooting_star/config.yml'

        :return: configuration dictionary
        """

        this_file_path = os.path.abspath(__file__)
        this_project_dir_path = '/'.join(this_file_path.split('/')[:-1])
        config_path = this_project_dir_path + '/config.yml'

        with open(config_path, 'r') as yml_file:
            config = yaml.safe_load(yml_file)[0]['config']
        return config

    def _create_and_add_a_new_spark(self, mouse_pos: Tuple[int, int]) -> None:
        """
        Creates and adds a new random Spark to create the visual effect of a
        shooting start. The random characteristics of the new Spark are bounded
        (min and max values) following the 'shooting_star/config.yml' file.

        :param mouse_pos: (x,y) coordinates of current position of the mouse
        :return: None. The attribute 'spark_list' is updated.
        :return: None
        """

        random_color = random.choices(population=range(255), k=3)
        random_radius = random.randrange(
            start=self._config['min_radius'],
            stop=self._config['max_radius']
        )
        random_lifespan = random.randrange(
            start=self._config['min_lifespan'],
            stop=self._config['max_lifespan']
        )

        # Add a random element -1 or +1 to prevent Sparks (circles) from
        # stacking vertically when the mouse is hold down but not moving.
        mouse_pos_ = (mouse_pos[0]+random.choice((-1, 1)), mouse_pos[1])

        # Create a new Spark with the random characteristic defined above
        new_spark = Spark(
            mouse_pos=mouse_pos_,
            color=random_color,
            radius=random_radius,
            lifespan=random_lifespan
        )
        # Add the new Spark to the list of sparks and to the pymunk space
        self.spark_list.append(new_spark)
        self.space.add(new_spark.body, new_spark.shape)

    def process_events(self) -> bool:
        """
        Process the actions carried out by the user.
            - Mouse click: create a set of Sparks in the mouse position

        :return: whether the simulation is running
        """

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                self._is_mouse_still_pressed = True
            if event.type == pygame.MOUSEBUTTONUP:
                self._is_mouse_still_pressed = False

        return True

    def run_logic(self) -> None:
        """
        Update every Spark instance:
            - the space physics' move forward in time ('step' method)
            - check if there mouse is still pressed in order to create more
                Sparks at the current position of the mouse
            - updates (decreases) the radius of the current Sparks
            - removes those sparks having a zero radius

        :return: None
        """

        # Pymunk Spaces update the positions and velocities of objects
        # accordingly in discrete time step using the 'step' method
        self.space.step(1/60)

        # If the mouse is still pressed, create new sparks
        if self._is_mouse_still_pressed:
            for _ in range(self._config['new_sparks_per_time_step']):
                self._create_and_add_a_new_spark(
                    mouse_pos=pygame.mouse.get_pos()
                )

        # Decrease the radius of the Sparks and remove those with zero radius
        for spark in self.spark_list:
            if spark.zero_radius():
                self.spark_list.remove(spark)

    def draw(self) -> None:
        """
        Display the elements of the simulation on the '_screen' attribute.

        :return: None
        """

        self._screen.fill(self._config['background_color'])
        for spark in self.spark_list:
            spark.draw(self._screen)
        pygame.display.update()

    def clock_tick(self) -> None:
        """
        Updates the pygame clock (attribute '_clock')

        :return: None
        """

        self._clock.tick(self._config['pygame_clock_tick'])


if __name__ == '__main__':
    shooting_star = ShootingStar()

    running = True
    while running:
        running = shooting_star.process_events()
        shooting_star.run_logic()
        shooting_star.draw()
        shooting_star.clock_tick()

    pygame.quit()
