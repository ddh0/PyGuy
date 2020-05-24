# Python 3.8.2
# PyGuy - A boundary-breaking PC platformer
# By Dylan Halladay - v0.1

import pygame
from pygame.locals import *

# Print start message to the screen. Likely won't be seen in time without a delay
print("Starting...\nTo exit the game, press ESCAPE.")

# Color constants
COLORKEY = (int(128), int(128), int(128))
BACKGROUND_COLOR = (int(255), int(255), int(255))

# Player constants
PLAYER_WIDTH = 45
PLAYER_HEIGHT = 120
PLAYER_SPEED = 2
JUMP_POWER = 2

# Game loop variable
keep_running = True

# 'pygame.time.Clock.tick()' isn't how you do it. Do this instead, then use clock.tick()
clock = pygame.time.Clock()

pygame.display.init()
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2)  # Reduces sound latency
pygame.mixer.init()

# Create fullscreen display, fill with color, and set window title text
ScreenSurface = pygame.display.set_mode((0, 0), flags=pygame.FULLSCREEN)
ScreenSurface.fill(BACKGROUND_COLOR)
pygame.display.set_caption('PyGuy v0.1')

# Create screen size variables, full size and half size
SW, SH = pygame.display.get_surface().get_size()
HW = int(SW / 2)
HH = int(SH / 2)

# Load images
PyGuySurface = pygame.image.load('resources/PyGuy.gif').convert()
PyGuyJumpSurface = pygame.image.load('resources/PyGuy_jump.gif').convert()

PyGuySurface.set_colorkey(COLORKEY)
PyGuyJumpSurface.set_colorkey(COLORKEY)

# Load sounds
StartSoundObj = pygame.mixer.Sound('resources/start.wav')

# Sprite groups
AllSpritesGroup = pygame.sprite.Group()    # Contains all sprites
BlockSpritesGroup = pygame.sprite.Group()  # Contains all blocks
EnemySpritesGroup = pygame.sprite.Group()  # Contains all enemies


class Player(pygame.sprite.Sprite):
    """ Tip - call keypress methods, then call move() """

    def __init__(self):
        super(Player, self).__init__()

        # Scale image, create rect, set starting position, and create mask
        self.image = pygame.transform.scale(PyGuySurface, (PLAYER_WIDTH, PLAYER_HEIGHT))  # image is a surface
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.health = 100

        # Velocity
        self.vx = 0
        self.vy = 0

        # Groups
        AllSpritesGroup.add(self)

    def up_key(self):
        self.vy = JUMP_POWER

    def down_key(self):
        self.vy = -JUMP_POWER

    def left_key(self):
        self.vx = -PLAYER_SPEED

    def right_key(self):
        self.vx = PLAYER_SPEED

    def no_keys(self):
        self.vx = 0
        self.vy = 0

    def move(self):
        """ Move player according to velocity over x axis, then over y axis.
            If a collision occurs, backtrack until resolved """
        self.rect.move_ip(self.vx, 0)                                                               # X-collisions
        while pygame.sprite.spritecollideany(self, BlockSpritesGroup, collided=None) is not None:   # with
            if self.vx < 0:                                                                         # blocks
                self.rect.move_ip(1, 0)
                self.vx -= 1                # Undo last px of movement
            else:                           # Reduce velocity by 1
                self.rect.move_ip(-1, 0)
                self.vx += 1

        self.rect.move_ip(0, -self.vy)                                                              # Y-collisions
        while pygame.sprite.spritecollideany(self, BlockSpritesGroup, collided=None) is not None:   # with
            if self.vy < 0:                                                                         # blocks
                self.rect.move_ip(0, 1)
                self.vy -= 1                # Undo last px of movement
            else:                           # Reduce velocity by 1
                self.rect.move_ip(0, -1)
                self.vy += 1


# Init player
PyGuy = Player()

# Game loop
while keep_running:
    # Get which keys are currently pressed
    KeyState = pygame.key.get_pressed()

    # Keys that control PyGuy
    if KeyState[K_UP] or KeyState[K_SPACE] or KeyState[K_w]:
        PyGuy.up_key()
    if KeyState[K_DOWN] or KeyState[K_s]:
        PyGuy.down_key()
    if KeyState[K_LEFT] or KeyState[K_a]:
        PyGuy.left_key()
    if KeyState[K_RIGHT] or KeyState[K_d]:
        PyGuy.right_key()
    if (not KeyState[K_UP] and
            not KeyState[K_SPACE] and
            not KeyState[K_w] and
            not KeyState[K_DOWN] and
            not KeyState[K_s] and
            not KeyState[K_LEFT] and
            not KeyState[K_a] and
            not KeyState[K_RIGHT] and
            not KeyState[K_d]):
        # If no keys are pressed
        PyGuy.no_keys()

    # ESCAPE key stops the game loop
    if KeyState[K_ESCAPE]:
        keep_running = False

    # Update PyGuy
    PyGuy.move()

    # Clear the screen
    ScreenSurface.fill(BACKGROUND_COLOR)

    # Draw sprites onto the screen
    AllSpritesGroup.draw(ScreenSurface)

    # Update screen
    pygame.display.flip()

    # Pump event queue (must be done once per loop, or no events will be handled)
    pygame.event.pump()

    # Tick the clock (if no args passed, framerate is unlimited, but so is CPU usage)
    clock.tick()
