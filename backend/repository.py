import datetime

from sqlalchemy import func

from app.auth.models import User
from app.models import Channel, UserSubscription, Video, VideoCategory
from backend.database import db

# this file encapsulate the database queries and logic to be imported into the routes.py file


class UserRepository:
    def __init__(self):
        self.session = db.session

    def get_user(self, user_id):
        user = User.query.filter_by(user_id=user_id).first()
        return user

    def get_user_list(self, user_ids):
        users = User.query.filter(User.user_id.in_(user_ids)).all()
        return users


class ChannelRepository:
    def __init__(self):
        self.session = db.session

    def get_channel(self, channel_id):
        channel = Channel.query.filter_by(channel_id=channel_id).first()
        return channel

    def get_channel_list(self, channel_ids):
        channels = (
            Channel.query.filter(Channel.channel_id.in_(channel_ids))
            .order_by(Channel.subscriber_count.desc())
            .all()
        )
        return channels

    def get_channel_list_no_videos(self):
        channels = Channel.query.filter(
            Channel.flag_fetched_top_videos.is_(False)
        ).all()
        return channels


class UserSubscriptionRepository:
    def __init__(self):
        self.session = db.session
        self.channel_repository = ChannelRepository()
        self.video_category_repository = VideoCategoryRepository()

    def get_user_subscription_list(self, user_id):
        user_subscriptions = (
            UserSubscription.query.filter_by(user_id=user_id)
            .order_by(UserSubscription.subscribed_at.asc())
            .all()
        )
        return user_subscriptions

    def get_user_subscription_list_enriched(self, user_id):
        user_subscriptions = UserSubscription.query.filter_by(user_id=user_id).all()

        for user_subscription in user_subscriptions:
            channel_id = user_subscription.channel_id
            channel = self.channel_repository.get_channel(channel_id)

            if channel is not None:
                # fetch the video category list and find the matching category based on the channel's category_id
                video_categories = (
                    self.video_category_repository.get_video_category_list()
                )
                category_id = channel.calculated_category
                category = next(
                    (c for c in video_categories if c.category_id == category_id), None
                )

                user_subscription.view_count = channel.view_count
                user_subscription.video_count = channel.video_count
                user_subscription.subscriber_count = channel.subscriber_count
                user_subscription.calculated_category = (
                    category.title if category is not None else None
                )

        return user_subscriptions

    def get_oldest_user_subcription_date(self, user_id):
        user_subscription = (
            UserSubscription.query.filter_by(user_id=user_id)
            .order_by(UserSubscription.subscribed_at.asc())
            .first()
        )
        return user_subscription.subscribed_at


class VideoRepository:
    def __init__(self):
        self.session = db.session

    def get_video(self, video_id):
        video = Video.query.filter_by(video_id=video_id).first()
        return video

    def get_video_list(self, video_ids):
        videos = Video.query.filter(Video.video_id.in_(video_ids)).all()
        return videos


class VideoCategoryRepository:
    def __init__(self):
        self.session = db.session

    def get_video_category(self, video_category_id):
        video_category = VideoCategory.query.filter_by(
            video_category_id=video_category_id
        ).first()
        return video_category

    def get_video_category_list(self):
        video_categories = VideoCategory.query.all()
        return video_categories


class CustomQueryRepository:
    def __init__(self):
        self.session = db.session

    def diff_now_date(self, date):
        days_diff = (datetime.datetime.now() - date).days
        # calculate the number of years, months, and days
        years, days = divmod(days_diff, 365.25)
        months, days = divmod(days, 30.44)
        full_diff = f"{int(years)} years, {int(months)} months, and {int(days)} days"
        return full_diff

    def get_top_5_countries(self, user_id):
        top_countries = (
            db.session.query(
                Channel.country.label("country"), db.func.count().label("count")
            )
            .join(UserSubscription, UserSubscription.channel_id == Channel.channel_id)
            .filter(UserSubscription.user_id == user_id)
            .group_by(Channel.country)
            .filter(Channel.country != "ZZ")  # remove the "unknown" country
            .order_by(db.func.count().desc())
            .limit(5)
        )  # maybe     query_result = query.all()
        return top_countries

    def get_subscription_categorie_count(self, user_id):
        sub_query = (
            db.session.query(
                UserSubscription.channel_title.label("channel1"),
                Channel.title.label("channel2"),
                VideoCategory.title.label("category"),
            )
            .join(Channel, Channel.channel_id == UserSubscription.channel_id)
            .join(
                VideoCategory, Channel.calculated_category == VideoCategory.category_id
            )
            .filter(UserSubscription.user_id == user_id)
            .subquery()
        )
        query = (
            db.session.query(
                sub_query.c.category.label("category"),
                func.count().label("value"),
            )
            .group_by(sub_query.c.category)
            .order_by(func.count().desc())
        )
        result = query.all()
        labels = [row[0] for row in result]
        data = [row[1] for row in result]
        return labels, data
