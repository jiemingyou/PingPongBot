from flask import Flask
from bot import main
import threading

app = Flask(__name__)


@app.route("/")
def index():
    thread = threading.Thread(target=main)
    thread.start()
    return "Congratulations, it's a web app!"