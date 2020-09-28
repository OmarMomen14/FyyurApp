#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from genres_list import genres
from datetime import datetime
from sqlalchemy import func, or_

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO(DONE): connect to a local postgresql database



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# The DB scheme design is as follow:

# Three Main Tables (Entities) :
##### 1. "Venue"
##### 2. "Artist"
##### 3. "Show"

# One Fixed Table: 
##### 4. "Genre" 
# 
# Which Gets populated from a python file 
# -genres_list.py- once when the db 
# is initiated for the first time, and if the file
# got updated, the new genres gets populated to 
# the db automatically

# Two Associative tables 
##### 5. "venue_genre_map"
##### 6. "artist_genre_map"

# With 2 One-to-Many relationships between: 
### Venue[parent] and Show[child]
### Artist[parent] and Show[child]

# And 2 Many-to-Many relationships between:
### Venue[parent] and Genre[child]
### Artist[parent] and Genre[child]
# Those 2 relationships are using 2 associative 
# tables to record the mapping between each entity 
# (either Venue or Artist) with Its associated 
# Genres

venue_genre_map = db.Table( 
  'venue_genre_map',
  db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key = True),
  db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key = True)
)

artist_genre_map = db.Table( 
  'artist_genre_map',
  db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key = True),
  db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key = True)
)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    address = db.Column(db.String(120), default = '')
    phone = db.Column(db.String(120), nullable = False)
    image_link = db.Column(db.String(500), default='')
    facebook_link = db.Column(db.String(120), default='')
    website_link = db.Column(db.String(120), default='')
    seek_talents = db.Column(db.Boolean, default = False)
    seek_description = db.Column(db.String(120), default='')

    genres = db.relationship(
      'Genre', 
      secondary = venue_genre_map,
      backref = db.backref('venues', lazy=True)
    )

    shows = db.relationship(
      'Show', 
      backref = 'venue', 
      lazy = True, 
      collection_class = list, 
      cascade = 'save-update'
    )

    # TODO(DONE): implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120), nullable = False)
    image_link = db.Column(db.String(500), default = '')
    facebook_link = db.Column(db.String(120), default = '')
    website_link = db.Column(db.String(120), default='')
    seek_venues = db.Column(db.Boolean, default = False)
    seek_description = db.Column(db.String(120), default='')

    genres = db.relationship(
      'Genre', 
      secondary = artist_genre_map,
      backref = db.backref('artists', lazy=True)
    )

    shows = db.relationship('Show', backref = 'artist', lazy = True, collection_class = list, cascade = 'save-update')

    # TODO(DONE): implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key = True)
  datetime = db.Column(db.DateTime, nullable = False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False)

class Genre(db.Model):
  __tablename__ = 'Genre'

  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(120), nullable=False)

# TODO(DONE) Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Updated Genres Table in DB if any new genre is 
# added to the genres_list.py file

