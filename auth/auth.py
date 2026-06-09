from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, redirect, url_for, request, flash

from models import db, User


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
    template_folder="templates"
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            flash("Logged in successfully!", "success")

            return redirect(url_for("index"))

        flash("Invalid username or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":

        username = request.form["username"].strip()

        password = request.form["password"]

        favourite_pokemon_id = int(
            request.form.get("favourite_pokemon_id", 25)
        )

        if not username:

            flash("Username cannot be empty.", "danger")

            return render_template("auth/register.html")

        if len(password) < 4:

            flash("Password must be at least 4 characters.", "danger")

            return render_template("auth/register.html")

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:

            flash("Username already taken.", "danger")

            return render_template("auth/register.html")

        new_user = User(

            username=username,

            password=generate_password_hash(password),

            favourite_pokemon_id=favourite_pokemon_id
        )

        db.session.add(new_user)

        db.session.commit()

        flash(
            "Account created successfully. Please log in.",
            "success"
        )

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash("You have been logged out.", "info")

    return redirect(url_for("auth.login"))