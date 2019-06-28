import os

from flask import Flask, session, render_template, request, redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from goodreads import goodreads

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
if not os.getenv("goodreadsAPI"):
    raise RuntimeError("goodreadsAPI is not set")

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

######### Book Review Submission ###########
@app.route("/book/<int:book_id>/submit_review", methods=["POST"])
def submit_review(book_id):
    # Check login
    if session.get("current_user") is None:
        return render_template("error.html", message="Must sign in to submit reviews!")
    user_id = db.execute("SELECT * FROM users WHERE username = :user", 
        {'user': session['current_user']}).fetchall()[0].id

    # Check user review history
    review_history = db.execute(
        "SELECT * FROM reviews WHERE book_id = :book_id AND user_id = :user_id",
        {'book_id': book_id, 'user_id': user_id}).fetchall()
    if len(review_history) == 1:
        return render_template("error.html", message='Already submitted a review before!')
    
    # Add new review
    rating = request.form.get("rating")
    comment = request.form.get("comment")
    db.execute("INSERT INTO reviews (book_id, user_id, rating, comment) VALUES (:book_id, :user_id, :rating, :comment)",
            {"book_id": book_id, "user_id": user_id, "rating": rating, "comment": comment})
    db.commit()
    return redirect(f"/book/{book_id}")


########### Book Page #############
@app.route("/book/<int:book_id>")
def book(book_id):
    # get book info from db: books
    book_info = db.execute("SELECT * FROM books WHERE id = :book_id", 
        {"book_id": book_id}).fetchall()
    if len(book_info) != 1:
        return render_template("error.html", message="Book not found!")
    # get book review from db: reviews
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id",
        {"book_id": book_id}).fetchall()
    # get Goodreads review from API
    res = goodreads(book_info[0].isbn)
    goodread_review = res.json()['books'][0] if res.status_code == 200 else {'notfound': '404'}
    return render_template("book.html", book_info=book_info[0], reviews=reviews, goodread_review=goodread_review)

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
    isbn_q = request.form.get("book_isbn").strip()
    title_q = request.form.get("book_title").strip()
    author_q = request.form.get("book_author").strip()
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
    # List reviewed books on personal page
    user_id = db.execute('SELECT id, username FROM users WHERE username = :username',
        {'username':username}).fetchall()[0].id
    my_books = db.execute(
        "SELECT reviews.book_id, reviews.user_id, reviews.rating, books.title, books.author FROM reviews JOIN books ON books.id = reviews.book_id WHERE reviews.user_id = :user_id",
        {'user_id': user_id}).fetchall()

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


######### API Endpoint #########
@app.route("/api/<isbn>")
def api(isbn):
    book = db.execute('SELECT * FROM books where isbn = :isbn',
        {'isbn':isbn}).fetchall()
    if len(book) == 0: 
        return jsonify({"error": "Invalid ISBN"}), 404
    book = book[0]
    review_stats = book_review_stats(book.id)
    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": review_stats[0],
        "average_score": review_stats[1]
    })

def book_review_stats(book_id):
    reviews = db.execute('SELECT * FROM reviews WHERE book_id = :book_id',
        {'book_id': book_id}).fetchall()
    if len(reviews) == 0:
        return None, None
    
    avg_score = sum([int(review.rating) for review in reviews]) / len(reviews)
    return len(reviews), avg_score