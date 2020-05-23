import pygame

# Init sound mixer and play start sound while game loads
pygame.mixer.pre_init(frequency=16000, size=8, channels=1, buffer=512)
pygame.mixer.init()
pygame.mixer.Sound('resources/start.wav').play()

from pygame.locals import ( # Keyboard keys
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT, # Window close button
)

import secrets
import datetime
import time

pygame.init()

def playsound(sound_obj, pause_length):
    sound_obj.play()
    if pause_length != 0:
        time.sleep(pause_length)

# Constants for color
# PLAYER_COLOR = (int(0), int(0), int(0))
# ENEMY_COLOR = (int(194), int(0), int(0))
# BLOCK_COLOR = (int(153), int(75), int(2))
BACKGROUND_COLOR = (int(97), int(158), int(255))

grey = (int(128), int(128), int(128))

# Create the screen
screen = pygame.display.set_mode((0, 0), flags=pygame.FULLSCREEN)
pygame.display.set_caption('PyGuy')

screen_rect = screen.get_rect()

# Get device's screen size and set variables
SW, SH = pygame.display.get_surface().get_size()

HW = SW/2
HH = SH/2

# Pre-load images into RAM
player_img = pygame.image.load('resources/PyGuy.gif').convert()
player_jump_img = pygame.image.load('resources/PyGuy_jump.gif').convert()

crawler_img = pygame.image.load('resources/Crawler.gif').convert()
crawler_1_img = pygame.image.load('resources/Crawler_1.gif').convert()
crawler_2_img = pygame.image.load('resources/Crawler_2.gif').convert()

block_img = pygame.image.load('resources/Block.gif').convert()

coin_img = pygame.image.load('resources/Coin_purple.gif').convert()

# Set color keys on images (what color of the original image will be transparent?)
player_img.set_colorkey(grey)
player_jump_img.set_colorkey(grey)

crawler_img.set_colorkey(grey)
crawler_1_img.set_colorkey(grey)
crawler_2_img.set_colorkey(grey)

coin_img.set_colorkey(grey)

# Pre-load sounds into RAM
jumpSoundObj = pygame.mixer.Sound('resources/jump.wav')
deathSoundObj = pygame.mixer.Sound('resources/death.wav')
coinSoundObj = pygame.mixer.Sound('resources/coin.wav')

# Other game constants
GRAVITY_FACTOR = .8
JUMP_FACTOR = 19

# Sprite constants
PLAYER_WIDTH = 25
PLAYER_HEIGHT = 50

CRAWLER_WIDTH = 55
CRAWLER_HEIGHT = 20

BLOCK_WIDTH = 100
BLOCK_HEIGHT = 15

COIN_SIZE = 16

PLAYER_SPEED = 3
CRAWLER_SPEED = 12
BLOCK_SPEED = 1

# Setting for whether mouse is visible in game window
pygame.mouse.set_visible(False)

# Sprite groups, useful for collision detection and updating lots of things at once
sprites = pygame.sprite.Group()
blocks = pygame.sprite.Group()
enemies = pygame.sprite.Group()
crawlers = pygame.sprite.Group()

# How many loops have been completed? (Starts on 1)
frame_count = 0

