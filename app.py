# import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
# from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import time
# import math
from helpers import login_required
# import sqlite3
# from flask import current_app, g

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)フラッシュ表示を有効にするために必要だった
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# データベース(sqlite3)に接続
#conn = sqlite3.connect('board.db')

#@app.before_request
#def before_request():
    #g.db = sqlite3.connect('board.db')


#def get_db():
    #if 'db' not in g:
        #g.db = sqlite3.connect('board.db')
    #return g.db

# Configure CS50 Library to use SQLite database CS50のパッケージを使用
db = SQL("sqlite:///board.db")


@app.route("/")
def index():
    # タグボタンの表示名を表示させるためにデータを取ってきてる
    genres = db.execute("SELECT * FROM genres")
    # その他を削除する
    genres.pop()

    # 上と同じ
    languages = db.execute("SELECT * FROM languages")
    # その他を削除する
    languages.pop()

    checking = db.execute("SELECT entry_id, day_end FROM entries")
    get_today = str(datetime.datetime.now().date())

    for i,j in enumerate(checking):
        # noneの場合は本来ないがテストデータがnoneになってしまっているため導入
        if checking[i]["day_end"] != None:
            # 今日と締切日を比較し締切日を過ぎていればis_activeを0にする
            formatted_date1 = time.strptime(str(checking[i]["day_end"]), "%Y-%m-%d")
            formatted_date2 = time.strptime(get_today, "%Y-%m-%d")
            if formatted_date1 < formatted_date2:
                db.execute("UPDATE entries SET is_active = 0 WHERE entry_id = ?", checking[i]["entry_id"])

    # entriesテーブルと中間テーブルを結合して必要な情報を取得
    entries = db.execute("""
        SELECT entries.*, GROUP_CONCAT(languages.name) as language_name, users.username
        FROM entries
        LEFT JOIN language_to_entry
        ON entries.entry_id = language_to_entry.entry_id
        LEFT JOIN languages
        ON languages.language_id = language_to_entry.language_id
        LEFT JOIN users
        ON users.user_id = entries.user_id
        WHERE is_active = 1
        GROUP BY entries.entry_id;
    """)

    #print(entry_languages)

    return render_template('index.html', genres=genres, languages=languages, entries=entries) #, entry_languages=entry_languages


@app.route("/input", methods=["GET", "POST"])
@login_required
def input():
    if request.method == "POST":

        get_project = request.form.get("project")
        get_mail = request.form.get("mail")
        get_languagelist = request.form.getlist("language")
        get_genre = request.form.get("genre")
        get_posted = datetime.datetime.now().date()
        get_period = str(request.form.get("period"))
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
        elif not get_languagelist:
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

        # textが入力されてるか確認
        elif not get_text:
            flash("テキストを何か入力してください")
            return redirect('input')

        db.execute("INSERT INTO entries (title, mail_address, time, level, genre, day_posted, day_end, body, user_id) values (?, ?, ?, ?, ?, ?, ?, ?, ?)", get_project, get_mail, get_complete, get_person, get_genre, get_posted, get_period, get_text, session["user_id"])
        # 工夫しがいがありそう
        get_entryid = db.execute("SELECT entry_id FROM entries WHERE title = ? AND mail_address = ? AND time = ? AND level = ? AND genre = ? AND day_posted = ? AND day_end = ? AND body = ?", get_project, get_mail, get_complete, get_person, get_genre, get_posted, get_period, get_text)

        for i in get_languagelist:
            get_language = int(i)
            db.execute("INSERT INTO language_to_entry (language_id, entry_id) values(?, ?)", get_language, get_entryid[0]["entry_id"])

        return redirect('/')

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
        rows = db.execute("SELECT * FROM users WHERE username = ?", get_username)

        # ユーザーネームが一つしかないか確認する
        if len(rows) == 1:
            flash("そのユーザーネームは既に使用されています")
            return redirect("register")

        # そのユーザーネームが登録されていなければ
        if len(rows) != 1:

            # パスワードをハッシュ化する
            hash_password = generate_password_hash(get_password)

        # 新規登録処理
        user_id = db.execute("INSERT INTO users(username, hash) values(?, ?)", get_username, hash_password)

        # ログイン状態にする
        session["user_id"] = user_id

        return redirect("/")

    else:
        return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("ユーザーネームを入力してください")
            return redirect('login')

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("パスワードを入力してください")
            return redirect('login')

        #*Loginを実現している
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("正しいユーザーネームもしくはパスワードを入力してください")
            return redirect("/login")
        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
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
@login_required
def mypage():
    # entriesテーブルと中間テーブルを結合して必要な情報を取得
    entries = db.execute("""
        SELECT entries.*, GROUP_CONCAT(languages.name) as language_name, users.username
        FROM entries
        LEFT JOIN language_to_entry
        ON entries.entry_id = language_to_entry.entry_id
        LEFT JOIN languages
        ON languages.language_id = language_to_entry.language_id
        LEFT JOIN users
        ON users.user_id = entries.user_id
        WHERE is_active = 1
        AND entries.user_id = ?
        GROUP BY entries.entry_id;
    """, session["user_id"])


    if request.method == "POST":
        db.execute("DELETE FROM language_to_entry WHERE entry_id = ?", request.form.get("deleteid"))
        db.execute("DELETE FROM entries WHERE entry_id = ?", request.form.get("deleteid"))

        entries = db.execute("""
            SELECT entries.*, GROUP_CONCAT(languages.name) as language_name, users.username
            FROM entries
            LEFT JOIN language_to_entry
            ON entries.entry_id = language_to_entry.entry_id
            LEFT JOIN languages
            ON languages.language_id = language_to_entry.language_id
            LEFT JOIN users
            ON users.user_id = entries.user_id
            WHERE is_active = 1
            AND entries.user_id = ?
            GROUP BY entries.entry_id;
        """, session["user_id"])

        return render_template("mypage.html", entries = entries)

    else:
        return render_template("mypage.html", entries = entries)

