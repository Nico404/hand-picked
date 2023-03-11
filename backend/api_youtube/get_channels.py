from backend.api_youtube.get_youtube_object import get_youtube_object
from backend.db_utils import save_channels


def get_channels(channel_ids, current_user):
    """
    Retrieves the authenticated client object and fetches the channel infos for the provided channel IDs.
    Returns the channels items from a channel.
    """
    print("getting channels...")
    channels = []

    youtube = get_youtube_object(current_user)

    for channel_id in channel_ids:
        try:
            # Fetch the channel.
            channel_response = (
                youtube.channels()
                .list(
                    part="snippet, statistics",
                    id=channel_id,
                )
                .execute()
            )

            # Extract the subscription items & next Token from the response. Both snippet and statistics
            channels.extend(channel_response["items"])

        except Exception as error:
            print(f"An error occurred: {error}")
            return None
    save_channels(channels)
    return channels
