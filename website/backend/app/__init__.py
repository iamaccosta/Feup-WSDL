from flask import Flask

app = Flask(__name__)
import os

@app.route("/")
def hello_world():
    return "Hello World!"
