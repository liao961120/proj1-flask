import os

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET"])
def index():
    if session.get("current_user") is None:
        return render_template("index.html")
    else:
        username = session["current_user"]
        return redirect(f"/{username}")

########### Search Books based on isbn, title, author ##########

@app.route("/search", methods=['GET', 'POST'])
def search():
    # User authorize
    if session.get("current_user") is None:
        return render_template("error.html", message="You need to login to search books!")
    # GET
    if request.method == 'GET':
        query_result = []
        return render_template("search.html", query_result=query_result)
    # POST
    isbn_q = request.form.get("book_isbn")
    title_q = request.form.get("book_title")
    author_q = request.form.get("book_author")
    query = (f"%{isbn_q}%", f"%{title_q}%", f"%{author_q}%")
    ## Search db for books
    query_result = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn AND title LIKE :title AND author LIKE :author LIMIT 20",
        {"isbn": query[0], "title": query[1], "author": query[2]}).fetchall()
    
    query_str = []
    if len(query_result) == 0:
        query_result = ["Non"]
        for h, con in zip(['ISBN', 'Title', 'Author'], [ele.strip('%') for ele in query]):
            if con == "": con = '<empty>'
            query_str.append(f"{h}: {con}")
    return render_template("search.html", query_result=query_result, query=query_str)



############## User Account Management #################

@app.route("/login", methods=["GET", "POST"])
def login():
    # Get method
    if request.method == "GET":
        if session.get("current_user") is None:
            return render_template("login.html")
        else:
            return redirect("/")
    # Post method
    username = request.form.get("username")
    psswd = request.form.get("password")
    # Check username/password validity
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 0:
        return render_template("error.html", message=f"'{username}' not registered!")
    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", 
        {"username": username, "password": psswd}).rowcount == 0:
        return render_template("error.html", message="Wrong Password!")
    # Record current user
    session["current_user"] = username
    return redirect(f"/{username}")

@app.route("/logout", methods=["GET"])
def logout():
    if session.get("current_user") is None:
        return render_template("error.html", message="You are not logged in!")
    del session["current_user"]
    return redirect("/")


@app.route("/<username>")
def user(username):
    # Check page access authority
    if session.get("current_user") is None: 
        return render_template("error.html", message="You are not logged in!")
    if session["current_user"] != username: 
        return render_template("error.html", message=f"You don't have authority to read '{username}'")
    # List books on personal page
    my_books = db.execute("SELECT * FROM books LIMIT 10")
    return render_template("user.html", username=username.capitalize(), my_books=my_books)

@app.route("/register", methods=["GET", "POST"])
def register():
    # Show register form if navigated through link
    if request.method == 'GET':
        return render_template("register.html")
    # Get form information.
    username = request.form.get("username")
    psswd = request.form.get("password")
    # Check for dublicate username in db
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 1:
        return render_template("error.html", message=f"'{username}' already used!")
    # Add new account
    db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
            {"username": username, "password": psswd})
    db.commit()
    return render_template("success.html", message=f"New account '{username}' added.")
