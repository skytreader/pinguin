from flask import Flask

import random

app = Flask(__name__)

@app.route("/", methods=["GET", "POST", "PUT", "PATCH"])
def index():
    return "test", random.choice((200, 404, 502))

if __name__ == "__main__":
    app.run(port=3141)
