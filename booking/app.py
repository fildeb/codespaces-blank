import calendar
import sqlite3
import uuid

from datetime import date
from flask import Flask, jsonify, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import (
    Session as FlaskSession,
)  # import the Session class from the flask_session module with a different name

from helpers import apology, login_required
from functools import wraps

app = Flask(__name__)
app.secret_key = "filthy"
app.config.update(EXPLAIN_TEMPLATE_LOADING=True)

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
FlaskSession(app)

# configure CS50 Library to use SQLite database
db = sqlite3.connect("/workspaces/codespaces-blank/booking/bookings.db")


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")


@app.route("/booking", methods=["GET", "POST"])
def booking():
    # Get year and month
    today = date.today()
    year = today.year
    month = today.month
    text_cal = calendar.HTMLCalendar(firstweekday=0)
    cal = text_cal.formatmonth(year, month, withyear=True)

    # Format each day in the cal cells to the right format
    for day in range(1, 32):
        formatted_day = f"{day:02d}.{month:02d}.{year}"
        cal = cal.replace(f">{day}<", f' data-date="{formatted_day}">{day}<')

    if request.method == "GET":
        return render_template("booking.html", cal=cal)

    if request.method == "POST":
        data = request.get_json()
        selectedDate = data.get("selectedDate")

        # Store the selected date in a session for later use
        session["selectedDate"] = selectedDate

    return jsonify(message="Date recied successfully")


@app.route("/select-time", methods=["POST"])
def select_time():
    if request.is_json:
        data = request.get_json()
        time = data.get("selectedTime")

        # Store the selected time in a session for later use
        session["selected_time"] = time

        return "Time selected successfully"
    else:
        return "Invalid request", 400


@app.route("/make-reservation", methods=["POST"])
def make_reservation():
    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    time = session.get("selected_time")
    selectedDate = session.get("selectedDate")

    if time is None:
        return "Time not found in session"
    if selectedDate is None:
        return "Date not found in session"

    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")

        # Generate a random ID for the booking
        booking_id = str(uuid.uuid4())

        # Insert data to SQL table / database and ensures that the changes made by the INSERT statement are permanently stored in the database.
        cursor.execute(
            "INSERT INTO bookings (name, phone, date, time, id) VALUES (?, ?, ?, ?, ?)",
            (name, phone, selectedDate, time, booking_id),
        )
        conn.commit()

        return redirect("/")
    else:
        return "invalid request", 400


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    try:
        # Store username in a variable
        username = request.form.get("username")
        # Store password in a variable, then hash the password and store the hash in another variable
        password = request.form.get("password")
        confirmpassword = request.form.get("confirmation")

    except ValueError:
        render_template("/")

    # Check for valid input in username field
    if username is None or username == "":
        return apology("Username field is empty")

    # Check for valid input in password field
    if password is None or password == "":
        return apology("Password field is empty")

    if confirmpassword != password:
        return apology("Passwords doesnt match")

    # Check if username is taken
    usercheck = db.execute("SELECT * FROM users WHERE username = '" + username + "'")
    result = usercheck.fetchall()
    if len(usercheck) == 1:
        return apology("Username already exists")

    # Hash password
    pwhash = generate_password_hash(password, method="pbkdf2", salt_length=16)

    # If everything checks out, insert new user to database
    db.execute("INSERT INTO users (username, hash) VALUES (?, ?);", username, pwhash)

    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        print("Username:", request.form.get("username"))
        print("Password:", request.form.get("password"))
        print("Rows:", rows)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/current_bookings", methods=["GET", "POST"])
@login_required
def admin_home():
    if request.method == "GET":
        bookings = db.execute("SELECT * FROM bookings")
        return render_template("current_bookings.html", bookings=bookings)


@app.route("/cancel-booking", methods=["POST"])
def cancel_booking():
    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    try:
        # Get the  row ID from the request
        row_id = request.get_json()["rowId"]

        # Execute the SQL query to delete the row from the database
        cursor.execute("DELETE FROM bookings WHERE id = ?", (row_id,))

        conn.commit()

        return jsonify({"success": True, "message": "Booking canceled successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
