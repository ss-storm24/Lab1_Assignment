import os

from flask import Flask, session, render_template, request, url_for, redirect, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
# DATABASE_URL = "postgresql://wlkiwvwgqndwtf:411e57176f8293d3bafb47d1ad1899c1c9048b85f641b92b4e6b1e9e506351ae@ec2-54-209-165-105.compute-1.amazonaws.com:5432/d87jp096ui7i1f"
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


# App routes for pages
@app.route("/")
def index():
    if session.get("user_id") is not None:
        return redirect(url_for("dashboard"))
    else:
        return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login_post():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user_check1 = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()

        if user_check1 is None or check_password_hash(user_check1.password, password) is None:
            flash("Incorrect login information. Please check your username and/or password and try again.")
            return redirect(url_for("login"))
        else:
            session["user_id"] = user_check1.username
            return redirect(url_for("dashboard"))


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register", methods=["GET", "POST"])
def register_post():
    if request.method == "POST":
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')

        if name is "" or username is "" or password is "":
            flash("Please fill all fields to register.")
            return redirect(url_for("register"))

        if db.execute("SELECT username FROM users WHERE username = :username", {"username": username}).rowcount > 0:
            flash("Username already exists")
            return redirect(url_for("register"))
        else:
            db.execute("INSERT INTO users (name, username, password) VALUES(:name, :username, :password)", {"name": name, "username": username, "password": generate_password_hash(password, method='sha256')})
            db.commit()
            flash("Registration completed successfully!")

    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))


@app.route("/search", methods=["GET","POST"])
def search():
    if request.method == "POST":
        book_search = request.form.get("search")
        # If the user searches by ISBN
        if request.form.get("inlineRadioOptions") == "option1":


return render_template("search.html")


if __name__ == "__main__":
    app.run()