"""
This is a module that implements a funny simulation called 'Pizza Rain' using
Python and the Pygame library. In this simulation, there are a lot of pizzas
falling down the screen while they rotate. The user is allowed to change the
fall speed and the rotation speed as well.

KEYWORDS: Sprites, Sprite Groups, YAML configuration files, Pygame, Simulations
"""

import os
import random
from typing import Dict, Any, Optional

import yaml
import pygame


class Pizza(pygame.sprite.Sprite):
    """
    Pizza class. A Pizza inherits the properties of the Pygame Sprite class.
    Pizzas fall down the screen while they rotate. When they reach the bottom,
    they appear at the top of the screen again.

    A Pygame Sprite is typically a 2D graphical object or image that can be
    used in game development to represent characters, objects, or other visual
    elements within a graphical environment. The Sprite class includes
    functionalities for things like movement, collision detection, animation,
     and rendering.
    """

    def __init__(
            self,
            pizza_img_path: str,
            vertical_speed: int,
            rotation_every: int,
            diameter: int,
            screen_height: int
    ) -> None:
        """
        Initialize a Pizza instance.

        :param pizza_img_path: path of the image representing the Pizza
        :param vertical_speed: number of pixels to move down at each step
        :param rotation_every: frequency of 90º counterclockwise rotations
        :param diameter: diameter of the Pizza (in pixels)
        :param screen_height: height of the Pygame screen (surface)
        :return: None
        """

        super().__init__()  # Initialize parent class pygame.sprite.Sprite

        # Sanity Check: check that the given 'pizza_img_path' exists
        if not os.path.exists(pizza_img_path):
            raise ValueError('The given pizza_img_path does not exists')

        # Define the image (pygaem surface) and scale it to the given diameter.
        self.image = pygame.image.load(pizza_img_path).convert()  # surface
        self.image = pygame.transform.scale(
            surface=self.image, size=(diameter, diameter)
        )

        # Get the rectangle of the surface with the top-left corner at
        # coordinates (0,0). They can be changed using the 'set_center' method.
        self.rect = self.image.get_rect()  # Sprite attribute
        self.vertical_speed = vertical_speed  # fall speed in pixels
        self.rotation_every = rotation_every  # frequency of 90º rotations
        self.diameter = diameter  # in pixels
        self.screen_height = screen_height  # in pixels

        # Track the number of updates to know when to perform a rotation
        self.n_updates = 0

    def set_center(self, x: int, y: int) -> None:
        """
        Updates the center of the Pizza to the given (x,y) coordinates

        :param x: horizontal coordinate X
        :param y: vertical coordinate Y
        :return: None
        """

        self.rect.center = (x, y)

    def update(
            self,
            vertical_speed_incr: Optional[int] = None,
            rotation_every_incr: Optional[int] = None
    ) -> None:
        """
        [overwrite the 'update' method from the parent class Sprite]
        If 'vertical_speed_incr' is given, just increment the attribute
        'vertical_speed' with the given value. (only values greater than one).
        If 'rotation_every_incr' is given, just increment the attribute
        'rotation_every' with the given value. (only values greater than one).

        Else (if none of these two arguments are provided), update the vertical
        position of the Pizza and perform rotations (if any).

        :param vertical_speed_incr: increment in 'vertical_speed' [Optional]
        :param rotation_every_incr: increment in 'rotation_every' [Optional]
        :return: None
        """

        if vertical_speed_incr is not None:
            self.vertical_speed = max(
                1, self.vertical_speed + vertical_speed_incr
            )
        elif rotation_every_incr is not None:
            self.rotation_every = max(
                1, self.rotation_every + rotation_every_incr
            )
            self.n_updates = self.rotation_every - 1
        else:
            self.rect.y += self.vertical_speed
            if self.rect.top > self.screen_height:
                # if the pizza gets out of the screen (at the bottom),
                # it appears at the top
                self.rect.bottom = 0

            self.n_updates += 1
            if self.n_updates == self.rotation_every:
                # Rotate the pizza
                self.n_updates = 0
                self.image = pygame.transform.rotate(self.image, angle=90)