# Define the player
class Player(pygame.sprite.Sprite):

    def __init__(self, pos):
        super(Player, self).__init__()
        
        self.image = pygame.transform.scale(player_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
        
        self.rect = self.image.get_rect(center=pos)
        
        # Velocity attributes
        
        self.vx = 0
        self.vy = 0
        
        # Misc attributes
        
        self.alive = True
        self.in_air = False
        
        # Sprite groups
        
        sprites.add(self)
    
    def update(self):
        
        # 
        # Find out if player is on a block, store bool in self.in_air
        # 
        # Change animation based on self.on_block
        # 
        # Apply gravity if in_air
        # 
        # Change veloicty based on keypresses
        # 
        # Move along x axis, handle collisions by moving -.vx
        # 
        # Move along y axis:
        #
        #   If going collide with block and vy < 0, self.in_air = 0
        
        if self.rect.bottom == SH or self.vy == 0: # If on ground or block

            self.vy = 0
            
            if self.was_in_air: # If player was in the air last frame, reset image to normal
                
                self.image = pygame.transform.scale(player_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
                self.was_in_air = False

        else: # If not on ground

            self.vy -= GRAVITY_FACTOR
            
            if not self.was_in_air: # If player was in the air last frame, set image to jump
            
                self.image = pygame.transform.scale(player_jump_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
                self.was_in_air = True
        
        pressed_keys = pygame.key.get_pressed()
        
        if pressed_keys[K_UP]:
            
            if frame_count >= (self.last_jump_frame + 60):
            
                if self.vy == 0: # If on ground or block
                    
                    playsound(jumpSoundObj, 0)
                    self.vy += JUMP_FACTOR
                    self.last_jump_frame = frame_count

        if pressed_keys[K_DOWN] and self.rect.bottom < SH: self.vy -= JUMP_FACTOR/2

        if pressed_keys[K_LEFT]:
        
            self.vx = -PLAYER_SPEED

        elif pressed_keys[K_RIGHT]:
            
            self.vx = PLAYER_SPEED
        
        else:
            
            self.vx = 0
        
        self.rect.move_ip(self.vx, 0) # Move in x direction
        
        collided = None
        
        collided = pygame.sprite.spritecollideany(self, blocks, collided = None)

        if collided is not None: # If collided with block
            self.rect.move_ip(-self.vx, 0) # Undo last frame's movement to prevent overlap
            
            if self.vx > 0: # Moving right
            
                self.vx = 0 # Stop moving
                self.rect.right = collided.rect.left # Set right side of self to left side of collided
            
            if self.vx < 0: # Moving left
            
                self.vx = 0 # Stop moving
                self.rect.left = collided.rect.right # Set left side of self to right side of collided
            
        if pygame.sprite.spritecollideany(self, enemies, collided = None) is not None: # If collided with enemy
            self.rect.move_ip(-self.vx, 0) # Undo last frame's movement to prevent overlap
            self.vx = 0 # Lose all velocity
            self.alive = False
            self.kill()
        
        self.rect.move_ip(0, -self.vy) # Move in y direction
        
        collided = None
        
        collided = pygame.sprite.spritecollideany(self, blocks, collided = None)
        
        if collided is not None: # If collided with block
            
            if self.vy > 0: # Moving up
            
                self.rect.move_ip(0, self.vy) # Undo last frame's movement to prevent overlap
                self.vy = 0 # Stop moving
                self.rect.top = collided.rect.bottom # Set top side of self to bottom side of collided
            
            if self.vy < 0: # Moving down
            
                self.rect.move_ip(0, self.vy) # Stop moving
                self.rect.bottom = collided.rect.top # Set bottom side of self to top side of collided
                self.last_block_frame = frame_count
            
        if pygame.sprite.spritecollideany(self, enemies, collided = None) is not None: # If collided with enemy
            self.alive = False
            self.kill()
        
        self.rect.clamp_ip(screen_rect)
        
        if self.alive == False: playsound(deathSoundObj, 1.5)

# Define crawlers
class Crawler(pygame.sprite.Sprite):

    def __init__(self):
        super(Crawler, self).__init__()
        
        self.image = pygame.transform.scale(crawler_img, (CRAWLER_WIDTH, CRAWLER_HEIGHT))
        
        self.rect = self.image.get_rect(left=SW+5000, bottom=SH) # Spawn to the right of the screen
        
        # Sprite groups
        
        sprites.add(self)
        enemies.add(self)
        crawlers.add(self)

    def update(self):
        
        # Animate legs based on frame number
        
        last_digit = int(str(frame_count)[-1:]) # Get last digit of frame number as an int

        if last_digit <= 3:
        
            self.image = pygame.transform.scale(crawler_img, (CRAWLER_WIDTH, CRAWLER_HEIGHT)) # Change to default image
        
        if last_digit > 3 and last_digit < 7:
            
            self.image = pygame.transform.scale(crawler_1_img, (CRAWLER_WIDTH, CRAWLER_HEIGHT)) # Change to image 1
        
        if last_digit >= 7:

            self.image = pygame.transform.scale(crawler_2_img, (CRAWLER_WIDTH, CRAWLER_HEIGHT)) # Change to image 2
        
        if self.rect.left > PyGuy.rect.right - 1: # If facing PyGuy

            self.rect.move_ip(-CRAWLER_SPEED, 0) # Keep going, but at half speed
        
        else:
            
            self.rect.move_ip(-CRAWLER_SPEED/2, 0) # Keep going, but at half speed

        crawlers.remove(self)                                                         # Upon collision with another Crawler,
        crawler_hit = pygame.sprite.spritecollideany(self, crawlers, collided = None) # kill the rightmost Crawler
        crawlers.add(self)                                                            # 

        if crawler_hit is not None: # If there was a collision
        
            if crawler_hit.rect.left > self.rect.left: # If self is further left
                crawler_hit.kill()
            
            else: # If self is further right
                self.kill()
        
        if self.rect.right < 0: # If offscreen to the left, remove
            self.kill()

# Define blocks
class Block(pygame.sprite.Sprite):
    
    def __init__(self, ypos):
        super(Block, self).__init__()
        
        self.image = pygame.transform.scale(block_img, (BLOCK_WIDTH, BLOCK_HEIGHT)) # Static image, no animations for blocks
        
        self.rect = self.image.get_rect(left=SW+BLOCK_WIDTH, top=ypos) # Just offscreen, with top of block at given y-position
        
        if pygame.sprite.spritecollideany(self, blocks, collided=None) is not None:
            self.kill() # If collision with already-exisiting block, kill self
        else:
            blocks.add(self)
        
        # Sprite groups
        
        sprites.add(self)
        blocks.add(self)
    
    def update(self):
        
        if secrets.randbelow(4800) == 1: # Sometimes, blocks randomly dissappear!
            blocks.remove(self)
            self.kill()
        
        if self.rect.right < 0: # Remove when offscreen
            blocks.remove(self)
            self.kill()
        
        self.rect.move_ip(-BLOCK_SPEED, 0) # Move blocks left across the screen

class Coin(pygame.sprite.Sprite):

    def __init__(self, pos):
        super(Coin, self).__init__()
        
        self.image = pygame.transform.scale(coin_img, (COIN_SIZE, COIN_SIZE))

        self.rect = self.image.get_rect(center=pos)
        
        

# Create coins


# Init PyGuy
PyGuy = Player((HW, HH))

running = True
clock = pygame.time.Clock()

block_ypos_list = []

for i in range(1, SH): # Get list of valid heights for blocks, so blocks don't look so random
    if i % ((PLAYER_HEIGHT*1.2)+BLOCK_HEIGHT) == 0:
        block_ypos_list.append(int(i))
    
# Game loop
while running:

    clock.tick(120)
    frame_count += 1

    # Check for escape key or close button

    for event in pygame.event.get():
    # Any events?
 
        if event.type == KEYDOWN:
        # Keypress events

            if event.key == K_ESCAPE:
            # Escape key pressed
                running = False

        elif event.type == QUIT:
            # Close window button pressed
            running = False

    # 1 in x chance of spawning a new crawler every frame
    if secrets.randbelow(180) == 1: new_crawler = Crawler()
    
    if secrets.randbelow(12) == 1: # 1 in x chance of spawning a new block
        new_block = Block(secrets.choice(block_ypos_list))

    # Update sprites in order
    PyGuy.update()
    enemies.update()
    blocks.update()
    
    # Clear screen
    screen.fill(BACKGROUND_COLOR)
    
    # Draw all sprites onto screen
    sprites.draw(screen)

    # Display new screen
    pygame.display.flip()
    
    # Stop if PyGuy is dead
    if not PyGuy.alive: running = False

pygame.quit()