import json

import requests
from dateutil.parser import parse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.auth.models import User
from app.models import Channel, UserSubscription, Video, VideoCategory
from app.repository import ChannelRepository, VideoRepository
from backend.database import db


class ApiService:
    """This class encapsulates all Google API interactions"""

    def __init__(self, current_user):
        self.current_user = current_user
        self.youtube = self.get_youtube_object()

    def get_youtube_object(self):
        # Retrieve the user's YouTube credentials from the database
        user = User.query.filter_by(user_id=self.current_user.user_id).first()
        credentials_info = json.loads(user.youtube_credentials)
        credentials = Credentials.from_authorized_user_info(credentials_info)

        # Build the Youtube object using the credentials
        youtube = build("youtube", "v3", credentials=credentials)
        return youtube

    def fetch_items(self, request_func, part, **kwargs):
        """
        Retrieves items from the YouTube API using the provided request function and parameters.
        Returns the list of items from the API response.
        """
        items = []
        next_page_token = None

        while True:
            try:
                response = request_func(
                    part=part, pageToken=next_page_token, **kwargs
                ).execute()
                items.extend(response["items"])
                next_page_token = response.get("nextPageToken")

                if not next_page_token:
                    break

            except Exception as error:
                print(f"An error occurred: {error}")
                return None

        return items

    def get_channel(self, channel_ids):
        """
        Fetches the channel infos for the provided channel IDs.
        Returns the channels items from a channel.
        """
        print("getting channels...")
        channels = []

        for channel_id in channel_ids:
            try:
                # Fetch the channel.
                channel_response = (
                    self.youtube.channels()
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
        return channels

    def save_channel(self, channels):
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
                    thumbnail_medium_url=channel["snippet"]["thumbnails"]["medium"][
                        "url"
                    ],
                    thumbnail_high_url=channel["snippet"]["thumbnails"]["high"]["url"],
                    country=country,
                    view_count=channel["statistics"]["viewCount"],
                    subscriber_count=channel["statistics"]["subscriberCount"],
                    video_count=channel["statistics"]["videoCount"],
                )
                db.session.add(new_channel)
        db.session.commit()

    def get_user_subscriptions(self):
        """
        Retrieves the authenticated client object and fetches the subscriptions of the authorized user's channel.
        Returns the list of subscription items from a user.
        """

        print("getting subscriptions...")
        subscriptions = []
        next_page_token = None

        while True:
            try:
                # Fetch the subscriptions for the authorized user's channel.
                subscriptions_response = (
                    self.youtube.subscriptions()
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
        return subscriptions

    def save_user_subscriptions(self, subscriptions):  # UCC9mlCpyisiIpp9YA9xV-QA
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
                    user_id=self.current_user.user_id,
                    username=self.current_user.username,
                    channel_id=subscription["snippet"]["resourceId"]["channelId"],
                    channel_title=subscription["snippet"]["title"],
                    flag_is_visible=True,
                    subscribed_at=parse(subscription["snippet"]["publishedAt"]),
                    thumbnail_default_url=subscription["snippet"]["thumbnails"][
                        "default"
                    ]["url"],
                )
            db.session.add(new_user_subscription)
        db.session.commit()

    def get_top_videos_from_channel(self, channel_id):
        """Retrieves the authenticated client object and fetches the top videos for the provided channel ID."""
        print("getting top videos of...", channel_id)
        videos = []
        try:
            # Call the search.list method to retrieve the top 10 rated videos
            search_response = (
                self.youtube.search()
                .list(
                    channelId=channel_id,
                    part="id,snippet",
                    order="rating",
                    type="video",
                    maxResults=10,
                )
                .execute()
            )
            videos.extend(search_response["items"])

        except Exception as error:
            print(f"An error occurred: {error}")
            return None
        return videos

    def save_videos(self, videos):
        print("saving top10 videos...")
        for video in videos:
            # check if the video already exists in the database
            video_id = video["id"]["videoId"]
            existing_video = Video.query.filter_by(video_id=video_id).first()
            if existing_video:
                new_user_subscription = existing_video
            else:
                # create a new UserSubscription object for the current user and channel
                new_user_subscription = UserSubscription(
                    video_id=video["id"]["videoId"],
                    title=video["snippet"]["title"],
                    view_count=video["snippet"]["viewCount"],
                    category_id=video["snippet"]["categoryId"],
                    link=f"https://www.youtube.com/watch?v={video_id}",
                    channel_id=video["snippet"]["channelId"],
                )
            db.session.add(new_user_subscription)
        # Update the fetched_top_videos flag for the channel
        channel = Channel.query.filter_by(
            channel_id=new_user_subscription.channel_id
        ).first()
        channel.fetched_top_videos = True  # this set True should be in repository
        db.session.commit()

    def get_video_categories(self):
        """Retrieves the authenticated client object and fetches the video categories."""
        print("getting video categories...")
        categories = []
        try:
            # Call the videoCategory method to retrieve the top 10 rated videos
            search_response = (
                self.youtube.videoCategories()
                .list(part="snippet", regionCode="US")
                .execute()
            )
            categories.extend(search_response["items"])

        except Exception as error:
            print(f"An error occurred: {error}")
            return None
        return categories

    def save_video_categories(self, categories):
        print("saving video categories...")
        for category in categories:
            # check if the video category already exists in the database
            category_id = category["id"]
            existing_category = VideoCategory.query.filter_by(
                category_id=category_id
            ).first()
            if existing_category:
                new_category = existing_category
            else:
                # create a new Category object for the current user and channel
                new_category = VideoCategory(
                    category_id=category_id,
                    title=category["snippet"]["title"],
                )
            db.session.add(new_category)
        db.session.commit()

    def update_channel_calculated_category(self):
        # First, get channels with no videos fetched
        videorepository = VideoRepository()
        channelrepository = ChannelRepository()
        channels = channelrepository.get_channel_list_no_videos()

        for channel in channels:
            # Get all videos for the current channel
            videos = videorepository.get_videos_by_channel_id(channel.id)

            # Count the occurrences of each category_id and find the most common one
            category_count = {}
            max_count = 0
            max_category_id = None
            for video in videos:
                category_id = video.category_id
                if category_id in category_count:
                    category_count[category_id] += 1
                else:
                    category_count[category_id] = 1
                if category_count[category_id] > max_count:
                    max_count = category_count[category_id]
                    max_category_id = category_id

            # Update the channel's calculated_category field with the most common category_id
            if max_category_id is not None:
                channel.calculated_category = max_category_id
                self.save(channel)