def populate_genres_table():
  genres_in_db = Genre.query.all()
  genres_names_db = []

  for genre in genres_in_db:
    genres_names_db.append(genre.name.lower())

  for genre in genres:
    if(genre.lower() not in genres_names_db):
      try:
        new_genre = Genre(name = genre)
        db.session.add(new_genre)
        db.session.commit()
      except:
        db.session.rollback()
        print(sys.exc_info())
      finally:
        db.session.close()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)
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
  # TODO(DONE): replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  all_venues = Venue.query.all()

  grouped_venues_by_city = {}
  for venue in all_venues:
    grouped_venues_by_city[venue.city.lower()] = []
  
  for venue in all_venues:
    grouped_venues_by_city[venue.city.lower()].append(venue)
  
  return render_template('pages/venues.html', areas=grouped_venues_by_city)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO(DONE): implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(func.lower(Venue.name).contains(search_term.lower())).all()

  response={
    "count": len(venues),
    "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term= search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO(DONE): replace with real venue data from the venues table, using venue_id
  
  venue_exist = bool(Venue.query.get(int(venue_id)))
  if not venue_exist:
    abort(404)

  venue = Venue.query.get(int(venue_id))
  venue_shows = venue.shows
  past_shows = []
  upcoming_shows = []
  for show in venue_shows:
    if (show.datetime >= datetime.now()):
      artist_id = show.artist_id
      artist = Artist.query.get(artist_id)
      upcoming_shows.append({
        'artist_id': artist_id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': str(show.datetime)
      })
    else:
      artist_id = show.artist_id
      artist = Artist.query.get(artist_id)
      past_shows.append({
        'artist_id': artist_id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': str(show.datetime)
      })
  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)

  shows = {
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': past_shows_count,
    'upcoming_shows_count': upcoming_shows_count
  }

  return render_template('pages/show_venue.html', venue=venue, shows = shows)

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO(DONE): insert form data as a new Venue record in the db, instead
  # TODO(DONE): modify data to be the data object returned from db insertion
  error = False
  try:
    new_venue = Venue()

    new_venue.name = request.form.get('name','').title()
    new_venue.city = request.form.get('city','').title()
    new_venue.state = request.form.get('state','')
    new_venue.address = request.form.get('address','')
    new_venue.phone = request.form.get('phone','')
    new_venue.image_link = request.form.get('image_link','')
    new_venue.facebook_link = request.form.get ('facebook_link','')
    new_venue.website_link = request.form.get ('website_link','')

    if request.form.get('seek_talents','') == 'yes':
      new_venue.seek_talents = True
      new_venue.seek_description = request.form.get('seek_description','')
    else:
      new_venue.seek_talents = False
    
    chosen_genres = request.form.getlist('genres')
    genres_list = []
    for genre in chosen_genres:
      g = Genre.query.filter(Genre.name == genre).first()
      if g != None:
        genres_list.append(g)
    if len(genres_list) > 0:
      new_venue.genres = genres_list 
    
    db.session.add(new_venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. The Venue could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return redirect(url_for('index'))


  # TODO(DONE): on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  # TODO:(DONE) Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  venue_exist = bool(Venue.query.get(int(venue_id)))
  if not venue_exist:
    abort(404)

  error = False
  try:
    venue = Venue.query.get(venue_id)
    venue_name = venue.name
    shows = venue.shows

    for show in shows:
      db.session.delete(show)

    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue '+venue_name+' could not be deleted.')
  else:
    flash('Venue '+ venue_name+' was successfully removed!')
  
  return redirect(url_for('index'))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  venue_exist = bool(Venue.query.get(int(venue_id)))
  if not venue_exist:
    abort(404)

  venue = Venue.query.get(venue_id)
  genres = []
  for g in venue.genres:
    genres.append(g.name)
  if venue.seek_talents:
    seek_talents = 'yes'
  else:
    seek_talents = 'no'

  form = VenueForm(state = venue.state, genres = genres, seek_talents = seek_talents, seek_description = venue.seek_description)
  

  # TODO(DONE): populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO(DONE): take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  venue_exist = bool(Venue.query.get(int(venue_id)))
  if not venue_exist:
    abort(404)

  error = False
  try:
    venue = Venue.query.get(venue_id)

    venue.name = request.form.get('name','')
    venue.city = request.form.get('city','')
    venue.state = request.form.get('state','')
    venue.address = request.form.get('address','')
    venue.phone = request.form.get('phone','')
    venue.image_link = request.form.get('image_link','')
    venue.facebook_link = request.form.get ('facebook_link','')
    venue.website_link = request.form.get ('website_link','')

    if request.form.get('seek_talents','') == 'yes':
      venue.seek_talents = True
      venue.seek_description = request.form.get('seek_description','')
    else:
      venue.seek_talents = False
      venue.seek_description = ''
    
    chosen_genres = request.form.getlist('genres')
    genres_list = []
    for genre in chosen_genres:
      g = Genre.query.filter(Genre.name == genre).first()
      if g != None:
        genres_list.append(g)
    
    venue.genres = genres_list
    
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. The Venue could not be edited.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO(DONE): replace with real data returned from querying the database
  
  artists = Artist.query.all()
  
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO(DONE): implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(func.lower(Artist.name).contains(search_term.lower())).all()

  response={
    "count": len(artists),
    "data": artists
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO(DONE): replace with real venue data from the venues table, using venue_id
  
  artist_exist = bool(Artist.query.get(int(artist_id)))
  if not artist_exist:
    abort(404)

  artist = Artist.query.get(int(artist_id))
  artist_shows = artist.shows

  past_shows = []
  upcoming_shows = []
  for show in artist_shows:
    if (show.datetime >= datetime.now()):
      venue_id = show.venue_id
      venue = Venue.query.get(venue_id)
      upcoming_shows.append({
        'venue_id': venue_id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': str(show.datetime)
      })
    else:
      venue_id = show.venue_id
      venue = Venue.query.get(venue_id)
      past_shows.append({
        'venue_id': venue_id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': str(show.datetime)
      })
  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)

  shows = {
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': past_shows_count,
    'upcoming_shows_count': upcoming_shows_count
  }
  
  return render_template('pages/show_artist.html', artist=artist, shows = shows )

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  artist_exist = bool(Artist.query.get(int(artist_id)))
  if not artist_exist:
    abort(404)

  artist = Artist.query.get(artist_id)
  
  genres = []
  for g in artist.genres:
    genres.append(g.name)
  if artist.seek_venues:
    seek_venues = 'yes'
  else:
    seek_venues = 'no'

  form = ArtistForm(state = artist.state, genres = genres, seek_venues = seek_venues, seek_description = artist.seek_description)
  
  # TODO(DONE): populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO(DONE): take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist_exist = bool(Artist.query.get(int(artist_id)))
  if not artist_exist:
    abort(404)

  error = False
  try:
    artist = Artist.query.get(artist_id)

    artist.name = request.form.get('name','')
    artist.city = request.form.get('city','')
    artist.state = request.form.get('state','')
    artist.address = request.form.get('address','')
    artist.phone = request.form.get('phone','')
    artist.image_link = request.form.get('image_link','')
    artist.facebook_link = request.form.get ('facebook_link','')
    artist.website_link = request.form.get ('website_link','')

    if request.form.get('seek_venues','') == 'yes':
      artist.seek_venues = True
      artist.seek_description = request.form.get('seek_description','')
    else:
      artist.seek_venues = False
      artist.seek_description = ''
    
    chosen_genres = request.form.getlist('genres')
    genres_list = []
    for genre in chosen_genres:
      g = Genre.query.filter(Genre.name == genre).first()
      if g != None:
        genres_list.append(g)
    
    artist.genres = genres_list
    
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. The Artist could not be edited.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO(DONE): insert form data as a new Venue record in the db, instead
  # TODO(DONE): modify data to be the data object returned from db insertion

  error = False
  try:
    new_artist = Artist()

    new_artist.name = request.form.get('name','')
    new_artist.city = request.form.get('city','')
    new_artist.state = request.form.get('state','')
    new_artist.phone = request.form.get('phone','')
    new_artist.image_link = request.form.get('image_link','')
    new_artist.facebook_link = request.form.get ('facebook_link','')
    new_artist.website_link = request.form.get ('website_link','')

    if request.form.get('seek_venues','') == 'yes':
      new_artist.seek_venues = True
      new_artist.seek_description = request.form.get('seek_description','')
    else:
      new_artist.seek_venues = False
    
    chosen_genres = request.form.getlist('genres')
    genres_list = []
    for genre in chosen_genres:
      g = Genre.query.filter(Genre.name == genre).first()
      if g != None:
        genres_list.append(g)
    if len(genres_list) > 0:
      new_artist.genres = genres_list 
    
    db.session.add(new_artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. The Artist could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('index'))

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO(DONE): on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')

@app.route('/artists/<artist_id>/delete', methods=['GET'])
def delete_artist(artist_id):
  # TODO(DONE): Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  artist_exist = bool(Artist.query.get(int(artist_id)))
  if not artist_exist:
    abort(404)

  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist_name = artist.name
    shows = artist.shows

    for show in shows:
      db.session.delete(show)

    db.session.delete(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist '+artist_name+' could not be deleted.')
  else:
    flash('Artist '+ artist_name+' was successfully removed!')
  
  return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO(DONE): replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  all_shows = Show.query.all()
  shows = []
  for show in all_shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    shows.append({
      'venue_id': venue.id,
      'venue_name': venue.name,
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': str(show.datetime)     
    })

  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create', methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO(DONE): insert form data as a new Show record in the db, instead

  error = False
  try:
    new_show = Show()

    artist_id = int(request.form.get('artist_id'))
    venue_id = int(request.form.get('venue_id'))
    artist_exist = bool(Artist.query.get(artist_id))
    venue_exist = bool(Venue.query.get(venue_id))
    
    if (not artist_exist):
      flash('The Artist ID does not exist, please key in an existing Artist ID.')
      
      return redirect(url_for('create_show_submission'))

    if (not venue_exist):
      flash('The Venue ID does not exist, please key in an existing Venue ID.')
      
      return redirect(url_for('create_show_submission'))

    new_show.artist_id = artist_id
    new_show.venue_id = venue_id
    new_show.datetime = request.form.get('start_time')
    
    db.session.add(new_show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. The Show could not be listed.')
    return redirect(url_for('create_show_submission')) 
  else:
    flash('The Show was successfully listed!')
    return redirect(url_for('index'))  

  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO(DONE): on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

@app.route('/shows/search', methods=['POST'])
def search_shows():
  
  search_term = request.form.get('search_term', '')
  
  shows = Show.query.filter(
    or_(
      func.lower(Artist.name).contains(search_term.lower()),
      func.lower(Venue.name).contains(search_term.lower())      
    )  
  ).all()

  data = []
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    data.append({
      'venue_id': venue.id,
      'venue_name': venue.name,
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': str(show.datetime)     
    })

  response={
    "count": len(shows),
    "shows": data
  }

  return render_template('pages/search_show.html', results=response, search_term=search_term)

#  Errors
#  ----------------------------------------------------------------

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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