@app.route("/output", methods=["GET", "POST"])
@login_required
def output():
    if request.method == "POST":

        get_project = request.form.get("project")
        get_mail = request.form.get("mail")
        get_languagelist = request.form.getlist("language")
        get_genre = request.form.get("genre")
        get_posted = datetime.datetime.now().date()
        get_period = str(request.form.get("period"))
        get_complete = request.form.get("complete")
        get_person = request.form.get("person")
        get_text = request.form.get("text")

        # projectが入力されてるか確認
        if not get_project:
            flash("プロジェクト名を入力してください")
            return redirect('output')

        # mailが入力されてるか確認
        elif not get_mail:
            flash("メールアドレスを入力してください")
            return redirect('output')

        # languageが入力されてるか確認
        elif not get_languagelist:
            flash("プログラミング言語を入力してください")
            return redirect('output')

        # genreが入力されてるか確認
        elif not get_genre:
            flash("ジャンルを入力してください")
            return redirect('output')

        # periodが入力されてるか確認
        elif not get_period:
            flash("募集期間を入力してください")
            return redirect('output')

        # completeが入力されてるか確認
        elif not get_complete:
            flash("制作期間を入力してください")
            return redirect('output')

        # personが入力されてるか確認
        elif not get_person:
            flash("募集する人のレベルを入力してください")
            return redirect('output')

        # textが入力されてるか確認
        elif not get_text:
            flash("テキストを何か入力してください")
            return redirect('output')

        db.execute("INSERT INTO entries (title, mail_address, time, level, genre, day_posted, day_end, body, user_id) values (?, ?, ?, ?, ?, ?, ?, ?, ?)", get_project, get_mail, get_complete, get_person, get_genre, get_posted, get_period, get_text, session["user_id"])
        # 工夫しがいがありそう
        get_entryid = db.execute("SELECT entry_id FROM entries WHERE title = ? AND mail_address = ? AND time = ? AND level = ? AND genre = ? AND day_posted = ? AND day_end = ? AND body = ?", get_project, get_mail, get_complete, get_person, get_genre, get_posted, get_period, get_text)

        for i in get_languagelist:
            get_language = int(i)
            db.execute("INSERT INTO language_to_entry (language_id, entry_id) values(?, ?)", get_language, get_entryid[0]["entry_id"])

        return render_template('watch.html')

    else:
        return render_template("output.html")

@app.route("/watch")
def watch():
    # タグボタンの表示名を表示させるためにデータを取ってきてる
    genres = db.execute("SELECT * FROM genres")
    # その他を削除する
    genres.pop()

    # 上と同じ
    languages = db.execute("SELECT * FROM languages")
    # その他を削除する
    languages.pop()

    checking = db.execute("SELECT entry_id, day_end FROM entries")
    get_today = str(datetime.datetime.now().date())

    for i,j in enumerate(checking):
        # noneの場合は本来ないがテストデータがnoneになってしまっているため導入
        if checking[i]["day_end"] != None:
            # 今日と締切日を比較し締切日を過ぎていればis_activeを0にする
            formatted_date1 = time.strptime(str(checking[i]["day_end"]), "%Y-%m-%d")
            formatted_date2 = time.strptime(get_today, "%Y-%m-%d")
            if formatted_date1 < formatted_date2:
                db.execute("UPDATE entries SET is_active = 0 WHERE entry_id = ?", checking[i]["entry_id"])

    # entriesテーブルと中間テーブルを結合して必要な情報を取得
    entries = db.execute("""
        SELECT entries.*, GROUP_CONCAT(languages.name) as language_name, users.username
        FROM entries
        LEFT JOIN language_to_entry
        ON entries.entry_id = language_to_entry.entry_id
        LEFT JOIN languages
        ON languages.language_id = language_to_entry.language_id
        LEFT JOIN users
        ON users.user_id = entries.user_id
        WHERE is_active = 0
        GROUP BY entries.entry_id;
    """)

    #print(entry_languages)

    return render_template('watch.html', genres=genres, languages=languages, entries=entries)



@app.route("/index_tag/<string:tag>")
def index_tag(tag):

    # タグボタンの表示名を表示させるためにデータを取ってきてる
    genres = db.execute("SELECT * FROM genres")
    # その他を削除する
    genres.pop()

    # 上と同じ
    languages = db.execute("SELECT * FROM languages")
    # その他を削除する
    languages.pop()

    # entriesテーブルと中間テーブルを結合して必要な情報を取得
    entries = db.execute("""
        SELECT entries.*, GROUP_CONCAT(languages.name) as language_name, users.username
        FROM entries
        LEFT JOIN language_to_entry
        ON entries.entry_id = language_to_entry.entry_id
        LEFT JOIN languages
        ON languages.language_id = language_to_entry.language_id
        LEFT JOIN users
        ON users.user_id = entries.user_id
        WHERE is_active = 1
        GROUP BY entries.entry_id;
    """)

    return render_template('index_tag.html', genres=genres, languages=languages, entries=entries)
    # return render_template('index.html')
