from backend.database import db


class Channel(db.Model):
    channel_id = db.Column(db.String(32), primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    published_at = db.Column(db.DateTime)
    thumbnail_default_url = db.Column(db.String(255))
    thumbnail_medium_url = db.Column(db.String(255))
    thumbnail_high_url = db.Column(db.String(255))
    country = db.Column(db.String(2))
    view_count = db.Column(db.Integer)
    subscriber_count = db.Column(db.Integer)
    video_count = db.Column(db.Integer)

    def __repr__(self):
        return f"{self.title} - {self.channel_id} - {self.view_count} - {self.subscriber_count} - {self.video_count}"


class UserSubscription(db.Model):
    user_subscription_id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    username = db.Column(db.String(255))
    channel_id = db.Column(db.String(32), db.ForeignKey("channel.channel_id"))
    channel_title = db.Column(db.String(255))
    flag_is_visible = db.Column(db.Boolean, default=True)
    subscribed_at = db.Column(db.DateTime)
    thumbnail_default_url = db.Column(db.String(255))

    def __repr__(self):
        return f"{self.user_id} - {self.user_subscription_id}"


class Video(db.Model):
    video_id = db.Column(db.String(32), primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(5000))
    published_at = db.Column(db.DateTime)
    thumbnail_default_url = db.Column(db.String(255))
    view_count = db.Column(db.Integer)
    category_id = db.Column(db.Integer)
    channel_id = db.Column(db.String(32), db.ForeignKey("channel.channel_id"))

    def __repr__(self):
        return f"{self.title} - {self.video_id} - {self.view_count}"
