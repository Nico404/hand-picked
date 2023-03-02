from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth.forms import LoginForm, RegistrationForm
from app.auth.models import User, login_manager
from backend.database import db

auth_bp = Blueprint("auth", __name__, url_prefix="")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route("/signin", methods=["GET", "POST"])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password. Try again...", "error")
            return redirect(url_for("auth.signin"))
        login_user(user)
        return redirect(url_for("main.index"))
    return render_template("signin.html", title="Sign In", form=form)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!", "success")
        return redirect(url_for("auth.signup"))
    else:
        if request.method == "POST":
            flash("Oh No! Form is not valid", "error")
    return render_template("signup.html", title="Sign Up", form=form)


@auth_bp.route("/signout")
@login_required
def signout():
    logout_user()
    return redirect(url_for("main.index"))
