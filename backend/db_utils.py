from datetime import datetime

from app.models import Channel
from backend.database import db


def save_channels(channels):
    for channel in channels:
        new_channel = Channel(
            channel_id=channel["snippet"]["resourceId"]["channelId"],
            title=channel["snippet"]["title"],
            description=channel["snippet"]["description"],
            published_at=datetime.strptime(
                channel["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            thumbnail_default_url=channel["snippet"]["thumbnails"]["default"]["url"],
            thumbnail_medium_url=channel["snippet"]["thumbnails"]["medium"]["url"],
            thumbnail_high_url=channel["snippet"]["thumbnails"]["high"]["url"],
        )
        db.session.add(new_channel)
    db.session.commit()
