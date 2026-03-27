from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "database", "tasks.db")


app = Flask(__name__)
app.secret_key = "supersecretkey"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL    
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)





def get_tasks(user_id):
    with sqlite3.connect(DATABASE) as conn:
        tasks = conn.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,)).fetchall()
    return tasks

def add_task(title, user_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("INSERT INTO tasks (title, user_id) VALUES (?, ?)", (title, user_id))


def delete_task(task_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

def toggle_task(task_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""
            UPDATE tasks
            SET completed = NOT completed
            WHERE id = ?
        """, (task_id,))


@app.route("/")
def landing():
    if "user_id" in session:
        return redirect("/home")

    return render_template("landing.html")

@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect("/")

    tasks = get_tasks(session["user_id"])
    return render_template("home.html", tasks=tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        hashed_password = generate_password_hash(password)

        with sqlite3.connect(DATABASE) as conn:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        with sqlite3.connect(DATABASE) as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            ).fetchone()

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            return redirect("/home")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect("/login")

    title = request.form.get("title")

    if title:
        add_task(title, session["user_id"])

    return redirect("/")

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    delete_task(task_id)
    return redirect("/")

@app.route("/update/<int:task_id>", methods=["POST"])
def update(task_id):
    toggle_task(task_id)
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
