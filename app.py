import os

from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from cs50 import SQL

app = Flask(__name__)

app.secret_key = generate_password_hash("run&go")
app.config['SESSION_TYPE'] = 'filesystem'



db = SQL("sqlite:///notes.db")

@app.route('/', methods=["GET", "POST"])
def index():
      db = SQL("sqlite:///notes.db")
      if request.method == 'POST':
           if request.form['type'] == 'add-note':
                  if not request.form['note-text']:
                        flash("you cant add empty note", 'warning')
                        return redirect("#")
                  note = request.form['note-text']

                  db.execute("INSERT INTO notes (user_id, note) VALUES(?, ?)", session['user_id'], note)
                  return redirect("/")
           if request.form['type'] == 'delete-note':
                  db.execute("DELETE FROM notes where note = ?", request.form['note-data'])
                  return redirect("#")
      else:
            if 'user_id' not in session:
                  return redirect("/login")

            data = db.execute("select * from notes where user_id = ?", session['user_id'])
            rows = []
            i = 0
            for row in data:
                  i += 1
                  info = {
                  'num' : i,
                  'note' : row['note']
                  }
                  rows.append(info)
            return render_template("index.html", rows=rows, i=0)

@app.route('/login', methods=["GET", "POST"])
def login():

   db = SQL("sqlite:///notes.db")
   if request.method == "POST":
      session.clear()



      if not request.form['username']:
            flash("You must provide a name", 'warning')
            return redirect("#")

      elif not request.form['password']:
            flash("You must provide a password", 'warning')
            return redirect("#")
      rows = db.execute("SELECT * FROM users WHERE username = ?", request.form["username"])

      if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password", 'warning')
            return redirect("#")

      session['user_id'] = rows[0]["id"]
      session['username'] = rows[0]['username']

      return redirect('/')
   else:
      return render_template("login.html")

@app.route("/register", methods = ["GET", "POST"])
def register():
      db = SQL("sqlite:///notes.db")
      if request.method == "POST":


            if not request.form['username']:
                  flash("You must provide a name", 'warning')
                  return redirect("#")
            if len(db.execute("SELECT * FROM users where username = ?", request.form['username'])) == 1:
                  flash("username is not available", 'warning')
                  return redirect("#")
            if not request.form['password']:
                  flash("You must provide a password", 'warning')
                  return redirect("#")
            if request.form['password'] != request.form['password_confirm']:
                  flash("passwords dont match", 'warning')
                  return redirect("#")

            username = request.form['username']
            password = request.form['password']

            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password))
            user_id = db.execute("SELECT id,username FROM users WHERE username = ?", request.form ['username'])
            session["user_id"] = user_id[0]['id']
            session['username'] =  user_id[0]['username']

            return redirect("/")

      else:
            return render_template("register.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

if __name__ == '__main__':
      app.run(debug=True)
