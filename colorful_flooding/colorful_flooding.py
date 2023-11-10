"""
This is a module that implements a funny simulation called 'Colorful Flooding'
using Python and the Pygame and Pymunk libraries.

In this simulation, there are some sources that generate balls that fill the
screen until you press the Space Bar. When the Space Bar is pressed, no more
balls are generated. Instead, the balls fall and disappear until there are
zero of them.

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

KEYWORDS: Pygame, Pymunk, YAML, Simulations, Physics using Python, Flooding.
"""

import os
import random
from typing import Any, Dict, Tuple

import pygame
import pymunk
import yaml


class Ball:
    """
    Ball class. Object that is created to flood the screen. It is represented
    as a dynamic Pymunk body with a circular shape.
    """

    def __init__(
            self,
            center: Tuple[int, int],
            mass: int,
            radius: int,
            elasticity: float,
            friction: float,
            color: Tuple[int, int, int],
    ):
        """
        Initialize a Ball instance.

        :param center: (x,y) initial coordinates of the ball
        :param mass: mass of the Ball
        :param radius: radius of the Ball (circle)
        :param elasticity: elasticity of the shape. float between 0 and 1.
        :param friction: friction coefficient. float between 0 and 1.
        :param color: color in RGB format
        """

        self.color = color  # in RGB format

        # Create the Pymunk Body of the Ball
        self.body = pymunk.Body(mass=mass, moment=1)
        self.body.position = center

        # Create the Pymunk Shape (Circle) of the Ball
        self.shape = pymunk.Circle(self.body, radius=radius)
        self.shape.elasticity = elasticity
        self.shape.friction = friction

    def is_out_of_the_screen(self, screen_height: int) -> bool:
        """
        Checks whether the Ball is out of the screen (visible or not).
        If it is out of the screen, we should remove it since it is no longer
        visible. The only way to leave the screen is when the bottom segment
        is removed.

        :param screen_height: height of the screen to know the screen limits
        return: whether the SmallBall is out of the screen
        """

        return self.body.position[1] - self.shape.radius // 2 > screen_height

    def draw(self, screen: pygame.surface) -> None:
        """
        Display the Ball on the given 'screen' (pygame surface)

        :param screen: pygame surface where the Ball is displayed
        :return: None
        """

        pygame.draw.circle(
            surface=screen,
            color=self.color,
            center=self.body.position,
            radius=self.shape.radius
        )


