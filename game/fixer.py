import os 
try:
    import sqlite3
except ImportError:
    os.system("pip install sqlite3")
    import sqlite3
try:
    import contextlib
    with contextlib.redirect_stdout(None):
        import pygame
except ImportError:
    os.system("pip install pygame")
    import contextlib
with contextlib.redirect_stdout(None):
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
import sys

for idx, arg in enumerate(sys.argv):
    if arg == "main":
        from main import main 
        while True:
            main()