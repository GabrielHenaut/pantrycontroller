import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, send_from_directory, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import csv
from datetime import date, datetime, timedelta

from helpers import login_required



# Configure application
app = Flask(__name__)

app.config["SECRET_KEY"] = "us=aAKSJDHG1*AJSF"
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# uri = os.getenv("DATABASE_URL")
# if uri.startswith("postgres://"):
#     uri = uri.replace("postgres://", "postgresql://")
# db = SQL(uri)

db = SQL("sqlite:///storage.db")

@app.route("/")
@login_required
def index():
    """Show storage on the main page"""
    # gets all the necessery information
    storage = db.execute("SELECT item, amount, unit, expiration, type FROM itens WHERE user_id=? ORDER BY expiration", session["user_id"])
    expiring = []

    for item in storage:
        item["item"] = item["item"].title()
        expiration = item["expiration"]
        today = datetime.today()
        day = timedelta(days=3)
        almost_expired = today + day
        almost_expired.date()
        print(type(almost_expired))
        if expiration < almost_expired:
            expiring.append(item)
        item["expiration"] = (f"{expiration.day}/{expiration.month}/{expiration.year}")

    if len(storage) < 1:
        flash("added itens will show here", "warning")
        return render_template("index.html", storage="", expiring="")
    else:
        if len(expiring) < 1:
            return render_template("index.html", storage=storage, expiring="")
        else:
            return render_template("index.html", storage=storage, expiring=expiring)


@app.route('/itens')
@login_required
def get_itens():
    list_itens = db.execute("SELECT item, amount, unit, expiration, type FROM itens WHERE user_id=? ORDER BY expiration", session["user_id"])
    for item in list_itens:
            item["item"] = item["item"].title()
    return jsonify(list_itens)


@app.route("/add_item", methods=["GET", "POST"])
@login_required
def add_item():
    """add itens to the pantry"""
    if request.method == "POST":

        # ensure a Name is provided
        if not request.form.get("name"):
            flash("must add the item's name", "warning")
            return redirect(request.url)

        # ensure a amount is provided
        if not request.form.get("amount"):
            flash("must add an amount", "warning")
            return redirect(request.url)

        # ensure a date is provided
        if not request.form.get("expiration"):
            flash("must add a expiration date", "warning")
            return redirect(request.url)

        if not request.form.get("type"):
            flash("Select a valid type", "warning")
            return redirect(request.url)

        # ensure amount is a number
        amount = request.form.get("amount")
        try:
            float(amount)
        except:
            flash("amount must be a number", "warning")
            return redirect(request.url)

        try:
            datetime.strptime(request.form.get("expiration"), "%Y-%m-%d")
        except:
            flash("must add a valid expiration date", "warning")
            return redirect(request.url)

        # checks if the user has that item already
        user = db.execute("SELECT item, amount FROM itens WHERE user_id=? AND item=? AND type=? AND unit=?", session["user_id"], request.form.get("name").upper(), request.form.get("type"), request.form.get("unit"))
        if len(user) < 1:
            db.execute("INSERT INTO itens (user_id ,item, amount, unit, expiration, type) VALUES(?, ?, ?, ?, ?, ?)", session["user_id"], request.form.get("name").upper(), request.form.get("amount"), request.form.get("unit"), request.form.get("expiration"), request.form.get("type"))
            flash("item added to pantry!", "success")
            return redirect(request.url)

        # update the item amount
        else:
            db.execute("UPDATE itens SET amount=? WHERE item=? AND user_id=?", (user[0]["amount"] + float(request.form.get("amount"))), request.form.get("name").upper(), session["user_id"])
            flash("item added to pantry!", "success")
            return redirect(request.url)


    else:
        # gets all the necessery information
        storage = db.execute("SELECT item, amount, unit, expiration, type FROM itens WHERE user_id=?", session["user_id"])
        for item in storage:
            item["item"] = item["item"].title()
            expiration = datetime.strptime(item["expiration"], "%Y-%m-%d")
            item["expiration"] = (f"{expiration.month}/{expiration.day}/{expiration.year}")
        if len(storage) < 1:
            return render_template("add_item.html", storage="")
        else:
            return render_template("add_item.html", storage=storage)




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must add a username", "danger")
            return redirect(request.url)

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must add a password", "danger")
            return redirect(request.url)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            flash("invalid username or password", "danger")
            return redirect(request.url)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")





