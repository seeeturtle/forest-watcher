from flask import Flask, render_template, request, url_for

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html", register=url_for("register"))


@app.route("/register", methods=["post"])
def register():
    return request.form["email"]
