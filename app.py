import os
import sqlite3

from flask import Flask, g, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = "dev-secret"
app.config["DATABASE"] = os.path.join(os.path.dirname(__file__), "e_voting.db")


HTML_TEMPLATE = """
<!doctype html>
<html>
  <head><title>{{ title }}</title></head>
  <body>
    <h1>{{ title }}</h1>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <ul>{% for msg in messages %}<li>{{ msg }}</li>{% endfor %}</ul>
      {% endif %}
    {% endwith %}
    {{ content|safe }}
  </body>
</html>
"""


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'voter'
        );

        CREATE TABLE IF NOT EXISTS elections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            created_by INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(created_by) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            election_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY(election_id) REFERENCES elections(id)
        );

        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            election_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            FOREIGN KEY(election_id) REFERENCES elections(id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(candidate_id) REFERENCES candidates(id),
            UNIQUE(election_id, user_id)
        );
        """
    )
    db.commit()


@app.before_request
def ensure_db():
    if not hasattr(g, "db"):
        get_db()


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template_string(
        HTML_TEMPLATE,
        title="E-Voting System",
        content="<p>Welcome to the e-voting platform.</p><p><a href='/register'>Register</a> | <a href='/login'>Login</a></p>",
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        confirm = request.form["confirm_password"]
        role = request.form.get("role", "voter")
        if not username or not password or password != confirm:
            return render_template_string(
                HTML_TEMPLATE, title="Register", content="<p>Registration failed. Please check your input.</p>"
            )
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            db.commit()
        except sqlite3.IntegrityError:
            return render_template_string(HTML_TEMPLATE, title="Register", content="<p>Username already exists.</p>")
        session["user_id"] = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()[0]
        session["role"] = role
        return redirect(url_for("dashboard"))
    return render_template_string(
        HTML_TEMPLATE,
        title="Register",
        content="""
        <form method='post'>
            <input name='username' placeholder='Username'><br>
            <input name='password' type='password' placeholder='Password'><br>
            <input name='confirm_password' type='password' placeholder='Confirm Password'><br>
            <select name='role'>
                <option value='voter'>Voter</option>
                <option value='admin'>Admin</option>
            </select><br>
            <button type='submit'>Register</button>
        </form>
    """,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        row = (
            get_db()
            .execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, password))
            .fetchone()
        )
        if row is None:
            return render_template_string(HTML_TEMPLATE, title="Login", content="<p>Invalid credentials.</p>")
        session["user_id"] = row[0]
        session["role"] = row[1]
        return redirect(url_for("dashboard"))
    return render_template_string(
        HTML_TEMPLATE,
        title="Login",
        content="""
        <form method='post'>
            <input name='username' placeholder='Username'><br>
            <input name='password' type='password' placeholder='Password'><br>
            <button type='submit'>Login</button>
        </form>
    """,
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    elections = db.execute("SELECT * FROM elections ORDER BY id DESC").fetchall()
    cards = []
    for election in elections:
        candidates = db.execute("SELECT * FROM candidates WHERE election_id = ?", (election["id"],)).fetchall()
        cards.append((election, candidates))
    content = "<p><a href='/logout'>Logout</a></p>"
    if session.get("role") == "admin":
        content += "<p><a href='/admin/elections'>Create election</a></p>"
    for election, candidates in cards:
        content += f"<h3>{election['title']}</h3><p>{election['description']}</p>"
        content += "<ul>"
        for candidate in candidates:
            content += f"<li>{candidate['name']}</li>"
        content += "</ul>"
        content += f"<p><a href='/vote/{election['id']}'>Vote</a> | <a href='/results/{election['id']}'>Results</a></p>"
    return render_template_string(HTML_TEMPLATE, title="Dashboard", content=content)


@app.route("/admin/elections", methods=["GET", "POST"])
def admin_elections():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form["title"].strip()
        description = request.form["description"].strip()
        candidates_input = request.form["candidates"].strip()
        if not title or not description or not candidates_input:
            return render_template_string(
                HTML_TEMPLATE, title="Create Election", content="<p>Please fill out all fields.</p>"
            )
        db = get_db()
        cur = db.execute(
            "INSERT INTO elections (title, description, created_by) VALUES (?, ?, ?)",
            (title, description, session["user_id"]),
        )
        election_id = cur.lastrowid
        for name in [line.strip() for line in candidates_input.splitlines() if line.strip()]:
            db.execute("INSERT INTO candidates (election_id, name) VALUES (?, ?)", (election_id, name))
        db.commit()
        return redirect(url_for("dashboard"))
    content = """
    <form method='post'>
        <input name='title' placeholder='Election title'><br>
        <textarea name='candidates' placeholder='One candidate per line'></textarea><br>
        <textarea name='description' placeholder='Description'></textarea><br>
        <button type='submit'>Create election</button>
    </form>
    """
    return render_template_string(HTML_TEMPLATE, title="Create Election", content=content)


@app.route("/vote/<int:election_id>", methods=["GET", "POST"])
def vote(election_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    election = db.execute("SELECT * FROM elections WHERE id = ?", (election_id,)).fetchone()
    if election is None:
        return render_template_string(HTML_TEMPLATE, title="Vote", content="<p>Election not found.</p>")
    if request.method == "POST":
        candidate_id = request.form.get("candidate_id")
        if not candidate_id:
            return render_template_string(HTML_TEMPLATE, title="Vote", content="<p>Please select a candidate.</p>")
        try:
            db.execute(
                "INSERT INTO votes (election_id, user_id, candidate_id) VALUES (?, ?, ?)",
                (election_id, session["user_id"], int(candidate_id)),
            )
            db.commit()
        except sqlite3.IntegrityError:
            return render_template_string(
                HTML_TEMPLATE, title="Vote", content="<p>You already voted in this election.</p>"
            )
        return render_template_string(
            HTML_TEMPLATE,
            title="Vote",
            content=f"<p>Your vote was recorded.</p><p><a href='/results/{election_id}'>View results</a></p>",
        )

    candidates = db.execute("SELECT * FROM candidates WHERE election_id = ?", (election_id,)).fetchall()
    options = "".join(
        f"<label><input type='radio' name='candidate_id' value='{candidate['id']}'>{candidate['name']}</label><br>"
        for candidate in candidates
    )
    content = f"<h2>{election['title']}</h2><p>{election['description']}</p>{options}<button type='submit'>Submit Vote</button>"
    return render_template_string(HTML_TEMPLATE, title="Vote", content=f"<form method='post'>{content}</form>")


@app.route("/results/<int:election_id>")
def results(election_id):
    db = get_db()
    election = db.execute("SELECT * FROM elections WHERE id = ?", (election_id,)).fetchone()
    if election is None:
        return render_template_string(HTML_TEMPLATE, title="Results", content="<p>Election not found.</p>")
    candidates = db.execute("SELECT * FROM candidates WHERE election_id = ?", (election_id,)).fetchall()
    lines = [f"<h3>{election['title']}</h3><p>{election['description']}</p>"]
    for candidate in candidates:
        vote_count = db.execute(
            "SELECT COUNT(*) FROM votes WHERE election_id = ? AND candidate_id = ?", (election_id, candidate["id"])
        ).fetchone()[0]
        lines.append(f"<p>{candidate['name']}: {vote_count} vote(s)</p>")
    return render_template_string(HTML_TEMPLATE, title="Results", content="".join(lines))


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
