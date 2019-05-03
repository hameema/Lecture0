import os

from flask import Flask, session,render_template,request,redirect,url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
#res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "KEY", "isbns": "9781632168146"})
#print(res.json())


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URI"):
    raise RuntimeError("DATABASE_URI is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URI"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods =["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username,"password": password}).rowcount == 1:
             return render_template ("search.html")
        return render_template("error.html", message="something wrong with the usernameor the password.")
    return render_template ("login.html")

@app.route("/sinup" , methods = ["GET","POST"] )
def sinup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username,"password": password}).rowcount == 1:
            return render_template("error.html", message="you are had sinedup befor.")
        db.execute("insert into users (username,password) values (:username,:password)",
                    {"username" :username ,"password" :password})
        db.commit()
        return redirect(url_for("login"))
    return render_template ("sinup.html")
@app.route("/search", methods=["POST"])
def search():
    isbn = request.form.get("isbn")
    title = request.form.get("title")
    author = request.form.get("author")
    books = db.execute("SELECT * FROM books WHERE isbn = :isbn OR title = :title OR author = :author",
                        {"isbn" : isbn , "title" : title, "author" : author})
    if books.rowcount == 0 :
        return render_template ("error.html",message = "there is no results")
    return render_template ("results.html", books = books)
