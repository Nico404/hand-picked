from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.models import Channel, UserSubscription
from backend.api_youtube.get_channels import get_channels
from backend.api_youtube.get_subscriptions import get_subscriptions
from backend.database import db

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html", title="Home")


@main_bp.route("/yourpicks")
@login_required
def yourpicks():
    if current_user.is_authenticated and current_user.youtube_credentials:
        # Get all the UserSubscription objects that belong to the current user and are visible
        user_subscription_list = UserSubscription.query.filter_by(
            user_id=current_user.user_id,
            flag_is_visible=True,
        ).all()
        # Get their channel IDs
        channel_ids = [
            user_subscription.channel_id for user_subscription in user_subscription_list
        ]
        channel_ids_list = (
            Channel.query.filter(Channel.channel_id.in_(channel_ids))
            .order_by(Channel.subscriber_count.desc())
            .all()
        )

        # Get the Channel objects based on the channel_ids list
        channels = (
            Channel.query.filter(Channel.channel_id.in_(channel_ids))
            .order_by(Channel.subscriber_count.desc())
            .all()
        )

        # If the user has no UserSubscription yet, get them and the channels associated from YouTube
        if len(channel_ids_list) == 0:
            get_subscriptions(current_user)

        # If the channel_list is empty, call the get_channels function
        if not channels:
            channels = get_channels(channel_ids, current_user)

    return render_template("yourpicks.html", channels=channels)


@main_bp.route("/yourtimeline")
@login_required
def yourtimeline():
    if current_user.is_authenticated and current_user.youtube_credentials:
        # Get all the UserSubscription objects that belong to the current user and are visible
        user_subscription_list = (
            UserSubscription.query.filter_by(
                user_id=current_user.user_id,
                flag_is_visible=True,
            )
            .order_by(UserSubscription.subscribed_at.asc())
            .all()
        )

    return render_template("yourtimeline.html", subscriptions=user_subscription_list)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = "8"
    query = (
        db.session.query(
            Channel.country.label("country"), db.func.count().label("count")
        )
        .join(UserSubscription, UserSubscription.channel_id == Channel.channel_id)
        .filter(UserSubscription.user_id == user_id)
        .group_by(Channel.country)
        .filter(Channel.country != "ZZ")  # remove the "unknown" country
        .order_by(db.func.count().desc())
        .limit(5)
    )
    query_result = query.all()

    custom_data = []
    for row in query_result:
        custom_data.append({"label": row.country, "value": row.count})

    return render_template("dashboard.html", custom_data=custom_data)


@main_bp.route("/support")
@login_required
def support():
    return render_template("support.html", email=current_user.email)
