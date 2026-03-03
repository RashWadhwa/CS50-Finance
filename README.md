# CS50 Finance – Flask Stock Trading App

This project is a Flask-based stock trading web application developed as part of a university module. It allows users to register, log in, look up stock quotes, buy and sell shares, and review their full transaction history. All monetary values are displayed in **US dollars ($)**, and user passwords are securely hashed with Werkzeug.

## Features

- **User accounts**
  - Registration and login with server-side validation
  - Passwords hashed using `werkzeug.security` (no plain-text storage)
- **Stock trading**
  - Quote view to check prices by symbol (e.g. AMZN, MSFT, GOOGL)
  - Buy and sell shares with balance and position checks
  - Portfolio view showing holdings, current prices, and total value in USD
- **History**
  - Complete ledger of all transactions (symbol, shares, price in $, timestamp)
  - Negative share counts used to represent sales
- **UI**
  - Consistent layout with a footer on each page
  - Footer includes an HTML validator link/button to check markup validity

## Manual Testing

The application was manually tested from the user’s perspective, including both expected and unexpected usage:

### Expected usage

- Registered new users and verified:
  - Successful login and redirection
  - Portfolio page loads with correct initial cash and empty holdings
- Requested quotes using valid stock symbols and confirmed prices render correctly
- Purchased the same stock multiple times and checked:
  - Share counts aggregate correctly in the portfolio
  - Total position value and cash balance update accurately
- Sold all and some of an existing position and verified:
  - Portfolio reflects reduced or zero share counts
  - Cash balance adjusts correctly
- Confirmed the **History** page lists all buy and sell transactions for the logged-in user in chronological order

### Unexpected and edge cases

- Entered alphabetical strings where **numbers** were expected (e.g. shares) and verified validation/handling
- Entered **zero, negative, and floating‑point** values where only positive integers are allowed
- Attempted to:
  - Spend more cash than the user has
  - Sell more shares than the user owns  
  and confirmed these actions are blocked with appropriate feedback
- Input invalid or non‑existent stock symbols to ensure errors are handled correctly
- Tested inputs containing potentially dangerous characters such as `'` and `;` to help guard against SQL injection
- Used the HTML validator button in the footer on each page to check the validity of the rendered HTML

## Tech Stack

- **Backend:** Python, Flask  
- **Auth & Security:** Werkzeug password hashing  
- **Database:** SQLite (or compatible SQL database)  
- **Templates:** Jinja2 (HTML/CSS)

## Running the App

1. Clone the repository and create a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
Set environment variables (for example):

bash
export FLASK_APP=app.py
export FLASK_ENV=development
Start the development server:

bash
flask run
Open http://127.0.0.1:5000/ in your browser.

This project demonstrates secure authentication, server-side validation, basic finance logic, and robust manual testing practices in a Flask web application.

