from backend.api_youtube.get_youtube_object import get_youtube_object
from backend.db_utils import save_user_subscriptions


def get_subscriptions(current_user):
    """
    Retrieves the authenticated client object and fetches the subscriptions of the authorized user's channel.
    Returns the list of subscription items from a user.
    """

    print("getting subscriptions...")
    subscriptions = []
    next_page_token = None

    youtube = get_youtube_object(current_user)

    while True:
        try:
            # Fetch the subscriptions for the authorized user's channel.
            subscriptions_response = (
                youtube.subscriptions()
                .list(
                    part="snippet",
                    mine=True,
                    maxResults=50,
                    pageToken=next_page_token,
                )
                .execute()
            )

            # Extract the subscription items & next Token from the response.
            next_page_token = subscriptions_response.get("nextPageToken")
            subscriptions.extend(subscriptions_response["items"])

            if not next_page_token:
                break

        except Exception as error:
            print(f"An error occurred: {error}")
            return None
    save_user_subscriptions(subscriptions, current_user)
    return subscriptions
