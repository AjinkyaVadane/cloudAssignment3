from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello Ajinkya I am up !"