class ColorfulFlooding:
    """
    ColorfulFlooding class. Implements the logic of the simulation. Generates
    balls from the defined sources. Deals with the interaction with the user.
    """

    def __init__(self) -> None:
        """
        Initialize a ColorfulFlooding instance.
        """

        # Read the configuration file
        self._config = self._get_config()

        # Initialize the Pygame elements
        pygame.init()
        self._screen = pygame.display.set_mode(
            (self._config['screen_width'], self._config['screen_height'])
        )
        pygame.display.set_caption(self._config['screen_caption'])
        self._clock = pygame.time.Clock()

        # Create a Pymunk Space
        self.space = pymunk.Space()
        self.space.gravity = (0, self._config['gravity'])  # vertical gravity

        # Define the (x,y) coordinates of the sources. They are placed at the
        # same height, and they are horizontally equidistant.
        sources_y = self._config['screen_height'] // 5
        sources_intra_distance = (
                self._config['screen_width'] // (self._config['n_sources'] + 1)
        )
        self.sources_positions = [
            (k * sources_intra_distance, sources_y)
            for k in range(1, self._config['n_sources'] + 1)
        ]

        # Define the limits of the Screen as Pymunk Segments (Static and
        # invisible objects). First, let's create the four screen corners:
        tl = (0, 0)  # Top Left corner
        tr = (self._config['screen_width'], 0)  # Top Right corner
        bl = (0, self._config['screen_height'])  # Bottom Left corner
        br = (self._config['screen_width'], self._config['screen_height'])

        # The bottom Segment is special because we will remove it when the
        # simulation ends, so we save its body and shape in an attribute
        _screen_bottom_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self._screen_bottom = (
            _screen_bottom_body,
            pymunk.Segment(body=_screen_bottom_body, a=bl, b=br, radius=4)
        )

        # Create the Left, Right, and Upper Segments
        _screen_upper_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        _screen_upper_shape = pymunk.Segment(_screen_upper_body, tl, tr, 4)
        _screen_left_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        _screen_left_shape = pymunk.Segment(_screen_left_body, tl, bl, 4)
        _screen_right_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        _screen_right_shape = pymunk.Segment(_screen_right_body, tr, br, 4)

        # Add the three segments to the pymunk space
        self.space.add(
            *self._screen_bottom,
            _screen_upper_body, _screen_upper_shape,
            _screen_left_body, _screen_left_shape,
            _screen_right_body, _screen_right_shape
        )

        # Create a list to store the balls that are generated in the simulation
        self.balls_list = []

        # time-steps counter to know when to generate new balls
        self.counter = 0  # increases until self._config['create_balls_every']

        # If _remove_screen_bottom is True, no more balls are generated and the
        # bottom segment is removed, so the current balls fall and disappear.
        self._remove_screen_bottom = False

    @staticmethod
    def _get_config() -> Dict[str, Any]:
        """
        Read the configuration file and return it as a python dictionary.
        The configuration file is called 'colorful_flooding/config.yml'

        :return: configuration dictionary
        """

        this_file_path = os.path.abspath(__file__)
        this_project_dir_path = '/'.join(this_file_path.split('/')[:-1])
        config_path = this_project_dir_path + '/config.yml'

        with open(config_path, 'r') as yml_file:
            config = yaml.safe_load(yml_file)[0]['config']
        return config

    def process_events(self) -> bool:
        """
        Process the actions of the user:
            - if user wants to end the simulation: quit pygame
            - if user presses Space Bar, remove the bottom segment

        :return: whether the simulation is running
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._remove_screen_bottom = True
        return not self._remove_screen_bottom or self.balls_list

    def run_logic(self) -> None:
        """
        Run the logic of the simulation:
            - Update the positions of the Balls according to the gravity.
            - Create new balls if the bottom segment has not been removed yet
            - Remove those balls that are no longer visible (out of screen)
            - Remove the bottom segment if needed

        :return: None
        """

        self.space.step(1/60)

        # Create new balls if the bottom segment has not been removed yet

        self.counter += 1
        if (not self._remove_screen_bottom and
                self.counter == self._config['create_balls_every']):
            self.counter = 0
            for source_x, source_y in self.sources_positions:
                new_ball = Ball(
                    center=(source_x + random.choice(seq=(-1, 1)), source_y),
                    mass=self._config['mass'],
                    radius=self._config['radius'],
                    elasticity=self._config['elasticity'],
                    friction=self._config['friction'],
                    color=random.choices(population=range(255), k=3)
                )
                self.balls_list.append(new_ball)
                self.space.add(new_ball.body, new_ball.shape)

        # If _remove_screen_bottom, remove the bottom segment.
        # Add a TRY/EXCEPT statement to remove the screen_bottom only once
        if self._remove_screen_bottom:
            try:
                self.space.remove(*self._screen_bottom)
            except AssertionError:
                pass

        # Remove those balls that are no longer visible (out of screen)
        for ball in self.balls_list:
            if ball.is_out_of_the_screen(self._config['screen_height']):
                self.balls_list.remove(ball)
                self.space.remove(ball.body, ball.shape)

    def draw(self) -> None:
        """
        Display the elements of the simulation on the 'screen' attribute.

        :return: None
        """

        self._screen.fill(self._config['background_color'])  # background
        for ball in self.balls_list:
            ball.draw(screen=self._screen)
        pygame.display.update()

    def clock_tick(self) -> None:
        """
        Updates the pygame clock (attribute '_clock')

        :return: None
        """

        self._clock.tick(self._config['pygame_clock_tick'])


if __name__ == '__main__':
    colorful_flooding = ColorfulFlooding()

    running = True
    while running:
        running = colorful_flooding.process_events()
        colorful_flooding.run_logic()
        colorful_flooding.draw()
        colorful_flooding.clock_tick()

    pygame.quit()
