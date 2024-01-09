import sqlite3
import threading
import uuid

from flask import Flask, g, jsonify, redirect, render_template, request, session
from googlesearch import search
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required

app = Flask(__name__)
app.secret_key = "694201337"
app.config["DATABASE"] = "/workspaces/codespaces-blank/crawler/accounts.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config["DATABASE"])
    return db

def close_db(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.before_request
def before_request():
    g.db = get_db()

@app.teardown_appcontext
def teardown_appcontext(exception=None):
    close_db(exception)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    
    # Get the search term from user inputs from HTML page
    searchword = request.form.get("search")

    # Check if searchword is None before using it
    if searchword is not None:
        searchresult = list(search(searchword, num_results=5))
        return render_template("search_result.html", searchresult=searchresult)
    else:
        return render_template("index.html", error="Please enter a search term")
    

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    try:
        username = request.form.get("username")
        pw = request.form.get("pw")
        confirmpw = request.form.get("confirmpw")
        # HASH PASSWORD
        hashed_pw = generate_password_hash(pw, method="pbkdf2", salt_length=16)
        # Generate random ID for user
        user_id = str(uuid.uuid4())
    except ValueError:
        return redirect("/")

    # Checking for correct inputs
    if username is None or username == "":
        return apology("Username field is empty")
    if pw is None or pw == "":
        return apology("Password field is empty")
    if confirmpw != pw:
        return apology("Passwords doesn't match!")
    
    try:
        # Checking for taken username
        usercheck = g.db.execute("SELECT * FROM accounts WHERE username = '" + username + "'")
        result = usercheck.fetchall()
        if len(result) == 1:
            return apology("That username already exists")
    except ValueError:
        return "Value error"
    
    # Insert new user to database
    print("")
    print("This will be inserted:")
    print("User ID: ",user_id)
    print("Username: ",username)
    print("Password: ",pw)
    print("")
    g.db.execute("INSERT INTO accounts (id, username, password) VALUES (?, ?, ?);", (user_id, username, pw))
    g.db.commit()
    status = g.db.execute("SELECT * FROM accounts;")
    print (status)

    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    if request.method == ("POST"):
        username = request.form.get("username")
        pw = request.form.get("pw")
        # Check if username and password is correct
        usercheck = g.db.execute("SELECT username, password FROM accounts WHERE username = ? AND password = ?", username, pw)
        if (len(usercheck) == 1):
            # Remember which user has logged in
            session["user_id"] = usercheck[0]["id"]

            # Redirect user to home page
            return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
