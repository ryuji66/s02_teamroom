import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import math
#from helpers import apology, login_required, lookup, usd
import sqlite3

app = Flask(__name__)

# データベースに接続
conn = sqlite3.connect('board.db')
c = conn.cursor()


@app.route("/")
def index():
    if request.method == "GET":

        return render_template("index.html")



@app.route("/input", methods=["GET", "POST"])
def input():
    if request.method == "POST":
       
        return redirect("/")

    else:
        return render_template("input.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
       
        return redirect("/")

    else:
        return render_template("register.html")