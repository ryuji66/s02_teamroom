import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import math
#from helpers import apology, login_required
import sqlite3
from flask import current_app, g

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)フラッシュ表示を有効にするために必要だった
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# データベース(sqlite3)に接続
conn = sqlite3.connect('board.db')
c = conn.cursor()

@app.before_request
def before_request():
    g.db = sqlite3.connect('board.db')


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('board.db')
    return g.db

@app.route("/")
def index():
    # entriesテーブルと中間テーブルを結合して必要な情報を取得
    query = '''
    SELECT entries.*, languages.name
    FROM entries
    JOIN language_to_entry ON entries.entry_id = language_to_entry.entry_id
    JOIN languages ON language_to_entry.language_id = languages.language_id;
    '''
    # entriesテーブルのデータを取得
    #データベース接続を開き、クエリを実行
    db = get_db()
    cur = db.cursor()
    cur.execute(query)
    #entriesテーブルすべてのデータを取得してentries変数に格納
    entries = cur.fetchall()

    #usersテーブルすべてのデータを取得してusers変数に格納
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()

    #index.htmlテンプレートにレンダリング。変数2つをテンプレートに渡す
    cur.close()
    return render_template('index.html', entries=entries, users=users)


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
            return redirect('input')

        # mailが入力されてるか確認
        elif not get_mail:
            flash("メールアドレスを入力してください")
            return redirect('input')

        # languageが入力されてるか確認
        elif not get_language:
            flash("プログラミング言語を入力してください")
            return redirect('input')

        # genreが入力されてるか確認
        elif not get_genre:
            flash("ジャンルを入力してください")
            return redirect('input')

        # periodが入力されてるか確認
        elif not get_period:
            flash("募集期間を入力してください")
            return redirect('input')

        # completeが入力されてるか確認
        elif not get_complete:
            flash("制作期間を入力してください")
            return redirect('input')

        # personが入力されてるか確認
        elif not get_person:
            flash("募集する人のレベルを入力してください")
            return redirect('input')

        g.db.execute("INSERT INTO entries (title, mail_address, time, level, genre, day_posted, day_end, body) values (?, ?, ?, ?, ?, ?, ?, ?)", (get_project, get_mail, get_complete, get_person, get_genre, get_posted, get_period, get_text))
        # 工夫しがいがありそう
        get_entryid = g.db.execute("SELECT entry_id FROM entries WHERE title = ? AND mail_address = ? AND time = ? AND level = ? AND genre = ? AND day_posted = ? AND day_end = ? AND body = ?", (get_project, get_mail, get_complete, get_person, get_genre, get_posted, get_period, get_text))
        g.db.execute("INSERT INTO language_to_entry (language_id, entry_id) values(?, ?)", (get_language, get_entryid))

        return render_template("index.html")

    else:
        return render_template("input.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        get_username = request.form.get("username")
        get_password = request.form.get("password")
        get_again = request.form.get("confirmation")

        # usernameが入力されているか確認
        if not get_username:
            flash("ユーザーネームを入力してください")
            return redirect("register")

        # passwordが入力されているか確認
        elif not get_password:
            flash("パスワードを入力してください")
            return redirect("register")

        # confirmationが入力されているか確認
        elif not get_again:
            flash("パスワードを再入力してください")
            return redirect("register")

        # パスワードと再入力の一致を確認
        elif get_password != get_again:
            flash("パスワードと再入力は一致させてください")
            return redirect("register")

        # Query database for username
        rows = g.db.execute("SELECT * FROM users WHERE username = ?", get_username)

        # ユーザーネームが一つしかないか確認する
        if len(rows) == 1:
            flash("そのユーザーネームは既に使用されています")
            return redirect("register")

        # そのユーザーネームが登録されていなければ
        if len(rows) != 1:

            # パスワードをハッシュ化する
            hash_password = generate_password_hash(get_password)

        # 新規登録処理
        user_id = g.db.execute("INSERT INTO users(username, hash) values(?, ?)", get_username, hash_password)

        # ログイン状態にする
        session["user_id"] = user_id

        return redirect("register")

    else:
        return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        #*Loginを実現している
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/mypage", methods=["GET", "POST"])
def mypage():
    user_id = session.get('user_id', None)


    if request.method == "POST":

        return redirect("/")

    else:
        return render_template("mypage.html")