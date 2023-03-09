import json
import os

import google_auth_oauthlib
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from app.auth.forms import LoginForm, RegistrationForm
from app.auth.models import User, login_manager
from backend.api_youtube.get_channel_statistics import (
    update_channel_statistics_for_user,
)
from backend.api_youtube.get_client_secret import get_client_secret
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

        # Check for YouTube credentials
        credentials = None
        if user.youtube_credentials:
            credentials = Credentials.from_authorized_user_info(
                json.loads(user.youtube_credentials)
            )
        if not credentials or credentials.expired:
            if credentials and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                return redirect(url_for("auth.authorize"))

        # Call the function to update channel statistics for the user
        update_channel_statistics_for_user(user.user_id)

        return redirect(url_for("main.index"))
    return render_template("signin.html", title="Sign In", form=form)


# Load client secrets from a file.
client_secrets_file = get_client_secret()
# Define the required scopes
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

# define the authorization route
@auth_bp.route("/authorize")
def authorize():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secrets_file, scopes=scopes
    )

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = url_for("auth.oauth2callback", _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes="true",
    )

    # Store the state so the callback can verify the auth server response.
    session["state"] = state

    return redirect(authorization_url)


# define the callback route
@auth_bp.route("/oauth2callback")
def oauth2callback():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session["state"]

    if state is None or state != request.args.get("state"):
        return "Invalid state parameter", 400

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=scopes,
        state=state,
    )
    flow.redirect_uri = url_for("auth.oauth2callback", _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    flow.fetch_token(authorization_response=request.url)

    # Store credentials in the Database.
    credentials = flow.credentials
    # credentials = Credentials.from_authorized_user_info(
    #     {"token": credentials.token, "refresh_token": credentials.refresh_token}
    # )
    # # rework this
    current_user.update_youtube_credentials(credentials)
    return redirect(url_for("main.yourpicks"))


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


# prevent creating the same user twice TODO


@auth_bp.route("/signout")
@login_required
def signout():
    logout_user()
    return redirect(url_for("main.index"))
