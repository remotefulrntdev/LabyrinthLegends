import pygame
import random
from difflib import SequenceMatcher
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
import threading, asyncio

# Load environment variables from .env file
load_dotenv()

# Retrieve the API token from the environment variable
API_TOKEN = os.getenv('KEY')
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
# Pygame initialization
WIDTH = 800
HEIGHT = 650
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

    def update(self):
        if self.rect.left > WIDTH:
            self.rect.right = 0

# Initialize the bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Define the command handler
@dp.message_handler(commands=['up'])
async def handle_up_command(message: types.Message):
    print("Received /up command")
    player.rect.y -= 10

# Start the bot
def start_bot():
    print("Bot started")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(dp.start_polling())

# Pygame initialization
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Subscriber, game By RemoteAccess01 <3")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# Start the bot in a separate thread
bot_thread = threading.Thread(target=start_bot, daemon=True)
bot_thread.start()

running = True
while running:
    clock.tick(FPS)

    # Process Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update game objects
    all_sprites.update()

    # Rendering
    screen.fill(BLACK)
    all_sprites.draw(screen)
    pygame.display.flip()

# Wait for the bot thread to finish before exiting
bot_thread.join()

pygame.quit()
