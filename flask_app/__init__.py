from flask import Flask, session
from flask_session import Session # dodgy code here
app = Flask(__name__)
app.secret_key = "secret book stuff"
app.config['SESSION_TYPE'] = 'filesystem' # dodgy code here
Session(app) # dodgy code here