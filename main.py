import math
import pygame
from other.cons import * 
intro = pygame.transform.scale(pygame.image.load("res/intro.png"), (WIDTH,HEIGHT))
pygame.init()
pygame.mixer_music.load("res/music/1/music.mp3")
pygame.mixer_music.play(-1)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Labyrinth Legends - RNT DEVELOPMENT")
clock = pygame.time.Clock()
screen.blit(intro, pygame.Rect((0,0), (WIDTH,HEIGHT)))
pygame.display.flip()

import os
from dotenv import load_dotenv

import random
import sys
import threading
import logging
from player.player import Player
from player.shadow import PlayersShadow
from environment.wall import Wall 
from other.utilz import Utilz 
from tg.database import db
from tg.bot import BotManager

from environment.star import Star
import time
from environment.trader import Trader
import json
from environment.pet import Pet 
from environment.tnt import Tnt


logging.basicConfig(level=logging.DEBUG)
load_dotenv()

API_TOKEN = os.getenv('KEY')

current_world = 1

def load_js(fil):
    with open(fil, "r") as f:
        return json.load(f)
def display_hearts(player:Player, screen):
    full_hearts = player.health // 10
    half_heart_remainder = (player.health % 10) // 5


    for i in range(full_hearts):
        screen.blit(heart, (i * 36, 70)) 


    if half_heart_remainder:
        screen.blit(half_heart, (full_hearts * 36, 70))

    empty_hearts = 10 - full_hearts - int(bool(half_heart_remainder))
    for i in range(empty_hearts):
        screen.blit(no_heart, ((full_hearts + int(bool(half_heart_remainder)) + i) * 36, 70))
    screen.blit(star, (WIDTH-120, 55))
    Utilz.draw_text(screen, str(player.score), 32, WIDTH-40,70 )

sw:list = load_js("swords.json")
pt:list  = load_js("potions.json")
pz:list  = load_js("pets.json")
ar:list  = load_js("artifacts.json")

all_items =sw 
all_items.extend(pt)
all_items.extend(ar)
all_items.extend(pz)
loaded_srfs = {f["name"]: pygame.transform.scale(pygame.image.load(f["image"]), (75,75)) for f in all_items}

loaded_pots = {f["name"]: pygame.transform.scale(pygame.image.load(f["image"]), (57,57)) for f in pt}

sword_ui = pygame.transform.scale(pygame.image.load("res/sword_ui.png"), (150,150))
artifact_ui = pygame.transform.scale(pygame.image.load("res/artifact_ui.png"), (150,150))

half_heart = pygame.transform.scale(pygame.image.load("res/heart-half.png"), (32,32))
heart = pygame.transform.scale(pygame.image.load("res/heart.png"), (32,32))
no_heart = pygame.transform.scale(pygame.image.load("res/no-heart.png"), (32,32))
star = pygame.transform.scale(pygame.image.load("res/star.png"), (64,64))

won = pygame.transform.scale(pygame.image.load("res/won.png"), (WIDTH,HEIGHT))
died = pygame.transform.scale(pygame.image.load("res/died.png"), (WIDTH,HEIGHT))

backpack = pygame.transform.scale(pygame.image.load("res/backpack.png"), (270,540))

