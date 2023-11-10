"""
This module implements a funny simulation called 'Solar System' using Python
and the Pygame library.

This is a zero-player simulation that simulates our Solar System. In the center
of the screen there is the Sun (since it is the center of the actual Solar
System). There are several planets orbiting around the Sun, but they do not
represent actual Planets.

Before running the simulation, the user is allowed to change the number of
planets, and also their colors, radius, and translation periods (see the
configuration file).

Pygame is a Python library that serves as a versatile framework for developing
2D games and multimedia applications. It provides a straightforward and
efficient way to manage graphics, sound, user input, and basic collision
detection.

KEYWORDS: Python, Pygame, Physics, YAML configuration files, Simulations, Space
"""

import os
import math
import random
from typing import Any, Dict, Tuple

import yaml
import pygame


class Sun:
    """
    Sun class. Represents the Sun in the Solar System simulation. The Sun is
    placed at the center of the screen since it is also the center of the
    actual Solar System. In this simulation, the Sun is a static star, and all
    the (invented) Planets orbit around it.
    """

    def __init__(
            self,
            screen_center: Tuple[int, int],
            radius: int,
            color: Tuple[int, int, int]
    ) -> None:
        """
        Initialize a Sun instance.

        :param screen_center: (x,y) coordinates of the center of the screen
        :param radius: radius of the Sun (in pixels)
        :param color: color of the Sun (in RGB format)
        :return: None
        """

        self.center = screen_center
        self.radius = radius
        self.color = color

    def draw(self, screen: pygame.surface) -> None:
        """
        Displays the Sun on the given 'screen' (pygame surface)

        :return: None
        """

        pygame.draw.circle(
            surface=screen,
            color=self.color,
            center=self.center,
            radius=self.radius
        )


class Planet:
    """
    Planet class. It represents a fictitious planet of our Solar System. It
    orbits endlessly around the Sun (center of the screen). This class
    leverages some Algebra concepts (two-dimensional vectors, perpendicularity)
    to compute the (x,y) coordinates so the Planet orbits around the Sun.
    """

    def __init__(
            self,
            init_center: Tuple[int, int],
            radius: int,
            translation_step: int,
            clockwise_translation: bool,
            color: Tuple[int, int, int],
            screen_center: Tuple[int, int],
    ) -> None:
        """
        Initialize a Planet instance.

        :param init_center: (x,y) coordinates of the initial center.
        :param radius: radius of the Planet
        :param translation_step: defines the translation period
        :param clockwise_translation: clockwise or counterclockwise translation
        :param color: color of the Planet (in RGB format)
        :param screen_center: used to know the relative position of the Planet
        :return: None
        """

        self.center = init_center
        self.radius = radius
        self.translation_step = translation_step
        self.clockwise_translation = clockwise_translation
        self.color = color
        self.screen_center = screen_center

        self.original_vector_norm = math.sqrt(
            (self.screen_center[0] - self.center[0]) ** 2 +
            (self.screen_center[1] - self.center[1]) ** 2
        )

    def update(self) -> None:
        """
        Updates the position of the Planets. Performs a small step towards the
        direction of movement that, at each time-step, ensures a circular orbit
        around the Sun. The direction of movement is computed as the
        perpendicular (orthogonal) vector of the vector from screen_center to
        planet_center. The step size is defined by the translation_step attr.
        Finally, scale the vector, so it has the original norm (and the orbit
        radius remains unmodified).

        :return: None
        """

        # Compute the vector from 'screen_center' to the center of the Planet
        v_x = self.screen_center[0] - self.center[0]
        v_y = self.screen_center[1] - self.center[1]
        # Compute the perpendicular vector to know to direction to move
        if self.clockwise_translation:
            v_perp_x, v_perp_y = v_y, - v_x
        else:  # counterclockwise translation
            v_perp_x, v_perp_y = - v_y, v_x

        # 'translation_step' attribute is like a learning rate.
        # A small translation_step will result in a small step along the
        # direction of movement (v_perp), and the original orbits will suffer
        # smaller variations. A large translation_step will result in a faster
        # translation movement (larger step at each iteration) but the original
        # orbit's radius will suffer larger variations.
        new_center_x = self.translation_step * v_perp_x + self.center[0]
        new_center_y = self.translation_step * v_perp_y + self.center[1]
        new_vector_norm = math.sqrt(
            (self.screen_center[0] - new_center_x) ** 2 +
            (self.screen_center[1] - new_center_y) ** 2
        )
        # Keep the original vector norm! i.e. keep the same translation radius
        # Since the step towards the direction of movement modifies (expands)
        # the orbit, we have to do something to keep it constant.
        # We will scale the vector, so it has the original vector norm.
        new_center_x = (
                self.screen_center[0] + (new_center_x - self.screen_center[0])
                / new_vector_norm * self.original_vector_norm
        )
        new_center_y = (
                self.screen_center[1] + (new_center_y - self.screen_center[1])
                / new_vector_norm * self.original_vector_norm
        )
        self.center = (new_center_x, new_center_y)

    def draw(self, screen: pygame.surface) -> None:
        """
        Displays the Planet on the given 'screen' (pygame surface)

        :return: None
        """

        pygame.draw.circle(
            surface=screen,
            color=self.color,
            center=self.center,
            radius=self.radius
        )


