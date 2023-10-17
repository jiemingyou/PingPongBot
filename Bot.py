import Keys
from elo import calc_elo
import telebot
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
import database
from datetime import datetime


def main():
    TG_KEY = Keys.TG_KEY
    DB_URL = Keys.DB_URL
    DB_KEY = Keys.DB_KEY

    # Intializing bot
    bot = telebot.TeleBot(TG_KEY)

    # Conencting to the DB
    db = database.Database(DB_URL, DB_KEY)

    @bot.message_handler(commands=["leaderboard"])
    def leaderboard(message):
        lb = db.leaderboard()
        msg = "Elo Ranking 🏆\n-----------\n"
        for row in lb:
            msg += f"{row['name']}\t{row['elo']} (W{row['wins']} L{row['loses']})\n"
        bot.send_message(message.chat.id, msg)

    @bot.message_handler(commands=["start", "help"])
    def send_welcome(message):
        msg = """\
PingPongBot V1 🤖🏓

This bot stores table tennis match results and keeps track of players' ELO ratings. 
Everyone's ELO-score starts from 1500.
You will gain elo points from winning games and lose points from losing.
The amount will be determined by the ELO score of your opponent and your final scoreline.

Commands:
/newplayer - Register a new player. You only need to do this once.
/storematch - Save a match result.
/leaderboard - Current standings.
/history - See past matches
/help - How to use the bot

If not working, dm @jiemingyou
        """
        bot.reply_to(message, msg)

    # Match history
    @bot.message_handler(commands=["history"])
    def history(message):
        p = db.get_players()
        results = db.match_history()
        idx = min(10, len(results))
        msg = ""
        for res in results[:idx]:
            msg += f"{res['created_at'][:10]}: {p[res['winner']]} ({res['winner_score']}) - ({res['loser_score']}) {p[res['loser']]}\n"

        bot.send_message(message.chat.id, msg)

    # Asks for the username
    @bot.message_handler(commands=["newplayer"])
    def add_player(message):
        msg = bot.send_message(message.chat.id, "Hi! What's your name?")
        bot.register_next_step_handler(msg, create_user)

    # Creates the user
    def create_user(message):
        username = message.text
        players = db.get_players().values()
        if username in players:
            bot.reply_to(
                message,
                f"There's already a user called {username}. Type /storematch to log a match result",
            )
            return

        db.insert_player(name=username)
        bot.reply_to(
            message,
            f"User {username} created succesfully. Type /storematch to log a match result",
        )

    # Asks for the finner
    @bot.message_handler(commands=["storematch"])
    def process_winner_name(message):
        player_names = db.get_players()

        markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        for player_name in list(player_names.values()) + ["New Player 🏓"]:
            markup.add(player_name)
        msg = bot.send_message(
            chat_id=message.chat.id, text="Who won? 🏆", reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_winner_choice, player_names)

    # Saves the winner
    def process_winner_choice(message, player_names):
        winner = message.text

        # Create a new user
        if winner == "New Player 🏓":
            add_player(message)
            return

        # Wrong input
        elif winner not in player_names.values():
            msg = bot.send_message(
                chat_id=message.chat.id, text="Invalid player name. Choose the winner 🏆"
            )
            bot.register_next_step_handler(msg, process_winner_choice, player_names)
            return

        msg = bot.send_message(chat_id=message.chat.id, text="Who lost?")

        bot.register_next_step_handler(msg, process_loser_name, winner, player_names)

    # Saves the loser
    def process_loser_name(message, winner, player_names):
        loser = message.text
        if loser == winner:
            msg = bot.send_message(message.chat.id, "You can't play against yourself!")
            bot.register_next_step_handler(
                msg, process_loser_name, winner, player_names
            )
            return

        markup = ReplyKeyboardRemove()
        msg = bot.send_message(
            chat_id=message.chat.id,
            text="Enter scoreline: (e.g. 11-5)",
            reply_markup=markup,
        )
        bot.register_next_step_handler(
            msg, process_scoreline, winner, loser, player_names
        )

    # Saves the scoreline and inserts the data to the database
    def process_scoreline(message, winner, loser, player_names):
        try:
            scoreline = message.text.split("-")
            winner_score = 0 if int(scoreline[0]) > int(scoreline[1]) else 1
            s1 = scoreline[winner_score]
            s2 = scoreline[abs(winner_score - 1)]
        except:
            msg = bot.send_message(
                chat_id=message.chat.id, text="Invalid input. Resend the scoreline:"
            )
            bot.register_next_step_handler(msg, process_scoreline)
            return

        # name: id map
        p = {v: k for k, v in player_names.items()}
        winner = p[winner]
        loser = p[loser]

        # Storing to the db
        db.insert_match(winner, loser, int(s1), int(s2))

        # Updating the elo
        winner_stats = db.get_player_info(winner)
        loser_stats = db.get_player_info(loser)
        winner_elo = winner_stats["elo"]
        loser_elo = loser_stats["elo"]
        elo1, elo2 = calc_elo(winner_elo, loser_elo, 1, abs(winner_score - 1))
        db.update_elo(elo1, winner)
        db.update_elo(elo2, loser)

        # Updating W/L
        winner_w = winner_stats["wins"]
        loser_l = loser_stats["loses"]
        db.update_wins(winner_w + 1, winner)
        db.update_loses(loser_l + 1, loser)

        bot.send_message(chat_id=message.chat.id, text="Match stored successfully!")

    # Start the bot
    bot.infinity_polling()
