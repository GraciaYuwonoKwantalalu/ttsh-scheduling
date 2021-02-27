from flask import Flask, redirect, url_for, render_template, request, session, flash

app = Flask(__name__)
app.secret_key = "hello"

@app.route('/')
@app.route('/login', methods=["POST", "GET"])
def login(): 
    if request.method == "POST": 
        session["user"] = request.form["name"]
        return redirect(url_for("timetable"))
    else: 
        if "user" in session:
            return redirect(url_for("timetable"))
        return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop("user", None)
    flash("You have been logged out!", "info")
    return redirect(url_for("login"))

@app.route('/timetable')
def timetable():    
    # LP 
    return render_template("timetable.html")

@app.route('/points')
def points():
    return render_template("points.html")

# @app.route('/admin')
# def admin():
#     return redirect(url_for("user", content=name, age=2, array_list=["billy","jim","timmy"]))




