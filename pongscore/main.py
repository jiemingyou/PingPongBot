from flask import Flask
from bot import main
import threading

app = Flask(__name__)


@app.route("/")
def index():
    thread = threading.Thread(target=main)
    thread.start()
    return "Congratulations, it's a web app!"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)