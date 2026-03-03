import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

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

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]
    if not user:
        return apology("User not found", 404)
    cash = user["cash"]

    rows = db.execute("""
        SELECT symbol, SUM(shares) AS total_shares
        FROM transactions
        WHERE user_id = ?
        GROUP BY symbol
    """, user_id)
    
    portfolio = []
    total = cash
    
    for row in rows:
        symbol = row["symbol"]
        shares = row["total_shares"]
        quote = lookup(symbol)
        price = quote["price"] if quote else 0
        total_value = price * shares
        
        portfolio.append({
            "symbol": symbol,
            "shares": shares,
            "price": price,
            "total": total_value
        })
        total += total_value
    return render_template("index.html", portfolio=portfolio, cash=cash, total=total)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        if not symbol:
            return apology("must provide stock symbol", 400)
        quote = lookup(symbol.upper())
        if quote is None:
            return apology("invalid symbol", 400)
        try:
            shares = int(shares)
            if shares <= 0:
                return apology("shares must be a positive integer", 400)
        except ValueError:
            return apology("shares must be a positive integer", 400)
        # Calculate cost
        price = quote["price"]
        total = price * shares
        # Fetch user's cash
        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
        if user["cash"] < total:
            return apology("insufficient funds", 400)
        # Update user's cash
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total, session["user_id"])
        # Insert transaction
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                session["user_id"], quote["symbol"], shares, price)
        flash("Bought!")
        return redirect("/")

    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute(
        "SELECT symbol, shares, price, transacted FROM transactions WHERE user_id = ? ORDER BY transacted DESC", 
        session["user_id"])
    return render_template("history.html", transactions=transactions)   
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear() # Forget any user_id
   
    if request.method == "POST":
        # Check username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Check password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Check username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    # Redirect user to login form
    return redirect("/")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide stock symbol", 400)
        quote_result = lookup(symbol.upper())
        if not quote_result:
            return apology("invalid symbol", 400)
        return render_template("quoted.html", quote=quote_result)
    else:
        return render_template("quote.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        
        print(f"DEBUG: Username: {username}")
        print(f"DEBUG: Password: {password}")
        print(f"DEBUG: Confirmation: {confirmation}")
        
        
        if not username:
            return apology("must provide username", 400)
        if not password:
            return apology("must provide password", 400)
        if password != confirmation:
            return apology("passwords do not match", 400)
        
        hash_pw = generate_password_hash(password)
        try:
            result = db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)", 
            username, hash_pw)
        except Exception as e:
            return apology(f"Registration error: {e}", 400)
        
        # Log the new user in
        rows = db.execute("SELECT id FROM users WHERE username = ?", username)
        if not rows:
            return apology("registration successful, but login failed", 400)
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("register.html") 
      
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    holdings = db.execute(
        "SELECT symbol, SUM(shares) as shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING shares > 0",
        session["user_id"],
    )
    symbols = [row["symbol"] for row in holdings]
    
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        
        # Check validation
        if not symbol or symbol not in symbols:
            return apology("Invalid symbol", 400)
        try:
            shares = int(shares)
        except (TypeError, ValueError):
            return apology("Shares must be a positive integer", 400) 
        # Check user own shares
        user_shares = next(item for item in holdings if item["symbol"] == symbol)["shares"]
        if shares > user_shares:
            return apology("You have more than enough shares", 400)
        
        # Selling calculation & confirmation
        quote = lookup(symbol)
        price = quote["price"]
        total = price * shares
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total, session["user_id"])  
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                session["user_id"], symbol, -shares, price)
        flash("Sold!")
        return redirect("/")
    else:
        return render_template("sell.html", symbols=symbols)
    