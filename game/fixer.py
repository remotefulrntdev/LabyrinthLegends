import argparse,os 
try:
    import sqlite3
except ImportError:
    os.system("pip install sqlite3")
    import sqlite3
try:
    import pygame
except ImportError:
    os.system("pip install pygame")
    import pygame
try:
    import dotenv
except ImportError:
    os.system("pip install dotenv")
    import dotenv
try: 
    import telebot 
except ImportError:
    os.system("pip install telebot")
    import telebot
from main import main 
while True:
    main()