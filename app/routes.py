from flask import Blueprint, render_template

from backend.youtube_api.get_subscriptions import get_subscriptions

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html", title="Home")


# @main_bp.route("/yourpicks")
# def yourpicks():
#     subscription_list = get_subscriptions()
#     return render_template("yourpicks.html", title="Your Picks", data=subscription_list)
