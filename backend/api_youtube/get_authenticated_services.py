import json
import os

import google_auth_oauthlib.flow
import googleapiclient.errors
from flask import url_for
from google.oauth2.credentials import Credentials

from app.auth.models import User
from backend.api_youtube.get_client_secret import get_client_secret

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


def flow(current_user):
    # Load client secrets from a file.
    client_secrets_file = get_client_secret()

    # Create an API client and save the credentials in the database.
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file,
        scopes,
        redirect_uri=url_for("main.index", _external=True),
    )
    credentials = flow.run_local_server(port=8081)

    # store the credentials in the database
    current_user.youtube_credentials = json.dumps(
        {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
        }
    )
    current_user.update_youtube_credentials(credentials)

    # close the popup window using JavaScript
    js = "window.opener.close(); window.close();"
    return f"<script>{js}</script>"


def get_authenticated_credentials(current_user):
    """
    Returns an authenticated Credentials object for the YouTube API.
    """

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # retrieve the current user's from the database
    current_user = User.query.get(current_user.user_id)

    # check if credentials already exist for the user.
    if current_user.youtube_credentials is not None:
        credentials_json = json.loads(current_user.youtube_credentials)
        credentials = Credentials.from_authorized_user_info(info=credentials_json)

        # check if the credentials are valid
        if credentials.valid:
            print("Credentials are valid")

        # if expired, get new credentials
        else:
            print("Credentials are expired")
            flow(current_user)

    # create new credentials
    else:
        print("No credentials found")
        flow(current_user)
