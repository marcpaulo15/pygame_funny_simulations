"""
This is a module that implements a funny simulation called 'Sand Clock'
using Python and the Pygame and Pymunk libraries. In this simulation, there are
some sand grains that flow from the upper bulb to the lower one by gravity.

You are allowed to tip over the clock (Space Bar) and to restart the simulation
('R' key). You are also allowed to change the gravity, the colors, and the mass
and radius of the sand grains. More information in 'sand_clock/config.yml'.

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

KEYWORDS: Pygame, Pymunk, YAML, Simulation, SandClock, SandTimer, HourGlass
"""

import os
import random
from typing import Tuple, Dict, Any

import yaml
import pymunk
import pygame


class SandGrain:
    """
    SandGrain class. The sand grains will flow from the upper bulb to the lower
    one by gravity.
    """

    desert_yellow = (255, 200, 0)  # color in RGB format

    def __init__(
            self,
            center: Tuple[int, int],
            radius: int,
            mass: int,
            color_type: str
    ) -> None:
        """
        Initialize a SandGrain instance.

        :param center: the (x,y) coordinates of the initial SandGrain center
        :param radius: radius of the SandGrain (circle)
        :param mass: mass of the SandGrain (pymunk body)
        :param color_type: either 'random' or 'yellow'
        :return: None
        """

        if color_type == 'random':
            self.color = random.choices(population=range(255), k=3)
        elif color_type == 'yellow':
            self.color = self.desert_yellow
        else:
            raise ValueError(
                "'color_type' must be either 'random' or 'yellow',"
                f"but {color_type} was given."
            )

        self.radius = radius

        # Create the pymunk Body (dynamic)
        self.body = pymunk.Body(mass=mass, moment=1)
        self.body.position = center

        # Create the pymunk Shape (circle)
        self.shape = pymunk.Circle(self.body, self.radius)

    def draw(self, screen: pygame.surface) -> None:
        """
        Display the SandGrain on the given 'screen' (pygame surface)

        :param screen: pygame surface where the SandGrain is displayed
        :return: None
        """

        pygame.draw.circle(
            surface=screen,
            color=self.color,
            center=self.body.position,
            radius=self.radius
        )


