import os

import sendgrid
from flask import Flask, render_template, request, url_for
from pymongo import MongoClient
from sendgrid.helpers.mail import *

app = Flask(__name__)

sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))

client = MongoClient("mongodb://127.0.0.1")
db = client.forest_watcher_dev
temp2 = db.temp2


@app.route("/")
def home():
    return render_template(
        "home.html",
        register=url_for("register"),
        categories=["과학소설(SF)"],
        ns=range(1, 11),
    )


@app.route("/register", methods=["post"])
def register():

    # data = {
    #     "list_ids": [os.environ.get("SENDGRID_LIST")],  # 'forest-watcher' list
    #     "contacts": [
    #         {"email": request.form["email"]},
    #     ],
    # }
    # res = sg.client._("marketing/contacts").put(request_body=data)
    from_email = Email("forest@watcher.com")
    to_email = To(request.form["email"])
    subject = "10월의 숲을 보다"
    c = (
        db.temp2.find({"second_category": request.form["과학소설(SF)"]})
        .sort("salesPoint", -1)
        .limit(int(request.form["num"]))
    )
    content = HtmlContent(
        render_template("email.html", categories={"과학소설(SF)": list(c)})
    )
    mail = Mail(from_email, to_email, subject, content)
    res = sg.client.mail.send.post(request_body=mail.get())

    if res.status_code != 202:
        return "Error"

    return "Done"
