from dateutil.parser import parse

from app.models import Channel, UserSubscription
from backend.database import db


# saves channels and relationship to Channel and UserChannel tables
def save_channels(channels):
    print("saving channels...", channels)
    for channel in channels:
        channel_id = channel["id"]
        # check if the channel already exists in the database
        existing_channel = Channel.query.filter_by(channel_id=channel_id).first()
        if existing_channel:
            new_channel = existing_channel
        else:
            if "country" in channel["snippet"]:
                country = channel["snippet"]["country"]
            else:
                country = "ZZ"

            new_channel = Channel(
                channel_id=channel_id,
                title=channel["snippet"]["title"],
                description=channel["snippet"]["description"],
                published_at=parse(channel["snippet"]["publishedAt"]),
                thumbnail_default_url=channel["snippet"]["thumbnails"]["default"][
                    "url"
                ],
                thumbnail_medium_url=channel["snippet"]["thumbnails"]["medium"]["url"],
                thumbnail_high_url=channel["snippet"]["thumbnails"]["high"]["url"],
                country=country,
                view_count=channel["statistics"]["viewCount"],
                subscriber_count=channel["statistics"]["subscriberCount"],
                video_count=channel["statistics"]["videoCount"],
            )
            db.session.add(new_channel)
    db.session.commit()


def save_user_subscriptions(subscriptions, current_user):  # UCC9mlCpyisiIpp9YA9xV-QA
    print("saving subscriptions...")
    for subscription in subscriptions:
        # check if the UserSubscription relationship already exists in the database
        user_subscription_id = subscription["id"]
        existing_user_subscription = UserSubscription.query.filter_by(
            user_subscription_id=user_subscription_id
        ).first()
        if existing_user_subscription:
            new_user_subscription = existing_user_subscription
        else:
            # create a new UserSubscription object for the current user and channel
            new_user_subscription = UserSubscription(
                user_subscription_id=user_subscription_id,
                user_id=current_user.user_id,
                username=current_user.username,
                channel_id=subscription["snippet"]["resourceId"]["channelId"],
                channel_title=subscription["snippet"]["title"],
                flag_is_visible=True,
                subscribed_at=parse(subscription["snippet"]["publishedAt"]),
                thumbnail_default_url=subscription["snippet"]["thumbnails"]["default"][
                    "url"
                ],
            )
        db.session.add(new_user_subscription)
    db.session.commit()