class SandClockStructure:
    """
    SandClockStructure class. It comprises two glass bulbs connected vertically
    by a narrow neck that allows a regulated flow of a substance from the upper
    bulb to the lower one by gravity. Typically, the upper and lower bulbs are
    symmetric so that the hourglass will measure the same duration regardless
    of orientation.
    """

    def __init__(
            self,
            center: Tuple[int, int],
            width: int,
            height: int,
            neck_width: int,
            line_width: int,
            line_color: Tuple[int, int, int]
    ) -> None:
        """
        Initialize a SandClockStructure instance.

        :param center: (x,y) coordinates of the center of the neck
        :param width: width of the SandClockStructure
        :param height: height of the SandClockStructure
        :param neck_width: width of the neck
        :param line_width: width of the lines thar represent the structure
        :param line_color: color of the lines (structure) in RGB format.
        """

        self.center = center
        self.width = width
        self.height = height
        self.line_width = line_width
        self.line_color = line_color

        # The 6 corners: Left(l) and Right(r) for Top(t), Neck(n), Bottom(b)
        tl = (center[0] - width//2, center[1] - height//2)  # Top Left
        tr = (center[0] + width//2, center[1] - height//2)  # Top Right
        nl = (center[0] - neck_width//2, center[1])  # Neck Left
        nr = (center[0] + neck_width//2, center[1])  # Neck Right
        bl = (center[0] - width//2, center[1] + height//2)  # Bottom Left
        br = (center[0] + width//2, center[1] + height//2)  # Bottom Right

        # Create a Pymunk Body for each of the six Segment of the structure
        self.body = (
            pymunk.Body(mass=1, moment=1, body_type=pymunk.Body.STATIC),
            pymunk.Body(mass=1, moment=1, body_type=pymunk.Body.STATIC),
            pymunk.Body(mass=1, moment=1, body_type=pymunk.Body.STATIC),
            pymunk.Body(mass=1, moment=1, body_type=pymunk.Body.STATIC),
            pymunk.Body(mass=1, moment=1, body_type=pymunk.Body.STATIC),
            pymunk.Body(mass=1, moment=1, body_type=pymunk.Body.STATIC)
        )

        # Create six Segments (shapes) that form the Box
        self.shape = (
            pymunk.Segment(body=self.body[0], a=tl, b=tr, radius=line_width),
            pymunk.Segment(body=self.body[1], a=tr, b=nr, radius=line_width),
            pymunk.Segment(body=self.body[2], a=nr, b=br, radius=line_width),
            pymunk.Segment(body=self.body[3], a=br, b=bl, radius=line_width),
            pymunk.Segment(body=self.body[3], a=bl, b=nl, radius=line_width),
            pymunk.Segment(body=self.body[3], a=nl, b=tl, radius=line_width)
        )

    def init_grain_random_position(self) -> Tuple[int, int]:
        """
        Returns a random (x,y) coordinates within the upper bulb boundaries.
        The motivation of this function is to create each SandGrain in a
        different position, so Pygame and Pymunk have it easier to display
        all the SandGrains in the first time-step.

        :return: randomly generated (x,y) coordinates within the upper bulb
        """

        # Compute the (x,y) top-left corner of the Structure
        tl = (self.center[0] - self.width//2, self.center[1] - self.height//2)
        # Let's model the descending diagonal from the top-left corner to the
        # left-neck point. This diagonal will be defined by the function:
        # y = m * x + b
        m = (tl[1] - self.center[1]) / (tl[0] - self.center[0])  # slope =Δy/Δx
        b = tl[1] - m * tl[0]  # b = y - m * x  [intercept]

        # Generate a random X coordinate (add and subtract some margins)
        x = random.randrange(start=tl[0] + 30, stop=self.center[0] - 15)
        # Find the maximum value for Y given the X value
        y_max = int(m * x + b)
        # Generate a random Y within the valid range
        y = random.randrange(start=tl[1] + 5, stop=y_max - 5)
        # Toss a coin and perform a horizontal flip to move the (x,y) coords to
        # the right part of the Structure (we computed the coordinates for the
        # left part, using the descending diagonal from top-left to left-neck)
        if random.random() > 0.5:
            x = self.center[0] - x + self.center[0]
        return x, y

    def draw(self, screen: pygame.surface) -> None:
        """
        Display the SandClockStructure on the given 'screen' (pygame surface)

        :param screen: surface on which the SandClockStructure is displayed
        :return: None
        """

        for segment in self.shape:
            pygame.draw.line(
                surface=screen,
                color=self.line_color,
                start_pos=segment.a,
                end_pos=segment.b,
                width=self.line_width
            )


class SandClock:
    """
    SandClock class. Simulates a Sand Clock (also known as Hourglass,
    Sandglass, or Sand Timer), which is a device used to measure the passage
    of time (but this implementation is NOT a real timer).

    This class creates a SandClockStructure and fills the upper bulb with many
    SandGrains that flow from the upper bulb to the lower one by gravity.

    This class also deals with the interaction with the user (tip over the
    clock, restart the clock, quit the simulation).
    """

    def __init__(self) -> None:
        """
        Initialize a SandClock instance.
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

        # Set up the pymunk space
        self.space = pymunk.Space()
        self.space.gravity = (0, self._config['gravity_y'])  # vertical gravity

        # Initialize the Sand Clock Structure
        self.sand_clock_structure = SandClockStructure(
            center=(
                self._config['screen_width'] // 2,
                self._config['screen_height'] // 2
            ),
            width=self._config['structure_width'],
            height=self._config['structure_height'],
            neck_width=self._config['neck_width'],
            line_width=self._config['line_width'],
            line_color=self._config['line_color']
        )
        # Add the Structure (its pymunk Segments) to the pymunk space
        for body, shape in zip(self.sand_clock_structure.body,
                               self.sand_clock_structure.shape):
            self.space.add(body, shape)

        # Initialize the SandGrains inside the upper bulb of the Sand Clock
        self.sand_grains_list = []
        for _ in range(self._config['n_sand_grains']):
            sand_grain = SandGrain(
                center=self.sand_clock_structure.init_grain_random_position(),
                radius=self._config['sand_grain_radius'],
                mass=self._config['sand_grain_mass'],
                color_type=self._config['sand_grain_color_type']
            )
            self.sand_grains_list.append(sand_grain)
        # Add all grains to the pymunk space, so they are affected by gravity
        for sand_grain_ in self.sand_grains_list:
            self.space.add(sand_grain_.body, sand_grain_.shape)

        self._tip_over = False  # whether to tip over the clock [Space Bar]
        self._reset = False  # whether to restart the clock ['R' keyboard]

    @staticmethod
    def _get_config() -> Dict[str, Any]:
        """
        Read the configuration file and return it as a python dictionary.
        The configuration file is called 'sand_clock/config.yml'

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
            - if the user wants to end the simulation: quit pygame
            - SPACE BAR: tip over the sand_clock
            - 'R': restart the sand_clock

        :return: whether the simulation is running
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._tip_over = True
                elif event.key == pygame.K_r:
                    self._reset = True
        return True

    def _flip_vertically(self) -> None:
        """
        Performs a vertical flip. The grains in the lower bulb are moved to the
        upper bulb and vice versa. When? When the user presses the space bar.

        :return: None
        """

        structure_center_y = self.sand_clock_structure.center[1]
        for sand_grain in self.sand_grains_list:
            x = sand_grain.body.position.x  # x coordinate remains untouched
            y = 2 * structure_center_y - sand_grain.body.position.y
            sand_grain.body.position = (x, y)

    def run_logic(self) -> None:
        """
        Run the logic of the simulation:
            - Update the positions all the SandGrain instances based on the
                gravity and their current position.
            - If the user has pressed the space bar, tip over the clock
            - If the user has pressed the 'R' key, restart the clock.

        :return: None
        """

        self.space.step(1/100)

        if self._tip_over:
            self._tip_over = False
            self._flip_vertically()

        if self._reset:
            self._reset = False
            self.__init__()

    def draw(self) -> None:
        """
        Display the elements of the simulation on the 'screen' attribute.

        :return: None
        """

        self._screen.fill(self._config['background_color'])
        self.sand_clock_structure.draw(screen=self._screen)
        for sand_grain in self.sand_grains_list:
            sand_grain.draw(screen=self._screen)
        pygame.display.update()

    def clock_tick(self) -> None:
        """
        Updates the pygame clock (attribute '_clock')

        :return: None
        """

        self._clock.tick(self._config['pygame_clock_tick'])


if __name__ == '__main__':
    sand_clock = SandClock()

    running = True
    while running:
        running = sand_clock.process_events()
        sand_clock.run_logic()
        sand_clock.draw()
        sand_clock.clock_tick()

    pygame.quit()
