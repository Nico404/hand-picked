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
        return self.title