@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            flash("must add a username", "danger")
            return redirect(request.url)

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must add a password", "danger")
            return redirect(request.url)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            flash("must add a password confirmation", "danger")
            return redirect(request.url)

        # checks if confirmation and password match
        elif request.form.get("confirmation") != request.form.get("password"):
            flash("password and confirmation must mach", "danger")
            return redirect(request.url)

        # checks if the username is already registerd
        if db.execute("SELECT username FROM users WHERE username = ?", request.form.get("username")):
            flash("username already being used", "danger")
            return redirect(request.url)

        # register the user in the database
        db.execute("INSERT INTO users (username, password) VALUES(?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))
        return render_template("login.html")

    else:
        return render_template("register.html")





@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    """remove itens from the pantry"""
    if request.method == "POST":

        # ensure a symbol is provided
        if not request.form.get("item"):
            flash("please provide a item", "danger")
            return redirect(request.url)

        # ensure a number of shares is provided
        if not request.form.get("amount"):
            flash("please provide an amount", "danger")
            return redirect(request.url)

        # ensure it is a valid symbol
        amount = request.form.get("amount")
        try:
            float(amount)
        except:
            flash("amount must be a number", "warning")
            return redirect(request.url)


        if float(amount) <= 0:
            flash("amount must be a positive number", "warning")
            return redirect(request.url)

        # checks if the user has enough of that item
        user = db.execute("SELECT item, amount FROM itens WHERE user_id=? AND item=?", session["user_id"], request.form.get("item").upper())
        if len(user) < 1 or float(request.form.get("amount")) > user[0]["amount"]:
            flash("you don't have enough of this item", "warning")
            return redirect(request.url)

        # execute the removal
        else:

            if (float(request.form.get("amount")) - user[0]["amount"]) == 0:
                db.execute("DELETE FROM itens WHERE user_id=? AND item=?", session["user_id"], request.form.get("item").upper())
            else:
                db.execute("UPDATE itens SET amount=? WHERE user_id=?", (user[0]["amount"] - float(request.form.get("amount"))), session["user_id"])

            flash("item removed from pantry!", "success")
            return redirect(request.url)

    else:
        return render_template("remove.html")



@app.route("/default", methods=["GET", "POST"])
@login_required
def default():
    """remove itens from the pantry"""
    if request.method == "POST":


        # ensure a Name is provided
        if not request.form.get("item"):
            flash("must add the item's name", "warning")
            return redirect(request.url)

        # ensure a amount is provided
        if not request.form.get("amount"):
            flash("must add an amount", "warning")
            return redirect(request.url)

        if not request.form.get("type"):
            flash("Select a valid type", "warning")
            return redirect(request.url)

        # ensure amount is a number
        amount = request.form.get("amount")
        try:
            float(amount)
        except:
            flash("amount must be a number", "warning")
            return redirect(request.url)

        user = db.execute("SELECT item, amount FROM default_pantry WHERE user_id=? AND item=? AND type=? AND unit=?", session["user_id"], request.form.get("item").upper(), request.form.get("type"), request.form.get("unit"))


        if request.form["action"] == "add":

            # checks if the user has that item already
            if len(user) < 1:
                db.execute("INSERT INTO default_pantry (user_id ,item, amount, unit, type) VALUES(?, ?, ?, ?, ?)", session["user_id"], request.form.get("item").upper(), request.form.get("amount"), request.form.get("unit"), request.form.get("type"))
                flash("item added to default pantry!", "success")
                return redirect(request.url)

            # update the item amount
            else:
                print(user)
                db.execute("UPDATE default_pantry SET amount=? WHERE item=? AND user_id=? AND type=? AND unit=?", (user[0]["amount"] + float(request.form.get("amount"))), request.form.get("item").upper(), session["user_id"], request.form.get("type"), request.form.get("unit"))
                flash("item added to default pantry!", "success")
                return redirect(request.url)

        elif request.form["action"] == "x":
            if len(user) < 1 or int(request.form.get("amount")) > user[0]["amount"]:
                flash("you don't have enough of this item", "warning")
                return redirect(request.url)

            # execute the removal
            else:

                if (int(request.form.get("amount")) - user[0]["amount"]) == 0:
                    db.execute("DELETE FROM default_pantry WHERE user_id=? AND item=? AND type=? AND unit=?", session["user_id"], request.form.get("item").upper(), request.form.get("type"), request.form.get("unit"))
                else:
                    db.execute("UPDATE default_pantry SET amount=? WHERE user_id=? AND item=? AND type=? AND unit=?", (user[0]["amount"] - float(request.form.get("amount"))), session["user_id"], request.form.get("item").upper(), request.form.get("type"), request.form.get("unit"))

                flash("item removed from pantry!", "success")
                return redirect(request.url)

    else:
        # gets all the necessery information
        storage = db.execute("SELECT item, amount, unit, type FROM default_pantry WHERE user_id=?", session["user_id"])
        if len(storage) < 1:
            flash("Itens added will be shown here!", "warning")
            return render_template("default.html", storage="")
        else:
            for item in storage:
                item["item"] = item["item"].title()
            return render_template("default.html", storage=storage)




@app.route("/remove_default", methods=["POST"])
@login_required
def remove_default():
    words = request.form.get("button").split()
    print(request.form.get("button"))
    db.execute("DELETE FROM default_pantry WHERE user_id=? AND item=? AND type=? AND unit=?", session["user_id"], words[0].upper(), words[2], words[1])
    return jsonify({'success':True}), 200, {'ContentType':'application/json'}


app.config["CLIENT_LIST"] = "/home/ubuntu/CS50x/final/pantry/static/client/"


@app.route("/shopping_list", methods=["GET"])
@login_required
def shopping_list():

    file = open("./static/client/Shopping List.csv", "w")
    writer = csv.writer(file)
    c_pantry = db.execute("SELECT item, amount, unit, type FROM itens WHERE user_id=?", session["user_id"])
    d_pantry = db.execute("SELECT item, amount, unit, type FROM default_pantry WHERE user_id=? ORDER BY type", session["user_id"])
    need_something = False
    full_list = []

    for d_product in d_pantry:
        s_list = []
        has = False
        for c_product in c_pantry:
            if c_product["item"] == d_product["item"]:
                has = True
                if c_product["amount"] < d_product["amount"]:
                    s_list.append(d_product["item"].title())
                    s_list.append(d_product["amount"] - c_product["amount"])
                    s_list.append(d_product["unit"])
                    s_list.append(d_product["type"])
                    need_something = True
                else:
                    continue
            else:
                continue
        if not has:
            for k, v in d_product.items():
                s_list.append(v)
                need_something = True
        if len(s_list) > 1:
            writer.writerow(s_list)
            full_list.append(s_list)
    file.close

    if request.method == "GET":
        if need_something:
            return render_template("shopping_list.html", full_list=full_list)
        else:
            return render_template("shopping_list.html", full_list="")


@app.route("/list_download", methods=["POST"])
@login_required
def list_download():
    return send_from_directory(app.config["CLIENT_LIST"], "Shopping List.csv", as_attachment=True)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    flash(f"{e.name}, code: {e.code}", "danger")
    return redirect(request.url)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
