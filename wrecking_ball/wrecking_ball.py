"""
This is a module that implements a funny simulation called 'Wrecking Ball'
using Python and the Pygame and Pymunk libraries. This is a zero-player
simulation in which there is a wrecking ball that moves across the screen and
collides with small balls (it actually runs over them )that fall from the top
of the screen.

The user is allowed to change the physics and features of the simulation.
More information can be found in 'wrecking_ball/config.yml'.

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
from typing import Tuple, Dict, Any

import yaml
import pygame
import pymunk


class SmallBall:
    """
    SmallBall class. Implements the functionalities of a SmallBall that falls
    from the top of the screen and collides with the WreckingBall (note that
    SmallBall is a dynamic body and WreckingBall is a kinematic body).
    Each SmallBall is represented as a pymunk circle, with the corresponding
    'body' and 'shape' attributes.

    When a SmallBall hits the bottom of the screen, that SmallBall is removed.
    """

    def __init__(
            self,
            center: Tuple[int, int],
            radius: int,
            mass: int,
            elasticity: float,
            friction: float,
            color: Tuple[int, int, int],
    ) -> None:
        """
        Initialize a SmallBall instance.

        :param center: (x,y) coordinates of the center
        :param radius: radius of the SmallBall (circle)
        :param mass: mass of the SmallBall
        :param elasticity: elasticity of the Pymunk shape
        :param friction: friction coefficient of the Pymunk shape
        :param color: color of the SmallBall in RGB format
        :return: None
        """

        self.color = color
        self.radius = radius

        # Create the Spark using the Pymunk library:
        # - body: represents the SmallBall in the physical world and has
        #       properties like mass, position, velocity, and rotation.
        # - shape: attached to a body and defines the geometry of the object.
        #       They are used for collision detection and response.
        self.body = pymunk.Body(mass=mass, moment=1)
        self.body.position = center
        self.shape = pymunk.Circle(self.body, self.radius)

        # Elasticity: A value of 0.0 gives no bounce,
        # while a value of 1.0 will give a ‘perfect’ bounce.
        self.shape.elasticity = elasticity  # float from between 0 and 1
        # Friction: Friction coefficient. A value of 0.0 is frictionless.
        self.shape.friction = friction  # float from between 0 and 1

    def is_out_of_screen(
            self,
            screen_width: int,
            screen_height: int
    ) -> bool:
        """
        Checks whether the SmallBall is out of the screen (visible or not).
        If it is out of the screen, we should remove it since it is no longer
        visible.

        :param screen_width: width of the screen to know the screen limits
        :param screen_height: height of the screen to know the screen limits
        return: whether the SmallBall is out of the screen
        """

        out_lower = self.body.position[1] - self.radius // 2 > screen_height
        out_left = self.body.position[0] + self.radius // 2 < 0
        out_right = self.body.position[0] - self.radius // 2 > screen_width
        return out_lower or out_left or out_right

    def draw(self, screen: pygame.surface) -> None:
        """
        Display the SmallBall on the given 'screen'.

        :param screen: pygame surface where the SmallBall is displayed
        :return: None
        """

        pygame.draw.circle(
            surface=screen,
            color=self.color,
            center=self.body.position,
            radius=self.radius
        )


class WreckingBall:
    """
    WreckingBall class. Implementation of the logic behind the simulation.
    There is a Pymunk Kinematic object called wrecking_ball which is not
    affected by the gravity and moves across the screen colliding with the
    SmallBall instances. When there is a collision, the wrecking_ball does not
    change its direction or velocity, but the SmallBall instances do that.
    """

    def __init__(self) -> None:
        """
        Initialize a WreckingBall instance.
        """

        # Read the config file
        self._config = self._get_config()

        # Initialize the Pygame elements
        pygame.init()
        self._screen = pygame.display.set_mode(
            (self._config['screen_width'], self._config['screen_height'])
        )
        pygame.display.set_caption(self._config['screen_caption'])
        self._clock = pygame.time.Clock()

        # set up the pymunk space
        self.space = pymunk.Space()
        self.space.gravity = (0, self._config['gravity_y'])  # vertical gravity

        # Create the wrecking ball (body and random initial velocity)
        self.wrecking_ball_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.wrecking_ball_body.position = (
            self._config['screen_width'] // 2,
            self._config['screen_height'] // 2
        )
        velocity_x = random.randrange(
            start=self._config['min_velocity_x'],
            stop=self._config['max_velocity_x']
        ) * random.choice((-1, 1))  # randomly select to move to left or right
        velocity_y = random.randrange(
            start=self._config['min_velocity_y'],
            stop=self._config['max_velocity_y']
        ) * random.choice((-1, 1))  # randomly select to move up or down
        self.wrecking_ball_body.velocity = (velocity_x, velocity_y)

        # Create the wrecking ball (shape: Circle)
        self.wrecking_ball_shape = pymunk.Circle(
            self.wrecking_ball_body, self._config['wrecking_ball_radius']
        )

        # Add the wrecking ball to the pymunk space
        self.space.add(self.wrecking_ball_body, self.wrecking_ball_shape)

        # Create list to store SmallBalls which will be added in the
        # 'run_logic' method (one new small ball every time step)
        self.small_balls_list = []

    @staticmethod
    def _get_config() -> Dict[str, Any]:
        """
        Read the configuration file and return it as a python dictionary.
        The configuration file is called 'wrecking_ball/config.yml'

        :return: configuration dictionary
        """

        this_file_path = os.path.abspath(__file__)
        this_project_dir_path = '/'.join(this_file_path.split('/')[:-1])
        config_path = this_project_dir_path + '/config.yml'

        with open(config_path, 'r') as yml_file:
            config = yaml.safe_load(yml_file)[0]['config']
        return config

    @staticmethod
    def process_events() -> bool:
        """
        Process the actions of the user (if the user wants to quit the
        simulation)

        :return: whether the simulation is running
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def run_logic(self) -> None:
        """
        Run the logic of the simulation:
            - Move forward in time the simulation physics (space.step call)
            - Make sure that the wrecking ball do not leave the screen
            - Create a new random SmallBall
            - Kill all the SmallBalls that are no longer visible

        :return: None
        """

        self.space.step(1/60)

        # Prevent the wrecking ball from leaving the screen (update velocity)
        vel_x, vel_y = self.wrecking_ball_body.velocity
        x, y = self.wrecking_ball_body.position
        if (x + self.wrecking_ball_shape.radius > self._config['screen_width']
                or x - self.wrecking_ball_shape.radius < 0):
            self.wrecking_ball_body.velocity = (- vel_x, vel_y)
        if (y + self.wrecking_ball_shape.radius > self._config['screen_height']
                or y - self.wrecking_ball_shape.radius < 0):
            self.wrecking_ball_body.velocity = (vel_x, - vel_y)

        # Create a new random SmallBall above the top of the screen (will fall
        # due to the gravity)
        new_random_center = (
            random.randrange(start=0, stop=self._config['screen_width']),
            - self._config['screen_height'] // 4  # above the top of the screen
        )
        new_small_ball = SmallBall(
            center=new_random_center,
            radius=self._config['small_ball_radius'],
            mass=self._config['small_ball_mass'],
            elasticity=self._config['elasticity'],
            friction=self._config['friction'],
            color=random.choices(population=range(255), k=3)
        )
        self.small_balls_list.append(new_small_ball)
        self.space.add(new_small_ball.body, new_small_ball.shape)

        # Kill all those SmallBalls which leave the screen
        for small_ball in self.small_balls_list:
            if small_ball.is_out_of_screen(
                    screen_width=self._config['screen_width'],
                    screen_height=self._config['screen_height']
            ):
                self.small_balls_list.remove(small_ball)
                self.space.remove(small_ball.body, small_ball.shape)

    def draw(self) -> None:
        """
        Display the elements of the simulation on the 'screen' attribute.

        :return: None
        """

        self._screen.fill(self._config['background_color'])  # fill background
        # Display the wrecking ball
        pygame.draw.circle(
            surface=self._screen,
            color=self._config['wrecking_ball_color'],
            center=self.wrecking_ball_body.position,
            radius=self.wrecking_ball_shape.radius
        )
        # Display the small balls
        for small_ball in self.small_balls_list:
            small_ball.draw(screen=self._screen)
        pygame.display.update()  # update the screen content

    def clock_tick(self) -> None:
        """
        Updates the pygame clock (attribute '_clock')

        :return: None
        """

        self._clock.tick(self._config['pygame_clock_tick'])


if __name__ == '__main__':
    wrecking_ball = WreckingBall()

    running = True
    while running:
        running = wrecking_ball.process_events()
        wrecking_ball.run_logic()
        wrecking_ball.draw()
        wrecking_ball.clock_tick()

    pygame.quit()