class SolarSystem:
    """
    SolarSystem class. It simulates the physics of our solar system: the Sun is
    the center of the solar system, and there are a set of planets that orbit
    around it.
    """

    def __init__(self) -> None:
        """
        Initialize a SolarSystem instance.
        """

        # Read the configuration file
        self._dir_path = ''  # updated in '_get_config' method
        self._config = self._get_config()

        self.background_image = pygame.image.load(
            self._dir_path + '/images/' + self._config['background_image']
        )
        self.background_image = pygame.transform.scale(
            surface=self.background_image,
            size=(self._config['screen_width'], self._config['screen_height'])
        )

        # Initialize the Pygame elements
        pygame.init()
        self._screen = pygame.display.set_mode(
            (self._config['screen_width'], self._config['screen_height'])
        )
        pygame.display.set_caption(self._config['screen_caption'])
        self._clock = pygame.time.Clock()

        _screen_center = (
            self._config['screen_width'] // 2,
            self._config['screen_height'] // 2
        )
        # Initialize the sun in the center of the screen
        self.sun = Sun(
            screen_center=_screen_center,
            radius=self._config['sun_radius'],
            color=self._config['sun_color']
        )

        # Initialize the planets and store them in a list
        self.planets_list = []
        next_y = self.sun.radius + self._config['intra_planets_distance']
        next_y = _screen_center[1] - next_y
        for i in range(self._config['n_planets']):
            next_y -= self._config['planets_radius'][i]
            planet = Planet(
                init_center=(self._config['screen_width'] // 2, next_y),
                radius=self._config['planets_radius'][i],
                translation_step=self._config['planets_translation_steps'][i],
                clockwise_translation=random.choice((False, True)),
                color=self._config['planets_colors'][i],
                screen_center=_screen_center
            )
            self.planets_list.append(planet)
            next_y -= planet.radius + self._config['intra_planets_distance']

    def _get_config(self) -> Dict[str, Any]:
        """
        Read the configuration file and return it as a python dictionary.
        The configuration file is called 'solar_system/config.yml'
        It also set the value to '_dir_path' attribute

        :return: configuration dictionary
        """

        this_file_path = os.path.abspath(__file__)
        this_project_dir_path = '/'.join(this_file_path.split('/')[:-1])
        self._dir_path = this_project_dir_path
        config_path = this_project_dir_path + '/config.yml'

        with open(config_path, 'r') as yml_file:
            config = yaml.safe_load(yml_file)[0]['config']
        return config

    @staticmethod
    def process_events() -> bool:
        """
        Process the actions of the user:
            - if user wants to end the simulation: quit pygame

        :return: whether the simulation is running
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def run_logic(self) -> None:
        """
        Run the logic of the simulation:
            - Update the positions of every the Planets.

        :return: None
        """

        for planet in self.planets_list:
            planet.update()

    def draw(self) -> None:
        """
        Display the elements of the simulation on the 'screen' attribute.

        :return: None
        """

        self._screen.blit(self.background_image, (0, 0))
        self.sun.draw(screen=self._screen)
        for planet in self.planets_list:
            planet.draw(screen=self._screen)
        pygame.display.update()

    def clock_tick(self) -> None:
        """
        Updates the pygame clock (attribute '_clock')

        :return: None
        """

        self._clock.tick(self._config['pygame_clock_tick'])


if __name__ == '__main__':
    solar_system = SolarSystem()

    running = True
    while running:
        running = solar_system.process_events()
        solar_system.run_logic()
        solar_system.draw()
        solar_system.clock_tick()

    pygame.quit()
