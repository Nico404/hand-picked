from backend.database import db


class Channel(db.Model):
    channel_id = db.Column(db.String(32), primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    published_at = db.Column(db.DateTime)
    thumbnail_default_url = db.Column(db.String(255))
    thumbnail_medium_url = db.Column(db.String(255))
    thumbnail_high_url = db.Column(db.String(255))
    country = db.Column(db.String(2), nullable=True)
    view_count = db.Column(db.Integer, nullable=True)
    subscriber_count = db.Column(db.Integer, nullable=True)
    video_count = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return self.title


class UserChannel(db.Model):
    user_channel_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    channel_id = db.Column(db.String(32), db.ForeignKey("channel.channel_id"))
    flag_is_visible = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"{self.user_id} - {self.channel_id}"
