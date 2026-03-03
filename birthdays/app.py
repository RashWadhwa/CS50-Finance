import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///birthdays.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # TODO: Add the user's entry into the database
        
        # Access form data
        name = request.form.get("name")
        month = request.form.get("month")
        day = request.form.get("day")

        # Setting up validation 
        if not name or not month or not day:             
             return redirect("/")

        try:
            # Converting to integer month/day
            month = int(month)
            day = int(day)
        except ValueError:               
            return redirect("/")

        # Additional validation 
        if not (1 <= month <= 12) or not (1 <= day <= 31):             
             return redirect("/")

        # Insert data into database
        db.execute("INSERT INTO birthdays (name, month, day) VALUES(?, ?, ?)", name, month, day)

        # Redirect to the GET route after successful submission
        return redirect("/")

    else:

        # TODO: Display the entries in the database on index.html
        
        # Query database for all birthdays
        birthdays = db.execute("SELECT * FROM birthdays")

        # Render the template, passing the list of birthdays
        return render_template("index.html", birthdays=birthdays)

        


