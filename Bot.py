import Keys
import PySimpleGUI as sg
import telebot

# Initialize the bot
bot = telebot.TeleBot(Keys.BOT_API_KEY)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)

print("Bot starting")

# Start the bot
bot.infinity_polling()