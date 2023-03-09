from sqlalchemy import text

from backend.api_youtube.get_youtube_object import get_youtube_object
from backend.database import db


def get_channel_statistics(current_user, channel_id):
    """Fetches the channel statistics for the provided channel ID."""
    # Get the authenticated client object
    youtube = get_youtube_object(current_user)

    try:
        # Fetch the channel statistics using the provided channel ID.
        channel_statistics_request = youtube.channels().list(
            part="statistics", id=channel_id, maxResults=1
        )
        channel_statistics_response = channel_statistics_request.execute()

        # Extract the required statistics from the response.
        view_count = int(
            channel_statistics_response["items"][0]["statistics"]["viewCount"]
        )
        subscriber_count = int(
            channel_statistics_response["items"][0]["statistics"]["subscriberCount"]
        )
        video_count = int(
            channel_statistics_response["items"][0]["statistics"]["videoCount"]
        )

        # Update the corresponding row in the channel table with the new statistics.
        update_query = f"""
            UPDATE channel
            SET view_count = {view_count}, subscriber_count = {subscriber_count}, video_count = {video_count}
            WHERE channel_id = '{channel_id}'
        """
        db.session.execute(update_query)
        db.session.commit()
    except Exception as error:
        print(
            f"An error occurred while fetching channel statistics for {channel_id}: {error}"
        )

    return channel_statistics_response


def update_channel_statistics_for_user(user_id):
    """Updates the channel statistics for all the channels that need it from that the user has subscribed to."""

    # Get a list of channel IDs that the user has subscribed to.
    channel_query = text("SELECT channel_id FROM User_Channel WHERE user_id = :user_id")
    channels = db.session.execute(channel_query, params={"user_id": user_id}).fetchall()

    # channels is a list of tuples with only the key ('UC0-swBG9Ne0Vh4OuoJ2bjbA',)
    for channel in channels:
        channel_id = channel[0]

        # Check if the required statistics are already present in the channel table.
        channel_check_statistics_query = text(
            "SELECT view_count, subscriber_count, video_count FROM channel WHERE channel_id = :channel_id"
        )
        channel_stats = db.session.execute(
            channel_check_statistics_query, params={"channel_id": channel_id}
        ).fetchone()
        if not channel_stats:
            # Fetch and store the missing statistics for the channel.
            get_channel_statistics(user_id, channel_id)
            print(user_id, channel_id)
