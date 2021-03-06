import os

from flask import Flask, session, render_template, request, url_for, redirect, flash
from flask import json, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Set up database
DATABASE_URL = "postgresql://wlkiwvwgqndwtf:411e57176f8293d3bafb47d1ad1899c1c9048b85f641b92b4e6b1e9e506351ae@ec2-54-209-165-105.compute-1.amazonaws.com:5432/d87jp096ui7i1f"
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Google Books API Key
GOOGLEBOOKS_API_KEY = "AIzaSyCBeFrtM_OO0HfF0eOgKNNT5ebTNQWKWxs"


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
            db.execute("INSERT INTO users (name, username, password) VALUES(:name, :username, :password)",
                       {"name": name, "username": username, "password": generate_password_hash(password, method='sha256')})
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
        book_search = request.form.get("search_r")
        u_search = db.execute("SELECT * FROM books WHERE isbn LIKE LOWER(:usearch) OR LOWER(title) LIKE LOWER(:usearch) OR LOWER(author) LIKE LOWER(:usearch)",
                              {"usearch": book_search}).fetchall()
        return render_template("search.html", results = u_search)

@app.route("/book/<string:isbn>", methods=["GET", "POST"])
def book_result(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    if db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).rowcount == 0:
        return render_template("error.html", message="Book not found. Please search again."), 404

    res = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": isbn, "key": GOOGLEBOOKS_API_KEY})


    if request.method == "POST":
        if db.execute("SELECT * FROM reviews WHERE user_id = :uder_id AND book_id = :book_id", {"user_id": session["user_id"], "book_id": book_id}).fetchone():
            return render_template("error.html", header="Sorry!", message="You can only submit one review per book.", isbn = isbn)
        else:
            rating = request.form.get("rating")
            review = request.form.get("review")
            db.execute("INSERT INTO reviews (user_id, book_id, rating, review) VALUES (:user_id, :book_id, :rating, :review)",
                       {"user_id": session["user_id"], "book_id": book_id, "rating": rating, "review": review})
            db.commit()
            text = "You've successfully submitted a review!"

    revs = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall()

    return render_template("books.html", header="Submitted!", text = text, book = book, isbn = isbn, reviews = revs)

@app.route("/api/<string:isbn>")
def book_api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    if book is None:
        return jsonify({"error": "Invalid ISBN"}), 404

    res = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": isbn, "key": GOOGLEBOOKS_API_KEY})
    data = res.json()['books'][0]

    return jsonify({
        "isbn": book.isbn,
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "ratingsCount": data['ratingsCount'],
        "averageRating": data['averageRating']
    })


if __name__ == "__main__":
    app.run()