import json

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.auth.models import User


def get_youtube_object(user):
    # Retrieve the user's YouTube credentials from the database
    user = User.query.filter_by(user_id=user.user_id).first()
    credentials_info = json.loads(user.youtube_credentials)
    credentials = Credentials.from_authorized_user_info(credentials_info)

    # Build the Youtube object using the credentials
    youtube = build("youtube", "v3", credentials=credentials)
    return youtube
