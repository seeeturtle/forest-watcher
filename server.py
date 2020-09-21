import os

import sendgrid
from flask import Flask, render_template, request, url_for
from sendgrid.helpers.mail import *

app = Flask(__name__)

sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))


@app.route("/")
def home():
    return render_template("home.html", register=url_for("register"))


@app.route("/register", methods=["post"])
def register():

    data = {
        "list_ids": ["***REMOVED***"],  # 'forest-watcher' list
        "contacts": [
            {"email": request.form["email"]},
        ],
    }
    res = sg.client._("marketing/contacts").put(request_body=data)

    if res.status_code != 202:
        return "Error"

    return "Done"
