from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required

from app.models import UserSubscription
from backend.database import db
from backend.email_management.send_support import send_simple_message
from backend.repository import (
    CustomQueryRepository,
    UserSubscriptionRepository,
    VideoCategoryRepository,
)
from backend.service import ApiService

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html", title="Home")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_authenticated and current_user.youtube_credentials:
        # Initialize repositories
        customqueryrepository = CustomQueryRepository()
        videocategoryrepository = VideoCategoryRepository()

        # Get the top 5 countries of the user's subscriptions
        top_5_countries = customqueryrepository.get_top_5_countries(
            current_user.user_id
        )
        # Create a list of dictionaries containing the custom data
        custom_data = [
            {"label": row.country, "value": row.count} for row in top_5_countries
        ]

        # Fetch category reference table
        video_categories = videocategoryrepository.get_video_category_list()
        if len(video_categories) == 0:
            api_service = ApiService(current_user)
            api_service.save_video_categories(api_service.get_video_categories())

        # # Fetch channels in need of categorization and update the calculated category field
        # api_service = ApiService(current_user)

        # api_service.update_channel_calculated_category()

    return render_template("dashboard.html", custom_data=custom_data)


@main_bp.route("/yourpicks")
@login_required
def yourpicks():
    if current_user.is_authenticated and current_user.youtube_credentials:
        # Get all the UserSubscription objects that belong to the current user
        usersubscriptionrepository = UserSubscriptionRepository()
        user_subscriptions = (
            usersubscriptionrepository.get_user_subscription_list_enriched(
                current_user.user_id
            )
        )
        print(user_subscriptions[0])

        # If there are no UserSubscription objects, fetch the user's subscriptions and the channels from the API
        if len(user_subscriptions) == 0:
            api_service = ApiService(current_user)
            user_subscriptions = api_service.get_user_subscriptions()
            api_service.save_user_subscriptions(user_subscriptions)
            channel_ids = [
                user_subscription["snippet"]["resourceId"]["channelId"]
                for user_subscription in user_subscriptions
            ]
            api_service.save_channel(api_service.get_channel(channel_ids))

            user_subscriptions = (
                usersubscriptionrepository.get_user_subscription_list_enriched(
                    current_user.user_id
                )
            )
    return render_template("yourpicks.html", user_subscriptions=user_subscriptions)


@main_bp.route("/update_subscription_visibility", methods=["POST"])
def update_subscription_visibility():
    print("aaa")
    user_subscription_id = request.form["user_subscription_id"]
    visibility = request.form["visibility"]
    visibility = True if visibility == "true" else False

    print(user_subscription_id, visibility)
    user_subscription = UserSubscription.query.filter_by(
        user_subscription_id=user_subscription_id
    ).first()

    if user_subscription:
        user_subscription.flag_is_visible = visibility
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})


@main_bp.route("/yourtimeline")
@login_required
def yourtimeline():
    if current_user.is_authenticated and current_user.youtube_credentials:
        # Initialize repositories
        usersubscriptionrepository = UserSubscriptionRepository()
        customqueryrepository = CustomQueryRepository()

        # Get all the UserSubscription objects that belong to the current user
        user_subscriptions = usersubscriptionrepository.get_user_subscription_list(
            current_user.user_id
        )
        # Get the first subscription's and calculate the difference between the current time and the subscription's time
        diff_time = customqueryrepository.diff_now_date(
            usersubscriptionrepository.get_oldest_user_subcription_date(
                current_user.user_id
            )
        )
    return render_template(
        "yourtimeline.html",
        user_subscriptions=user_subscriptions,
        diff_time=diff_time,
    )


@main_bp.route("/support")
@login_required
def support():
    return render_template("support.html", email=current_user.email)


@main_bp.route("/send_message", methods=["GET", "POST"])
def send_message():
    subject = request.form["subject"]
    email = request.form["email"]
    message = request.form["message"]

    if request.method == "POST":
        response = send_simple_message(subject, email, message)
        if response.status_code == 200:
            flash("Message sent successfully!", "success")
        else:
            flash("Error sending message.", "error")
        return render_template("support.html")
    return render_template("support.html")
