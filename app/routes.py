from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.models import Channel, UserChannel
from backend.api_youtube.get_subscriptions import get_subscriptions
from backend.api_youtube.get_youtube_object import get_youtube_object

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html", title="Home")


@main_bp.route("/yourpicks")
@login_required
def yourpicks():
    if current_user.is_authenticated and current_user.youtube_credentials:
        # Get all the UserChannel objects that belong to the current user and are visible
        user_channel_list = UserChannel.query.filter_by(
            user_id=current_user.user_id,
            flag_is_visible=True,
        ).all()

        # Extract the channel IDs from the UserChannel objects and retrieve the corresponding channels
        channel_ids = [user_channel.channel_id for user_channel in user_channel_list]
        channel_list = (
            Channel.query.filter(Channel.channel_id.in_(channel_ids))
            .order_by(Channel.subscriber_count.desc())
            .all()
        )

        # If the user has no subscriptions yet, get them from YouTube
        if len(channel_list) == 0:
            get_subscriptions(current_user)

    return render_template("yourpicks.html", subscriptions=channel_list)


@main_bp.route("/yourtimeline")
@login_required
def yourtimeline():
    if current_user.is_authenticated and current_user.youtube_credentials:
        # Get all the UserChannel objects that belong to the current user and are visible
        user_channel_list = UserChannel.query.filter_by(
            user_id=current_user.user_id,
            flag_is_visible=True,
        ).all()

        # Extract the channel IDs from the UserChannel objects and retrieve the corresponding channels
        channel_ids = [user_channel.channel_id for user_channel in user_channel_list]
        channel_list = (
            Channel.query.filter(Channel.channel_id.in_(channel_ids))
            .order_by(Channel.published_at.desc())
            .all()
        )

    return render_template("yourtimeline.html", subscriptions=channel_list)


@main_bp.route("/support")
@login_required
def support():
    return render_template("support.html", email=current_user.email)