class PizzaRain:
    """
    PizzaRain class. Creates a Group of Pizza instances. The idea is to
    simulate a pizza rain. The user is allowed to use the keyboard arrows to
    speed up or slow down the simulation and the rotation speed of the pizzas.

    In Pygame, a Sprite Group is a fundamental concept that simplifies the
    management and rendering of multiple sprites (Pizza instances in our case).
    It is a container for holding and organizing sprite objects. Sprite groups
    provide a convenient way to perform common operations on multiple sprites
    simultaneously, such as updating ('update' method) and drawing them on the
    screen ('update' method). Sprite groups also provide methods for handling
    collision detection between sprites ('spritecollide' is used here).
    """

    _white_color = (255, 255, 255)  # background color

    def __init__(self) -> None:
        """
        Initialize a PizzaRain instance
        """

        # Read the configuration file
        self._dir_path = ''  # updated in '_get_config' method
        self._config = self._get_config()

        self._is_running = True  # If False, the simulation is paused

        # Initialize the Pygame elements
        pygame.init()
        self._screen = pygame.display.set_mode(
            (self._config['screen_width'], self._config['screen_height'])
        )
        pygame.display.set_caption(
            self._config['screen_caption'].format(is_running='running')
        )
        self._clock = pygame.time.Clock()

        # Create the list of Pizza instances
        self._pizza_list = pygame.sprite.Group()
        for _ in range(self._config['number_of_pizzas']):
            pizza_img = random.choice(self._config['pizza_images_files'])
            pizza = Pizza(
                pizza_img_path=self._dir_path + '/images/' + pizza_img,
                vertical_speed=self._config['vertical_speed'],
                rotation_every=self._config['rotation_every'],
                diameter=self._config['diameter'],
                screen_height=self._config['screen_height']
            )
            # Make sure that there are no pizzas that overlap
            while pygame.sprite.spritecollide(
                    pizza, self._pizza_list, dokill=0
            ):
                pizza.set_center(
                    x=random.randrange(self._config['screen_width']),
                    y=random.randrange(self._config['screen_height'])
                )
            self._pizza_list.add(pizza)

    def _get_config(self) -> Dict[str, Any]:
        """
        Read the configuration file and return it as a python dictionary.
        The configuration file is called 'pizza_rain/config.yml'

        :return: configuration dictionary
        """

        this_file_path = os.path.abspath(__file__)
        pizza_rain_dir_path = '/'.join(this_file_path.split('/')[:-1])
        self._dir_path = pizza_rain_dir_path
        config_path = pizza_rain_dir_path + '/config.yml'

        with open(config_path, 'r') as yml_file:
            config = yaml.safe_load(yml_file)[0]['config']
        return config

    def process_events(self) -> bool:
        """
        Process the actions carried out by the user:
            - SPACE BAR: pause/resume the simulation
            - RIGHT ARROW: increase the frequency of rotations (rotation_every)
            - LEFT ARROW: decrease the frequency of rotations (rotation_every)
            - DOWN ARROW: increase the fall speed (vertical_speed)
            - UP ARROW: decrease the fall speed (vertical_speed)

        :return: whether to go on with the simulation
        """

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # pause/resume
                    self._is_running = not self._is_running
                if event.key == pygame.K_UP:  # decrease fall speed
                    self._pizza_list.update(
                        vertical_speed_incr=-self._config['vertical_speed_incr']
                    )
                elif event.key == pygame.K_DOWN:  # increase fall speed
                    self._pizza_list.update(
                        vertical_speed_incr=self._config['vertical_speed_incr']
                    )
                elif event.key == pygame.K_RIGHT:  # increase rotation freq
                    self._pizza_list.update(
                        rotation_every_incr=-self._config['rotation_every_incr']
                    )
                elif event.key == pygame.K_LEFT:  # decrease rotation freq
                    self._pizza_list.update(
                        rotation_every_incr=self._config['rotation_every_incr']
                    )
        return True

    def run_logic(self) -> None:
        """
        Update every Pizza instance:
            - move down every pizza (vertical_speed)
            - may rotate every pizza (rotation_every)

        :return: None
        """

        if self._is_running:
            self._pizza_list.update()
        # Update the screen caption to inform about state 'running' or 'paused'
        pygame.display.set_caption(
            self._config['screen_caption'].format(
                is_running='running' if self._is_running else 'paused'
            )
        )

    def draw(self) -> None:
        """
        Display the elements of the simulation on the '_screen' attribute

        :return: None
        """

        self._screen.fill(self._white_color)  # background color
        self._pizza_list.draw(self._screen)  # display all the pizzas
        pygame.display.update()  # update the screen's content

    def clock_tick(self) -> None:
        """
        Updates the pygame clock (attribute '_clock')

        :return: None
        """

        self._clock.tick(self._config['pygame_clock_tick'])


if __name__ == '__main__':
    pizza_rain = PizzaRain()

    running = True
    while running:
        running = pizza_rain.process_events()
        pizza_rain.run_logic()
        pizza_rain.draw()
        pizza_rain.clock_tick()

    pygame.quit()
