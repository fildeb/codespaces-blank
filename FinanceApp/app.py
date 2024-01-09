import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__, template_folder='templates')
app.config.update(
    EXPLAIN_TEMPLATE_LOADING = True
)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
@login_required
def index():
    """Show portfolio of stocks"""
    if request.method == "GET":
        user_id = session["user_id"]
        userdata = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        for row in userdata:
            username = row["username"]
        stockdata = db.execute("SELECT company_name, SUM(shares), SUM(total) FROM purchases WHERE id = ? GROUP BY company_name", user_id)
        total = db.execute("SELECT SUM(total) FROM purchases WHERE id = ?", user_id)
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)

        if total[0]["SUM(total)"] is None:
            return render_template ('index0.html', username=username)
        else:
            # Convert values from table to int
            cash_value = float(cash[0]["cash"])
            total_marketvalue = float(total[0]["SUM(total)"])
            total_value = cash_value + total_marketvalue

    return render_template("index.html", username=username, stockdata=stockdata, cash=cash_value, total=total_value)


# Return sender to the buy-page if buy-button is clicked
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    # Get access to the users balance/cash reserve
    user_id = session["user_id"]
    cashtable = db.execute("SELECT cash FROM users WHERE id = ?", user_id)

    # Convert cash to correct currency with the USD function
    for row in cashtable:
        balance = row["cash"]
        balanceusd = usd(balance)

    if request.method == "GET":
        return render_template("buy.html", balance=balanceusd)

    # Return "buy_quote" template with stock info, buy button and balance
    if request.method == 'POST':

        # Show error message if blank input or page not found
        symbol = request.form.get('symbol')
        stock_info = lookup(symbol)
        if (stock_info is None):
            return apology('Blank input or company doesnt exist')

        # Get transaction details and update the "purchases" table
        shares = request.form.get('shares')
        company = stock_info["name"]
        cost_price = float(stock_info["price"])
        today = date.today()
        total = (cost_price * float(shares))

        # Return apology if insufficient funds
        if (balance < total):
            return apology('Insufficient funds')

        # Insert transaction to purchases AND transactions table if successful
        db.execute("INSERT INTO purchases (id, company_name, cost_price, shares, total, date) VALUES (?, ?, ?, ?, ?, ?)", user_id, company, cost_price, shares, total, today)
        db.execute("INSERT INTO transactions (type, symbol, price, shares, date, time, id) VALUES ('buy', ?, ?, ?, ?, 'time', ?)", company, cost_price, shares, today, user_id)

        # Update users balance
        balance = balance - (int(shares) * int(stock_info["price"]))
        db.execute("UPDATE users SET cash = ? WHERE id = ?", balance, user_id)

    return redirect ('/')


@app.route("/history", methods = ["GET"])
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    transactions = db.execute('SELECT * FROM transactions WHERE id = ?', user_id)

    return render_template('history.html', transactions=transactions)


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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
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


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():

    # Render quote page
    if request.method == 'GET':
        return render_template('quote.html')

    # Get user input and try to find company via Lookup function, return apology if not found
    if request.method == 'POST':
        symbol = request.form.get('symbol')
        info = lookup(symbol)
        if (info is None):
            return apology("Input is blank or company does not exist")

        # Return ticker info if company is found with Lookup function
        return render_template('quoted.html', ticker2=info)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    try:
        # Store username in a variable
        username = request.form.get("username")
        # Store password in a variables, then hash the password and store the hash in another variable
        password = request.form.get("password")
        confirmpassword = request.form.get("confirmation")

    except ValueError:
        render_template("/")

    # Check for valid input in username field
    if username is None or username == '':
        return apology('Username field is empty')

    # Check for valid input in password field
    if password is None or password == '':
        return apology('Password field is empty')

    if (confirmpassword != password):
        return apology('Passwords doesnt match')

    # Check if username is taken
    usercheck = db.execute("SELECT * FROM users WHERE username = '" + username + "'")
    if len(usercheck) == 1:
        return apology('Username already exists')

    # Hash password
    pwhash = generate_password_hash(password, method='pbkdf2', salt_length=16)

    # If everything checks out, insert new user to database
    db.execute("INSERT INTO users (username, hash) VALUES (?, ?);", username, pwhash)

    return redirect ("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    # Get user ID and date
    user_id = session["user_id"]
    today = date.today()

    if request.method == 'GET':
        companies = db.execute("SELECT company_name FROM purchases WHERE id = ? GROUP BY company_name", user_id)
        return render_template('sell.html', companies=companies)

    if request.method == 'POST':
        # Get HTML input
        sellstockname = request.form.get('symbol')
        sellstockamount = request.form.get('shares')

        # Convert to int
        sellstockamount = int(sellstockamount)

        # Get stockinfo from the input
        stockinfo = lookup(sellstockname)
        company_name = stockinfo["name"]
        stockprice = stockinfo["price"]

        # Get current holding
        current_holding = db.execute('SELECT SUM(shares), SUM(total) FROM purchases WHERE id = ? AND company_name = ?', user_id, sellstockname)

        for row in current_holding:
            current_shares = row["SUM(shares)"]
            current_total = row["SUM(total)"]
            current_shares = int(current_shares)
            current_total = int(current_total)

        # Update users holdings in database
        new_amount_stocks = (current_shares - sellstockamount)
        new_amount_total = (new_amount_stocks * stockprice)

        # Update shareholdings in portfolio
        if (sellstockamount > current_shares):
            return apology('Not enough stocks')

        elif (sellstockamount == current_shares):
            db.execute('DELETE FROM purchases WHERE id = ? AND company_name = ?', user_id, sellstockname)

        else:
            db.execute('UPDATE purchases SET shares = ? AND total = ? WHERE id = ? AND company_name = ?', new_amount_stocks, new_amount_total, user_id, sellstockname)

        print ('right after db.execute')

        # Update wallet with cash
        user_info = db.execute('SELECT * FROM users WHERE id = ?', user_id)
        for row in user_info:
            cash = row['cash']
            cash = int(cash)

        total_sales = (float(sellstockamount) * float(stockprice))
        cash_updated = (cash + total_sales)
        db.execute('UPDATE users SET cash = ? WHERE id = ?', cash_updated, user_id)

        # Update transactions
        db.execute("INSERT INTO transactions (type, symbol, price, shares, date, time, id) VALUES ('sell', ?, ?, ?, ?, 'time', ?)", company_name, stockprice, sellstockamount, today, user_id)

        print('end of it')
        print(new_amount_stocks)

    return redirect('/')
