from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tasks.db")


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html",
                                   code=403,
                                   message="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html",
                                   code=403,
                                   message="must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
                rows[0]["hash"], request.form.get("password")):
            return render_template("error.html",
                                   code=403,
                                   message="invalid username/password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # validate the username
        if username == "":
            return render_template("error.html",
                                   code=403,
                                   message="must provide username")
        result = db.execute("SELECT * FROM users WHERE username = ?", username)
        if result:
            return render_template("error.html",
                                   code=403,
                                   message="username is already used")

        # check that the password field is not empty
        if not password or not confirmation:
            return render_template("error.html",
                                   code=403,
                                   message="Provide a password")

        # check that the two passwords are equal
        if password != confirmation:
            return render_template("error.html",
                                   code=403,
                                   message="Password are not equal")

        if not db.execute("INSERT INTO users(username, hash) VALUES(?, ?)",
                          username, generate_password_hash(password)):
            return render_template(
                "error.html",
                code=403,
                message="Something went wrong. Please try again. ")

        return redirect("/login")
    else:
        return render_template("register.html")
