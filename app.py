#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.mime import image
from email.policy import default
import json
from unicodedata import name
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request,
    Response,
    flash,
    redirect,
    url_for,
    jsonify,
    abort
    )
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_wtf.csrf import CSRFProtect
from forms import *
from datetime import datetime
import sys
from model import db,Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
csrf = CSRFProtect(app)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
#db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    venues = db.session.query(Venue.city, Venue.state).distinct(
        Venue.city, Venue.state)

    for venue in venues:
        venues_in_city = db.session.query(Venue.id, Venue.name).filter(Venue.city == venue[0]).filter(Venue.state == venue[1])
                                                                       
        data.append({
            "city": venue[0],
            "state": venue[1],
            "venues": venues_in_city
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search = request.form.get('search_term', '')
    result = Venue.query.filter(Venue.name.ilike("%" + search + "%")).all()
    response = {
        "count": len(result),
        "data": result} 
  
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).one() # Single Item
    shows = Show.query.filter_by(venue_id=venue_id).all() # List

    if venue is None and shows is None:
        return {}

  
    upcoming_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
    upcoming_shows = []
    past_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
    past_shows = []
    

    data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website_link": venue.website_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link
        }

    for show in shows:
        print(show)
        artist_data = Artist.query.filter_by(id=show.artist_id).one() # Single Item
    
        artist_information = {
            "artist_id": artist_data.id or "Id Not Found",
           "artist_name": artist_data.name or "Name Does Not Exist",
           "artist_image_link": artist_data.image_link or "Sina Link",
            "start_time": format_datetime(str(show.start_time))
        }

        if show.start_time > datetime.now():
            upcoming_shows.append(artist_information)
        else:
            past_shows.append(artist_information)


        
    extended_data = {"past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)}
    data.update(extended_data)

    

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form,meta={'csrf': False})
    try:
        if form.validate():
            v = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                genres=form.genres.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                seeking_talent=form.seeking_talent.data,

                facebook_link=form.facebook_link.data,
                seeking_description=form.seeking_description.data,
                website_link=form.website_link.data

            )
            db.session.add(v)
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        else:
            message = []
            for field, err in form.errors.items():
                message.append(field + ' ' + '|'.join(err))
            flash('Errors ' + str(message))
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + v.name + ' could not be listed.')
              
    finally:
        db.session.close()

    return render_template('pages/home.html', )


@app.route('/venues/<venue_id>/delete', methods=["POST", "GET"])
def delete_venue(venue_id):
    try:
        venue_object = db.session.query(Venue).filter(Venue.id == int(venue_id)).first()
        db.session.delete(venue_object)
        db.session.commit()

        flash('Venue has been removed!')
        
    except Exception as e:
        print(e)
        db.session.rollback()
        print(sys.exc_info())
        flash('Venue could not be removed!')
    finally:
        db.session.close()
   
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data= Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
     search = request.form.get('search_term', '')
     s = Artist.query.filter(Artist.name.ilike("%" + search + "%")).all()
     response = {
        "count": len(s),
        "data": s
        }
 
     return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    artist = Artist.query.filter_by(id=artist_id).one() #Lists a single Item
    shows = Show.query.filter_by(artist_id=artist_id).all() #Lists the shows a single artist has
    
    if artist is None and shows is None:
        return {}
    upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
    upcoming_shows = []
    past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
    past_shows = []
    
   
     # data=None

    data={
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website_link": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description":artist.seeking_description,
        "image_link": artist.image_link,
    }

    
    for show in shows:
        venue_data = Venue.query.filter_by(id=show.venue_id).one()
        venue_information = {
           "venue_id": venue_data.id or "Id Not Found",
           "venue_name": venue_data.name or "Name Does Not Exist",
           "venue_image_link": venue_data.image_link or "Image Link does not exist",
           "start_time": format_datetime(str(show.start_time))
         }
        if show.start_time > datetime.now():
              upcoming_shows.append(venue_information)
        else:
            past_shows.append(venue_information)

    extended_data = {
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    data.update(extended_data)

   

    
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    r = Artist.query.filter_by(id=artist_id).one()
    r = db.session.merge(r)
    form = ArtistForm(request.form)
    if not form.validate():
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(err)
        return render_template('forms/edit_artist.html', form=form, artist=edit_artist)
    else:
        try:
            r.name = form.name.data
            r.city = form.city.data
            r.state = form.state.data
            r.phone = form.phone.data
            r.genres = form.genres.data
            r.facebook_link = form.facebook_link.data
            r.website_link = form.website_link.data
            r.image_link = form.image_link.data
            r.seeking_venue = form.seeking_venue.data
            r.seeking_description = form.seeking_description.data
            db.session.add(r)
            db.session.commit()
            flash('Artist ' + form.name.data + ' Edited')
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('Artist ' + form.name.data + ' not  Edited.')

        finally:
            db.session.close()
    
    return redirect(url_for('show_artist', artist_id=artist_id)) 


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).one()

    form.state.process_data(venue.state)
    form.genres.process_data(venue.genres)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    edit_venue = Venue.query.filter_by(id=venue_id).one()
    edit_venue = db.session.merge(edit_venue)
    form = VenueForm()
    if not form.validate():
        for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    # do something with your errorMessages for fieldName
                    flash(err)
        return render_template('forms/edit_venue.html', form=form, venue=edit_venue)
    else: # Passed Form Validation Test
        try:
            edit_venue.name = form.name.data
            edit_venue.genres = form.genres.data
            edit_venue.address = form.address.data
            edit_venue.city = form.city.data
            edit_venue.state = form.state.data
            edit_venue.facebook_link = form.facebook_link.data
            edit_venue.website_link = form.website_link.data
            edit_venue.image_link = form.image_link.data
            edit_venue.seeking_talent = form.seeking_talent.data
            edit_venue.seeking_description = form.seeking_description.data
            db.session.add(edit_venue)
            db.session.commit()

            flash('Venue ' + form.name.data + ' was successfully Edited!')
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('An error occurred. Venue ' + form.name.data + ' could not be Edited.')
        finally:
            db.session.close()

        return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form ,meta={'csrf': False})
    try:
        if form.validate():
            new_artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            image_link=form.image_link.data,
            website_link = form.website_link.data,
            facebook_link=form.facebook_link.data,
            seeking_description = form.seeking_description.data,
            seeking_venue = form.seeking_venue.data)
            db.session.add(new_artist)
            db.session.commit()
            flash('Artist ' + form.name.data + ' Success')
        else:
            message = []
            for field, err in form.errors.items():
                message.append(field + ' ' + '|'.join(err))
            flash('Errors ' + str(message))
    except:
        db.session.rollback()
        flash(' Artist ' + form.name.data + ' Not Listed.')
    finally:
        db.session.close()
   
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.all() #list all shows at /shows

    data = list() # or data = []

    for s in shows: #loop
        v = Venue.query.get(s.venue_id)
        a = Artist.query.get(s.artist_id)
        data.extend([{
            "venue_id": v.id,
            "venue_name": v.name,
            "artist_id": a.id,
            "artist_name": a.name,
            "artist_image_link": a.image_link,
            "start_time": s.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        }])

   
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form,meta={'csrf': False})
    try:
        s = Show()
        s.artist_id = form.artist_id.data
        s.venue_id = form.venue_id.data
        s.start_time = form.start_time.data
        db.session.add(s)
        db.session.commit()
        flash('Show successfully listed!')
    except:
        db.session.rollback()
        flash('Ops, an error occured.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
