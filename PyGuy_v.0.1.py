# Python 3.8.2
# PyGuy - A boundary-breaking PC platformer
# By Dylan Halladay - v0.1

import pygame
from pygame.locals import *

# Print start message to the screen. Likely won't be seen in time without a delay
print("Starting...\nTo exit the game, press ESCAPE.")

# Screen size constants
screen_width = 256
screen_height = 224

# Color constants
COLORKEY = (128, 128, 128)
BACKGROUND_COLOR = (255, 255, 255)
BLOCK_COLOR = (0, 0, 0)

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

# Get physical monitor display size, scale screen to fill, set window title text
hw_display = pygame.display.Info()
hw_display_size = (hw_display.current_w, hw_display.current_h)
screen_surface = pygame.display.set_mode((screen_width, screen_height), flags=pygame.FULLSCREEN)
screen_surface = pygame.transform.scale(screen_surface, hw_display_size)
pygame.display.set_caption('PyGuy v0.1')

screen_surface.fill(BACKGROUND_COLOR)
half_width = int(screen_width / 2)
half_height = int(screen_height / 2)

pygame.mouse.set_visible(False)

# Load images
pyguy_surface = pygame.image.load('resources/PyGuy.gif').convert()
pyguy_jump_surface = pygame.image.load('resources/PyGuy_jump.gif').convert()

pyguy_surface.set_colorkey(COLORKEY)
pyguy_jump_surface.set_colorkey(COLORKEY)

# Load sounds
start_sound_obj = pygame.mixer.Sound('resources/start.wav')

# Sprite lists (easier to iterate over than groups)
all_sprites_list = []
block_sprites_list = []


class Player(pygame.sprite.Sprite):
    """ Tip - call keypress methods, then call move() """

    def __init__(self, x_center, y_center):
        super().__init__()

        # Scale image, create rect, set starting position, and create mask
        self.image = pygame.transform.scale(pyguy_surface, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.rect = self.image.get_rect(center=(x_center, y_center))
        self.mask = pygame.mask.from_surface(self.image)

        self.health = 100

        # Velocity
        self.vx = 0
        self.vy = 0

        all_sprites_list.append(self)

    def up_key(self):
        self.vy = JUMP_POWER

    def down_key(self):
        self.vy = -JUMP_POWER

    def left_key(self):
        self.vx = -PLAYER_SPEED

    def right_key(self):
        self.vx = PLAYER_SPEED

    def action_key(self):
        pass

    def no_keys(self):
        self.vx = 0
        self.vy = 0

    def update(self):
        """ Move player according to velocity over x axis, then over y axis.
            If a collision occurs, backtrack until resolved """
        self.rect.move_ip(self.vx, 0)
        for block in block_sprites_list:
            if pygame.sprite.collide_mask(self, block) is not None:
                if self.vx < 0:
                    self.rect.move_ip(1, 0)
                    self.vx -= 1                # Undo last px of movement
                else:                           # Reduce velocity by 1
                    self.rect.move_ip(-1, 0)
                    self.vx += 1

        self.rect.move_ip(0, -self.vy)
        for block in all_sprites_list:
            if pygame.sprite.collide_mask(self, block) is not None:
                if self.vy < 0:
                    self.rect.move_ip(0, 1)
                    self.vy -= 1                # Undo last px of movement
                else:                           # Reduce velocity by 1
                    self.rect.move_ip(0, -1)
                    self.vy += 1


class Block(pygame.sprite.Sprite):

    def __init__(self, x_center, y_center, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLOCK_COLOR)
        self.image.convert_alpha(self.image)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x_center, y_center)

        all_sprites_list.append(self)
        block_sprites_list.append(self)


# Create player
pyguy = Player(half_width, half_height)

# Create testing block
testing_block = Block(half_width+100, half_height+100, 20, 20)

# Game loop
while keep_running:
    # Get which keys are currently pressed
    key_state = pygame.key.get_pressed()

    # Keys that control PyGuy
    if key_state[K_UP] or key_state[K_w]:
        pyguy.up_key()
    if key_state[K_DOWN] or key_state[K_s]:
        pyguy.down_key()
    if key_state[K_LEFT] or key_state[K_a]:
        pyguy.left_key()
    if key_state[K_RIGHT] or key_state[K_d]:
        pyguy.right_key()
    if key_state[K_SPACE] or key_state[K_f]:
        pyguy.action_key()
    if (not key_state[K_UP] and
            not key_state[K_w] and
            not key_state[K_DOWN] and
            not key_state[K_s] and
            not key_state[K_LEFT] and
            not key_state[K_a] and
            not key_state[K_RIGHT] and
            not key_state[K_d] and
            not key_state[K_SPACE] and
            not key_state[K_f]):
        # If no keys are pressed
        pyguy.no_keys()

    # ESCAPE key stops the game loop
    if key_state[K_ESCAPE]:
        keep_running = False

    # Update PyGuy
    pyguy.update()

    # Clear the screen
    screen_surface.fill(BACKGROUND_COLOR)

    # Draw sprites onto the screen
    for sprite in all_sprites_list:
        screen_surface.blit(sprite.image, sprite.rect)

    # Update screen
    pygame.display.flip()

    # Pump event queue (must be done once per loop, or no events will be handled)
    pygame.event.pump()

    # Tick the clock (if no args passed, framerate is unlimited, but so is CPU usage)
    clock.tick()
