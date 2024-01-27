import pygame
from pygame.locals import *
import telebot
# impott SequenceMatcher
from difflib import SequenceMatcher
from dotenv import load_dotenv
import os
import threading

load_dotenv()

API_TOKEN = os.getenv('KEY')

# Step 1: Set up the Pygame environment
pygame.init()
screen = pygame.display.set_mode((800, 600))

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
# Step 2: Create the Player sprite class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))  # Replace with your actual player image
        self.rect = self.image.get_rect()
        self.rect.x = 375  # Initial x-position of the player
        self.rect.y = 275  # Initial y-position of the player

    def update(self, keys):
        if keys[K_LEFT]:
            self.rect.x -= 5  # Adjust the movement speed as needed

# Step 3: Integrate with telebot
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['left'])
def move_left(message):
    player.update({K_LEFT: True})  # Update the player's movement state
    print("Received /left command")
# Create the player sprite
player = Player()

# Start the telebot
def start_bot():
    bot.polling()

bot_thread = threading.Thread(target=start_bot)
bot_thread.start()

# Game loop
while True:
    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    # Update player position
    player.update(pygame.key.get_pressed())

    # Redraw the screen
    screen.fill((255, 255, 255))  # Clear the screen
    screen.blit(player.image, player.rect)  # Draw the player sprite
    pygame.display.flip()  # Update the display
