from dateutil.parser import parse

from app.models import Channel, UserChannel
from backend.database import db


# saves channels and relationship to Channel and UserChannel tables
def save_channels(channels, user_id):
    for channel in channels:
        channel_id = channel["snippet"]["resourceId"]["channelId"]

        # check if the channel already exists in the database
        existing_channel = Channel.query.filter_by(channel_id=channel_id).first()
        if existing_channel:
            new_channel = existing_channel
        else:
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
            )
            db.session.add(new_channel)

        # create a new UserChannel relationship for the current user and channel
        new_user_channel = UserChannel(
            user_id=user_id, channel_id=new_channel.channel_id, flag_is_visible=True
        )
        db.session.add(new_user_channel)
    db.session.commit()
