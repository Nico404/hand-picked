from flask import Blueprint, render_template
from flask_login import current_user

from app.models import Channel
from backend.api_youtube.get_subscriptions import get_subscriptions

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html", title="Home")


@main_bp.route("/yourpicks")
def yourpicks():
    # subscriptions = []
    if current_user.is_authenticated and current_user.youtube_credentials:
        # subscription_list = get_subscriptions(current_user)
        subscription_list = Channel.query.all()
        if len(subscription_list) == 0:
            get_subscriptions(current_user)
    return render_template("yourpicks.html", subscriptions=subscription_list)
