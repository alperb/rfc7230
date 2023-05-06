import os
from flask import Flask, make_response, render_template, request

app = Flask(__name__)

cookies = {}

@app.route("/", methods=["GET"])
def index():
    c = request.cookies.get("cs408_cookie")
    if c is None:
        res = make_response(render_template("index.html"))
        return res
    else:
        if c in cookies:
            return render_template("flag.html", user="albertlevi")
        else:
            return render_template("index.html")

@app.route("/login", methods=["GET"])
def loginview():
    res = make_response(render_template("login.html"))
    return res

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username == "albertlevi" and password == "galatasarayftw":
        res = make_response("Logged in!")
        res.status_code = 302
        res.headers["Location"] = "/"
        random_value = os.urandom(16).hex()
        res.set_cookie("cs408_cookie", random_value)
        cookies[random_value] = True
        return res
    else:
        res = make_response("Bad request")
        res.status_code = 400
        return res



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
