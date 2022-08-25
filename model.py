import dateutil.parser
import babel
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from forms import *



app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)




class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(), nullable=True)
    website_link = db.Column(db.String(500), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    upcoming_shows = db.Column(db.String(), nullable=True)
    past_shows = db.Column(db.String(), nullable=True)
    past_shows_count = db.Column(db.Integer, nullable=True)
    upcoming_shows_count = db.Column(db.Integer, nullable=True)
    show = db.relationship('Show', backref='venues', lazy='joined', cascade="all,delete")


    def __repr__(self):
        return '<Venue {}>'.format(self.name)


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    # artist_image_link = db.Column(db.String(), nullable=True)
    # venue_name = db.Column(db.String(), nullable=True)
   # artist_name = db.Column(db.String(), nullable=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
                           

    def __repr__(self):
        return '<Show {}{}>'.format(self.artist_id, self.venue_id)

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120), )
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(), nullable=True)
    upcoming_shows = db.Column(db.String(), nullable=True)
    past_shows_count = db.Column(db.Integer, nullable=True)
    upcoming_shows_count = db.Column(db.Integer, nullable=True)
    show = db.relationship('Show', backref='artists', lazy='joined', cascade="all,delete")


    def __repr__(self):
        return '<Artist {}>'.format(self.name)








