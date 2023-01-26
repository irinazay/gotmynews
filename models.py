import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class UserTopic(db.Model):
    """Mapping users to topics."""
   
    __tablename__ = "users_topics"
   
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    )
    
    topic_id = db.Column(
    db.Integer,
    db.ForeignKey('topics.id'),
    primary_key=True
    )

    isSelected=db.Column(db.Boolean)

class TopicSubreddit(db.Model):
    """Mapping topics to subreddits."""
    

    __tablename__ = "topics_subreddits"

    topic_id = db.Column(
        db.Integer,
        db.ForeignKey('topics.id'),
        primary_key=True
    )

    subreddit_id = db.Column(
        db.Integer,
        db.ForeignKey('subreddits.id'),
        primary_key=True
    )


class Topic(db.Model):
    """Available topics."""

    __tablename__ = "topics"

    id = db.Column(db.Integer, 
    primary_key=True)

    name = db.Column(db.Text)



class Subreddit(db.Model):
    """Available subreddits"""

    __tablename__ = 'subreddits'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    url = db.Column(
        db.Text, 
        unique=True
    )

    topics = db.relationship(
        'Topic',
        secondary="topics_subreddits",
        cascade="all,delete",
        backref="subreddits",
    )

class Post(db.Model):
    """An individual daily posts."""

    __tablename__ = "posts"

    id = db.Column(db.Integer,
    primary_key=True
    )

    title = db.Column(db.Text)

    url = db.Column(db.Text)

    date = db.Column(
        db.DateTime,
        default=datetime.datetime.now)

    subreddit_id = db.Column(db.Integer, db.ForeignKey('subreddits.id'))

    subreddits = db.relationship(
        "Subreddit",
        backref="posts", 
       
    )



class User(db.Model):
    """User in the system."""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    first_name = db.Column(
        db.String(100), 
        nullable=False, 
        unique=False
    )

    last_name = db.Column(
        db.String(100), 
        nullable=False, 
        unique=False
    )

    email = db.Column(
        db.String(80),
        nullable=False,
        unique=True,
    )
    
    password_hash = db.Column(
        db.String(200),
        nullable=False,
        unique=False,
        primary_key=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.datetime.now
    )

    modified_at = db.Column(
        db.DateTime,
        default=datetime.datetime.now
    )

    topics = db.relationship(
        'Topic',
        secondary="users_topics",
        backref="users",
    )

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
     
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)


def connect_db(app):
    """Connect database to Flask app."""

    db.app = app
    db.init_app(app)