def main():
    global current_world
    current_world = 1
    all_sprites = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    exits = Utilz.get_exits(CELLS_X, CELLS_Y)
    for exit in exits:
        exit.kill()
        walls.add(exit)
    grid, walls,exits = Utilz.generate_labyrinth(CELLS_X, CELLS_Y,gr=walls)
    grid2, walls2,exits2 = Utilz.generate_labyrinth(CELLS_X, CELLS_Y, (216, 186, 70), (255,255,255))
    stars_group = pygame.sprite.Group()
    def swap():
        global current_world, walls
        # change worlds 
        current_world = 2 
        walls = walls2
        player.walls = walls2 
        shadow.walls = walls2 
        if player.pet != None:
            player.pet.walls = walls2 
            player.pet.finder.walls = walls2 
        stars_group.remove(stars_group)
        for star in stars_group.sprites():
            star.walls = walls2
        for tnt in tnt_group.sprites():
            tnt.walls = walls2
        logging.debug("Swapped worlds.")

    player = Player(walls,swap,None, None,None)
    all_sprites.add(player)
    shadow = PlayersShadow(player, walls, grid,os.getenv("DEBUG")=="0")
    shadow_group = pygame.sprite.GroupSingle() # bros sigma alone
    shadow_group.add(shadow)
    player.shadow = shadow
    pet_group = pygame.sprite.Group()
    pet_group.add()
    player.pet_group = pet_group

    tnt_group = pygame.sprite.Group()
    trader_group = pygame.sprite.Group()
    trader_will_appear_after = random.randint(FPS,FPS*30)
    player.trader_group = trader_group


    tick = 0
    running = True
    rr_5 = backpack.get_rect()
    rr_5.center = (0+ rr_5.width/2,HEIGHT/2)
    pygame.time.wait(6000)
    rp_timer = 0
    bot_manager = BotManager(API_TOKEN, player, trader_group,shadow) 
    bot_thread = threading.Thread(target=bot_manager.start, daemon=True)
    bot_thread.start()
    while running:
        tick += 1
        clock.tick(FPS)
        start_upd_t = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
        if current_world == 1:
            wall_thrd = threading.Thread(target=walls.update,args=[player])
        else:
            wall_thrd = threading.Thread(target=walls2.update,args=[player])
        if player.died: 
            bot_manager.bot.stop_bot()
            rp_timer += 1

            if rp_timer > FPS*10:
                rp_timer = float("-inf")
                return
                
            screen.blit(died, pygame.Rect((0,0), (WIDTH,HEIGHT)))
            pygame.display.flip()
            continue
        if player.won: 
            bot_manager.bot.stop_bot()
            screen.blit(won, pygame.Rect((0,0), (WIDTH,HEIGHT)))
            pygame.display.flip()
            continue
        wall_thrd.start()
        screen.fill(BLACK)
        all_sprites.update()
        stars_group.update(player,current_world)
        shadow_group.update(player)
        pet_group.update(player)
        trader_group.update(player, current_world)
        tnt_group.update(player, current_world)

        # Rendering

        all_sprites.draw(screen)

        shadow_group.draw(screen)
        pet_group.draw(screen)

        connection, cursor = db.connect_database()
        cursor.execute("SELECT * FROM players")
        players = cursor.fetchall()
        connection.close()
        best = {"moves": 0, "id": 00000, "banned": 0, "tg_name": "real_master"}
        # Update move counts
        for player_data in players:
            # new fomat: 
            data = {"tg_id":player_data[0],"moves": player_data[1], "banned": player_data[2], "tg_name": player_data[3]}
            if data["moves"] > best["moves"] and (data["banned"] == 0 or data["banned"] == None):
                best = data
        # Spawn stars
        if tick % 6 == 0:
            if len(stars_group.sprites()) < (CELLS_X * CELLS_Y / 200):

                
                
                player_x, player_y = player.rect.topleft
                
                rx = random.randint(max(1, player_x // CELL_SIZE ), min(CELLS_X - 2, player_x // CELL_SIZE)) * CELL_SIZE
                ry = random.randint(max(1, player_y // CELL_SIZE), min(CELLS_Y - 2, player_y // CELL_SIZE)) * CELL_SIZE
                
                rx += random.randint(1,20)*CELL_SIZE
                ry += random.randint(1,20)*CELL_SIZE
                if current_world == 1:

                    new_star = Star((rx, ry), stars_group, walls)
                else:
                    new_star = Star((rx, ry), stars_group, walls2)            

                stars_group.add(new_star)
        # Spawn tnt
        if tick % (FPS*6) == 0:


                
                
            player_x, player_y = player.rect.topleft
            
            rx = random.randint(max(1, player_x // CELL_SIZE ), min(CELLS_X - 2, player_x // CELL_SIZE)) * CELL_SIZE
            ry = random.randint(max(1, player_y // CELL_SIZE), min(CELLS_Y - 2, player_y // CELL_SIZE)) * CELL_SIZE
            
            rx += random.randint(1,4)*CELL_SIZE
            ry += random.randint(1,4)*CELL_SIZE

            if current_world == 1:

                new_tnt = Tnt((rx, ry), tnt_group, walls,shadow,stars_group)   
            else:
                new_tnt = Tnt((rx, ry), tnt_group, walls2,shadow,stars_group)            

            tnt_group.add(new_tnt)
            logging.debug("TNT spawned in")
            # else:
            #     logging.debug("Enough stars")
        if tick % trader_will_appear_after == 0: 
            rx = random.randint(max(1, player_x // CELL_SIZE ), min(CELLS_X - 2, player_x // CELL_SIZE)) * CELL_SIZE
            ry = random.randint(max(1, player_y // CELL_SIZE), min(CELLS_Y - 2, player_y // CELL_SIZE)) * CELL_SIZE
            rx += random.randint(1,20)*CELL_SIZE
            ry += random.randint(1,20)*CELL_SIZE
            if current_world == 1:

                new_trader = Trader((rx, ry), stars_group, walls)
            else:
                new_trader = Trader((rx, ry), trader_group, walls2)   
            logging.debug("Trader appeared") 
            trader_group.add(new_trader)

            trader_will_appear_after = random.randint(FPS,FPS*30)

        wall_thrd.join() # we making separate theard for optimisation there are like 90k of walls
        if current_world == 1:
            walls.draw(screen)
        else:
            walls2.draw(screen)
        tnt_group.draw(screen)
        stars_group.draw(screen)
        for trader in trader_group.sprites():
            trader.blit_img(screen)
        trader_group.draw(screen)
        Utilz.draw_text(screen, "Player with most moves: @" + str(best["tg_name"])+", count of their moves: "+str(best["moves"]), 18, WIDTH / 2, 10)
        # draw last message in top right
        Utilz.draw_text(screen, "Last message: " + bot_manager.last_message, 18, WIDTH/2, 30)
        if player.health <= 0:
            logging.info("You died :(")
            player.died = True
        Utilz.draw_text(screen, shadow.state, 24, shadow.rect.centerx,shadow.rect.top)
        Utilz.draw_text(screen, str(shadow.health) + " HP", 24, shadow.rect.centerx,shadow.rect.top-30)
        Utilz.draw_text(screen, str(shadow.rebirths) + " REBIRTHS", 24, shadow.rect.centerx,shadow.rect.top-60)
        # we should divide spacing by 2, find the center of the screen, and add to that point spacing and set it as right. (right).
        spacing = 32
        random_rect = sword_ui.get_rect()
        random_rect.center = (WIDTH/2, HEIGHT-100)
        spacing /= 2
        center = WIDTH/2
        center += spacing
        random_rect.left = center 


        screen.blit(sword_ui, random_rect)


        random_rect_3 = sword_ui.get_rect()
        random_rect_3.center = ((WIDTH/2)-sword_ui.get_width() , HEIGHT-100)
        center -= spacing* 2
        random_rect_3.right = center 

        screen.blit(artifact_ui, random_rect_3)
        display_hearts(player, screen)
        if player.equipped_sword_i != None: 


            n = player.equipped_sword_i["name"]
            srf = loaded_srfs[n]
            random_rect_2 = srf.get_rect()
            random_rect_2.center = random_rect.center
            random_rect_2.y += 20

            screen.blit(srf, random_rect_2)
        if player.equipped_artifact != None: 
            n = player.equipped_artifact["name"]
            srf = loaded_srfs[n]
            random_rect_4 = srf.get_rect()
            random_rect_4.center = random_rect_3.center
            random_rect_4.y += 20
            screen.blit(srf, random_rect_4)
        if player.equipped_pet != None:
            Utilz.draw_text(screen, player.equipped_pet["name"].upper(), 26, player.pet.rect.centerx, player.pet.rect.top-40)
        pots = ", ".join([key + f" ({round(value/FPS)})" for key, value in player.potions.items()])
        # Utilz.draw_text(screen, "Your potions: " + pots, 26, WIDTH/2, 130)
        if player.backpack_turned_on:
            screen.blit(backpack, rr_5)
            # BLIT POTIONS
            base_y = 230
            base_x = 35
            y_mod = 87
            x_mod = 0

            for pot, duration in player.potions.items():
                new_random_rect = pygame.Rect((base_x, base_y),Utilz.a_tuples((57, 57), (0,rr_5.top)))
                screen.blit(loaded_pots[pot], new_random_rect)
                Utilz.draw_text_with_next_line(screen, pot, 17, base_x+135, base_y+0,130)
                Utilz.draw_text(screen, Utilz.timeee(duration), 17, base_x+135, base_y+40)
                base_x += x_mod
                base_y += y_mod

        # logging.debug("AVG SPF: " +str(start_upd_t*FPS-time.time()))
    


        pygame.display.flip()
        if not running:
            break



if __name__ == "__main__":
    while True:
        main()