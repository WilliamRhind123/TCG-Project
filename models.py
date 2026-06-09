from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    favourite_pokemon_id = db.Column(
        db.Integer,
        default=25
    )


class CollectionItem(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    pokemon_id = db.Column(
        db.Integer,
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        default=1
    )

    created_at = db.Column(
    db.DateTime,
    default=datetime.utcnow
    )   


class Notification(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    recipient_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    message = db.Column(db.String(300), nullable=False)

    image = db.Column(db.String(200), nullable=True)

    is_read = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TradeRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    requested_pokemon_id = db.Column(db.Integer, nullable=False)
    offered_pokemon_id = db.Column(db.Integer, nullable=False)

    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    sender = db.relationship("User", foreign_keys=[sender_id])
    receiver = db.relationship("User", foreign_keys=[receiver_id])

class FeedPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.String(500), nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship("User", backref="feed_posts")


class FeedLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("feed_post.id"),
        nullable=False
    )

    post = db.relationship("FeedPost", backref="likes")
    user = db.relationship("User")

class FeedComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.String(300), nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("feed_post.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship("User")
    post = db.relationship("FeedPost", backref="comments")