import Keys
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import database
from datetime import datetime

TG_KEY = Keys.TG_KEY
DB_URL = Keys.DB_URL
DB_KEY = Keys.DB_KEY

# Intializing bot
bot = telebot.TeleBot(TG_KEY)

# Conencting to the DB
db = database.Database(DB_URL, DB_KEY)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "The bot is already running!")

# Match history
@bot.message_handler(commands=['history'])
def history(message):
    p = db.get_players()
    results = db.match_history()
    for res in results:
        msg = f"{res['created_at'][:10]}: {p[res['player1']]} ({res['score1']}) - ({res['score2']}) {p[res['player2']]}"
        bot.send_message(message.chat.id, msg)

# Add a new player
@bot.message_handler(commands=['newplayer'])
def add_player(message):
    msg = bot.send_message(message.chat.id, "Hi! What's your name?")
    bot.register_next_step_handler(msg, create_user)

# Creates the user
def create_user(message):
    username = message.text
    players = db.get_players().values()
    if username in players:
        bot.reply_to(message, f"There's already a user called {username}. Type /storematch to log a match result")
        return

    db.insert_player(name = username)
    bot.reply_to(message, f"User {username} created succesfully. Type /storematch to log a match result")

# Storing a match
@bot.message_handler(commands=['storematch'])
def process_player_1_name(message):
    player_names = db.get_players()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for player_name in player_names.values():
        markup.add(player_name)
    msg = bot.send_message(chat_id=message.chat.id, text="Choose player 1:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_player_1_choice, player_names)

def process_player_1_choice(message, player_names):
    player_1_name = message.text
    if player_1_name not in player_names.values():
        msg = bot.send_message(chat_id=message.chat.id, text="Invalid player name. Choose player 1:")
        bot.register_next_step_handler(msg, process_player_1_choice, player_names)
        return
    msg = bot.send_message(chat_id=message.chat.id, text="Enter player 2 name:")
    bot.register_next_step_handler(msg, process_player_2_name, player_1_name, player_names)

def process_player_2_name(message, player_1_name, player_names):
    player_2_name = message.text
    msg = bot.send_message(chat_id=message.chat.id, text="Enter winner name:")
    bot.register_next_step_handler(msg, process_winner_name, player_1_name, player_2_name, player_names)

def process_winner_name(message, player_1_name, player_2_name, player_names):
    winner_name = message.text
    markup = ReplyKeyboardRemove()
    msg = bot.send_message(chat_id=message.chat.id, text="Enter scoreline: (e.g. 11-5)", reply_markup=markup)
    bot.register_next_step_handler(msg, process_scoreline, player_1_name, player_2_name, winner_name, player_names)

def process_scoreline(message, player_1_name, player_2_name, winner_name, player_names):
    try:
        scoreline = message.text.split("-")
        winner_score = 0 if scoreline[0] > scoreline[1] else 1
        s2 = scoreline[winner_score] if winner_name == player_1_name else scoreline[abs(winner_score-1)]
        s1 = scoreline[0] if s1 == scoreline[1] else scoreline[1]
    except:
        msg = bot.send_message(chat_id=message.chat.id, text="Invalid input. Resend the scoreline:")
        bot.register_next_step_handler(msg, process_scoreline)
        return
    
    # name: id
    p = {v: k for k, v in player_names.items()}

    # Storing to the db
    db.insert_match(p[player_1_name], p[player_2_name], int(s1), int(s2), p[winner_name])

    # TODO: Updating the elo

    bot.send_message(chat_id=message.chat.id, text="Match stored successfully!")
    


# Start the bot
bot.infinity_polling()

