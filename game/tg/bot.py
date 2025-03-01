# telebot_manager.py

from dotenv import load_dotenv
import logging
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
import random
from telebot import TeleBot, types
from difflib import SequenceMatcher
import os
from tg.database import db
from environment.trader import Trader
from other.cons import CELL_SIZE
import json
from telebot import formatting
from other.utilz import Utilz
from player.player import Player


def load_js(fil):
    with open(fil, "r") as f:
        return json.load(f)


sw = load_js("swords.json")
ar = load_js("artifacts.json")
pt = load_js("potions.json")
pz = load_js("pets.json")

all_things: list = sw
all_things.extend(ar)
all_things.extend(pt)
all_things.extend(pz)

load_dotenv()
attack_sounds = [
    pygame.mixer.Sound(os.path.join("res/music/attack", file))
    for file in os.listdir("res/music/attack")
    if file.endswith((".mp3", ".wav", ".ogg", ".flac"))
]
potion_sound = pygame.mixer.Sound("res/music/loot/potion.ogg")
purchase_sound = pygame.mixer.Sound("res/music/loot/purchase.ogg")
inv_toggle = pygame.mixer.Sound("res/music/inv/1.ogg")

class BotManager:
    def __init__(self, API_TOKEN, player, traders, shadow):
        self.bot = TeleBot(API_TOKEN, skip_pending=True, parse_mode="MARKDOWN")
        self.last_message = ""
        self.player: Player = player
        self.traders = traders
        self.shadow = shadow
        self.skid = 1

        @self.bot.message_handler(commands=["start"])
        def handle_start(message):
            markup = types.ReplyKeyboardMarkup(row_width=2)
            button_up = types.KeyboardButton("⬆️ Up")
            button_down = types.KeyboardButton("⬇️ Down")
            button_left = types.KeyboardButton("⬅️ Left")
            button_right = types.KeyboardButton("➡️ Right")
            markup.add(button_up, button_down, button_left, button_right)
            button_interact = types.KeyboardButton("🎅 Interact")
            button_balance = types.KeyboardButton("💵 Balance")
            markup.add(button_interact, button_balance)

            button_attack = types.KeyboardButton("⚔ ATTACK")
            markup.add(button_attack)
            button_backpack = types.KeyboardButton("🎒 BACKPACK")
            markup.add(button_backpack)
            self.bot.send_message(
                message.chat.id, "Use the arrow buttons to move", reply_markup=markup
            )

        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message: types.Message):
            logging.debug("Received message: " + message.text)
            text = message.text.lower()
            self.set_last_message(message.text)

            # Assuming that 'player' is an instance of the Player class
            if not db.user_exists(message.from_user.id):
                db.create_player(message.from_user.id, message.from_user.username)
            if self.similar(text, "up") > 0.4:
                player.uppy = True
                db.update_move_count(message.from_user.id)
                random.choice(player.walks).play()
            elif self.similar(text, "down") > 0.4:
                player.downy = True
                db.update_move_count(message.from_user.id)
                random.choice(player.walks).play()
            elif self.similar(text, "left") > 0.4:
                player.lefty = True
                db.update_move_count(message.from_user.id)
                random.choice(player.walks).play()
            elif self.similar(text, "right") > 0.4:
                player.righty = True
                db.update_move_count(message.from_user.id)
                random.choice(player.walks).play()
            elif self.similar(text, "interact") > 0.4:
                self.handle_trade(message)
            elif self.similar(text, "balance") > 0.4:
                dat = self.get_info(message.from_user.id)
                # 0 = moves, 1 score
                self.bot.send_message(
                    message.chat.id,
                    f"You have {formatting.hbold(str(dat[0]) + ' moves')} and {formatting.hbold(str(dat[1]) + ' score')}",
                    parse_mode="HTML",
                )
            elif self.similar(text, "attack") > 0.4:
                dist = Utilz.get_distance(self.player, self.shadow)
                if dist < CELL_SIZE * 3:
                    if self.player.equipped_sword_i != None:
                        self.shadow.health -= (
                            self.player.equipped_sword_i["damage"] * self.player.dmgmult
                        )
                        logging.info("Hit Shadow")
                    else:
                        self.shadow.health -= 1 * self.player.dmgmult
                        logging.info("Hit Shadow")
                    random.choice(attack_sounds).play()
                logging.debug(dist)
            elif self.similar(text, "backpack") > 0.4:
                self.player.backpack_turned_on = not self.player.backpack_turned_on
                inv_toggle.play()
            else:
                self.bot.send_message(
                    message.chat.id,
                    "What do you mean? 🤔"
                    ,reply_to_message_id=message.i,
)
        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_query(call: types.CallbackQuery):
            trader_with_minimal_dist = [None, float("inf")]
            for trader in self.traders.sprites():
                dist_clcd = trader.get_distance(self.player)
                if dist_clcd < trader_with_minimal_dist[1]:
                    trader_with_minimal_dist = [trader, dist_clcd]
            if trader_with_minimal_dist[1] > CELL_SIZE * 4:
                self.bot.send_message(call.message.chat.id, "You are too far!")
                return
            if (
                call.data == "Swords"
                or call.data == "Potions"
                or call.data == "Artifacts"
                or call.data == "Pets"
            ):
                trader_with_minimal_dist = [None, float("inf")]
                for trader in self.traders.sprites():
                    dist_clcd = trader.get_distance(self.player)
                    if dist_clcd < trader_with_minimal_dist[1]:
                        trader_with_minimal_dist = [trader, dist_clcd]
                if trader_with_minimal_dist[1] > CELL_SIZE * 4:
                    self.bot.send_message(call.message.chat.id, "You are too far!")
                    return
                markup = types.InlineKeyboardMarkup()
                for selling_item in trader.selling[call.data]:
                    new_btn = types.InlineKeyboardButton(
                        f'{selling_item["name"]} ({selling_item["level"]})',
                        callback_data=selling_item["uuid"],
                    )
                    markup.add(new_btn)
                self.bot.send_message(
                    call.message.chat.id,
                    f"Oh, see you wanna some {call.data}... Ok, I think I have that. What would you like to see?",
                    reply_markup=markup,
                )
            else:
                # checking is an item
                e = None
                for item in all_things:
                    if item["uuid"] == call.data:
                        e = item
                if e == None:
                    if call.data.startswith("confirm"):
                        n = call.data.split("+")[1]
                        e = None
                        for item in all_things:
                            if item["uuid"] == n:
                                e = item
                        if e == None:
                            return
                        is_selling = False
                        # print(trader_with_minimal_dist[0].selling)
                        # for selling_i in trader_with_minimal_dist[0].selling.keys():
                        #     # print(trader_with_minimal_dist[0].selling[selling_i],e)
                        #     if Utilz.mathcer(e, trader_with_minimal_dist[0].selling[selling_i]):
                        #         print("IS SELLING")
                        #         is_selling = True

                        # if not is_selling:
                        #     self.bot.send_message(
                        #         call.message.chat.id,
                        #         "I don't sell that! Are you trying to scam me?!",
                        #     )
                        #     return
                        if e in player.unlocked:
                            if e["type"] == "artifact":
                                player.equipped_artifact = e
                            if e["type"] == "sword":
                                player.equipped_sword = e["level"]
                                player.equipped_sword_i = e
                            if e["type"] == "pet":
                                player.equipped_pet = e
                            return
                        if player.score >= e["score_price"] // self.skid:
                            players_moves = db.get_info(call.from_user.id)
                            logging.debug("PLAYER MOVES " + str(players_moves))
                            players_moves = players_moves[1]
                            if players_moves >= e["moves_price"] // self.skid:
                                if e["type"] == "sword":
                                    if e["level"] > player.equipped_sword:
                                        player.equipped_sword = e["level"]
                                        player.equipped_sword_i = e
                                    else:
                                        self.bot.send_message(
                                            call.message.chat.id,
                                            f"You already have better / this item!",
                                        )
                                        return
                                if e["type"] == "potion":
                                    potion_sound.play()
                                else:
                                    purchase_sound.play()
                                if e["type"] == "artifact":
                                    if e["name"] == "The Artifact of Music":
                                        pygame.mixer_music.load("res/music/2/music.mp3")
                                        pygame.mixer_music.play(-1)
                                    else:
                                        pygame.mixer_music.load("res/music/1/music.mp3")
                                        pygame.mixer_music.play(-1)
                                    if e["name"] == "The Bless of Shoper":
                                        self.skid = 3
                                    else:
                                        self.skid = 1
                                if e["type"] == "artifact":
                                    player.equipped_artifact = e
                                    player.unlocked.append(e)
                                if e["type"] == "sword":
                                    player.equipped_sword = e["level"]
                                    player.equipped_sword_i = e
                                    player.unlocked.append(e)
                                if e["type"] == "pet":
                                    player.unlocked.append(e)
                                    player.equipped_pet = e
                                player.score -= e["score_price"] // self.skid
                                db.update_move_count(
                                    call.from_user.id, -(e["moves_price"] // self.skid)
                                )
                                self.bot.send_message(
                                    call.message.chat.id, f"Purchase successfull!"
                                )

                                # EQUIP THE THING

                                if e["type"] == "potion":
                                    if player.potions.get(e["uuid"], None) == None:
                                        player.potions[e["uuid"]] = e["duration"]
                                    else:
                                        player.potions[e["uuid"]] += e["duration"]
                                return
                        self.bot.send_message(
                            call.message.chat.id, f"You have not enought currency!"
                        )

                    else:
                        return
                # is_selling = False
                # for selling_i in trader_with_minimal_dist[0].selling.keys():
                #     if n in trader_with_minimal_dist[0].selling[selling_i]:
                #         is_selling = True

                # if not is_selling:
                #     self.bot.send_message(call.message.chat.id, "I don't sell that! Are you trying to scam me?!")
                #     return
                markup = types.InlineKeyboardMarkup()
                new_btn = types.InlineKeyboardButton(
                    f"Buy!", callback_data="confirm+" + e["uuid"]
                )
                markup.add(new_btn)
                dat = self.get_info(call.from_user.id)
                # 0 = moves, 1 score
                chars = "Characteristics: \n\n"
                if e["type"] == "sword":
                    chars += f"Damage: {e['damage']}\nLevel: {e['level']}\n\n"
                elif e["type"] == "potion":
                    chars += f"Duration: {Utilz.timeee(e['duration'])}\nLevel: {e['level']}\n\n"
                elif e["type"] == "pet":
                    # speed":24, "reach":3,"stun_chance":0.0004, "damage_cd":18,damage
                    chars += f"Damage: {e['damage']}\nSpeed: {e['speed']}\nReach: {e['reach']}\nStun chance: {e['stun_chance']}\nDamage cooldown: {e['damage_cd']}\nCoolness: Sick\n\n"
                self.bot.send_photo(
                    call.message.chat.id,
                    photo=open(e["image"], "rb"),
                    caption=f'{formatting.hbold(e["name"])}\n\n{formatting.hitalic(e["desc"])}\n\n{chars}\nWanna this item? It costs only {formatting.hbold(str(int(e["score_price"])//self.skid))} score, but you need to pay additional {formatting.hbold(str(int(e["moves_price"])//self.skid))} moves. \n\n\nYou have {formatting.hbold(str(dat[0]))} moves and {formatting.hbold(str(dat[1]))} score',
                    reply_markup=markup,
                    parse_mode="HTML",
                )

        # Start the bot

    def start(self):
        logging.debug("Bot started")
        self.bot.polling()

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def handle_trade(self, message: types.Message):
        trader_with_minimal_dist = [None, float("inf")]
        for trader in self.traders.sprites():
            dist_clcd = trader.get_distance(self.player)
            if dist_clcd < trader_with_minimal_dist[1]:
                trader_with_minimal_dist = [trader, dist_clcd]
        if trader_with_minimal_dist[1] > CELL_SIZE * 4:
            self.bot.send_message(message.chat.id, "You are too far!")
            return
        markup = types.InlineKeyboardMarkup()
        for selling_categories in trader.selling.keys():
            new_btn = types.InlineKeyboardButton(
                selling_categories, callback_data=selling_categories
            )
            markup.add(new_btn)

        self.bot.send_message(
            message.chat.id,
            "Hello, stanger! I've got some pretty cool stuff to show you! Wanna buy some?",
            reply_markup=markup,
        )

    def set_last_message(self, message):
        self.last_message = message

    def get_info(self, tg_id):
        data = db.get_info(str(tg_id))

        data_moves = data[1]
        data_score = self.player.score
        return (data_moves, data_score)
