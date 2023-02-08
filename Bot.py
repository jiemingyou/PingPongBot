import Keys
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import database

TG_KEY = Keys.TG_KEY
DB_URL = Keys.DB_URL
DB_KEY = Keys.DB_KEY

# Intializing bot
bot = telebot.TeleBot(TG_KEY)

# Conencting to the DB
db = database.Database(DB_URL, DB_KEY)

# Temporary storage
match_info = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "The bot is already running!")

# Add a new player
@bot.message_handler(commands=['newplayer'])
def add_player(message):
    msg = bot.send_message(message.chat.id, "Hi! What's your name?")
    bot.register_next_step_handler(msg, create_user)

# Creates the user
def create_user(message):
    username = message.text
    db.insert_player(name = username)
    bot.reply_to(message, f"User {username} created succesfully. Type /newscore to log a match result")

# Generates the users markup for choosing the correct player
def users_markup(users) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    for id in list(users.keys()):
        markup.add(InlineKeyboardButton(users[id], callback_data=id))
    return markup

# Processing the markup
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    
    # New match
    if not match_info:
        match_info["p1"] = call.data
        msg = bot.send_message(call.message.chat.id, "Who was your opponent?")
    
    # Opponent
    elif "p2" not in match_info.keys():
        match_info["p2"] = call.data
        msg = bot.send_message(call.message.chat.id, "Who won?")
    
    # Winner
    elif call.data in match_info.values():
        match_info["winner"] = call.data
        msg = bot.send_message(call.message.chat.id, "Send the score")
        log_score_forwarder(msg)

# Log a match
@bot.message_handler(commands=['newscore'])
def ask_information(message):
    match_info.clear()
    msg = "1. Select your name (to create a new player, call /newplayer)\n2. Select your opponent\n3. Select the winner"
    players = db.get_players()
    bot.send_message(message.chat.id, msg, reply_markup=users_markup(players))

def log_score_forwarder(message):
    msg = bot.send_message(message.chat.id, "e.g. 11-5")
    bot.register_next_step_handler(msg, log_score)

def log_score(message):
    try:
        score = message.text.split("-")
        bot.reply_to(message, score)
    except:
        bot.send_message(message.chat.id, "Invalid score. Please try again.")
    bot.send_message(message.chat.id, "Score saved succesfully")
    


# Start the bot
bot.infinity_polling()

