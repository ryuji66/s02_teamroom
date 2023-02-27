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
    # entryテーブルと中間テーブルを結合して必要な情報を取得
    #query = '''
        #SELECT entry.title, lang.name, genre.name, entry.mail_address, entry.time, entry.level, entry.body
        #FROM entry
        #JOIN entry_lang ON entry.id = entry_lang.entry_id
        #JOIN lang ON entry_lang.lang_id = lang.id
        #JOIN entry_genre ON entry.id = entry_genre.entry_id
        #JOIN genre ON entry_genre.genre_id = genre.id
    #'''
    #c.execute(query)
    #data = c.fetchall()

    return render_template("index.html")



@app.route("/input", methods=["GET", "POST"])
def input():
    if request.method == "POST":

        get_project = request.form.get("project")
        get_mail = request.form.get("mail")
        get_language = request.form.get("language")
        get_genre = request.form.get("genre")
        get_posted = datetime.date
        get_period = request.form.get("period")
        get_complete = request.form.get("complete")
        get_person = request.form.get("person")
        get_text = request.form.get("text")

        # projectが入力されてるか確認
        if not get_project:
            flash("プロジェクト名を入力してください")

        # mailが入力されてるか確認
        elif not get_mail:
            flash("メールアドレスを入力してください")

        # languageが入力されてるか確認
        elif not get_language:
            flash("プログラミング言語を入力してください")

        # genreが入力されてるか確認
        elif not get_genre:
            flash("ジャンルを入力してください")

        # periodが入力されてるか確認
        elif not get_period:
            flash("募集期間を入力してください")

        # completeが入力されてるか確認
        elif not get_complete:
            flash("制作期間を入力してください")

        # personが入力されてるか確認
        elif not get_person:
            flash("募集する人のレベルを入力してください")

        # db.execute("INSERT INTO entry (title, mail_address, time, level, day_posted, day_end, body) values(?, ?, ?, ?, ?, ?, ?)", get_project, get_mail, get_complete, get_person, get_posted, get_period, get_text)

        return render_template("index.html")

    else:
        return render_template("input.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/mypage", methods=["GET", "POST"])
def mypage():
    if request.method == "POST":

        return redirect("/")

    else:
        return render_template("mypage.html")