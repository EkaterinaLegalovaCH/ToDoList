from flask import Flask, render_template, request, redirect
import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "database", "tasks.db")


app = Flask(__name__)

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER DEFAULT 0
            )
        """)


def get_tasks():
    with sqlite3.connect(DATABASE) as conn:
        tasks = conn.execute("SELECT * FROM tasks").fetchall()
    return tasks

def add_task(title):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))


def delete_task(task_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))



@app.route("/")
def index():
    tasks = get_tasks()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")

    if title:
        add_task(title)

    return redirect("/")

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    delete_task(task_id)
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
