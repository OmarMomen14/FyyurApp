from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, RadioField, TextAreaField, IntegerField, TextField
from wtforms.validators import DataRequired, AnyOf, URL, NumberRange
from genres_list import genres
from wtforms import ValidationError
import phonenumbers


# Get Genres choices
genres_choices = []
for genre in genres:
    genres_choices.append((genre,genre))

# I have included some validators in the from field
# but it doesn't seem to be working well, and i have
# spent so long time to find out the reason but couldn't
# find it

class ShowForm(Form):
    artist_id = IntegerField(
        'artist_id', 
        validators = [DataRequired(), 
        NumberRange(min=1, max=99999)
        ]
    )
    venue_id = IntegerField(
        'venue_id',
        validators = [DataRequired(),
        NumberRange(min=1, max=99999)
        ]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    address = StringField(
        'address'
    )
    phone = StringField(
        'phone', 
        validators=[DataRequired()]
    )
    # I got this custom validation from the wtforms docs
    # And the validation method from a stackoverflow answer
    # However, it doesn't seem to work, it took me forever to debug
    # But never found a solution 
    # Wtforms docs: https://wtforms.readthedocs.io/en/2.3.x/validators/
    # Stackoverflow answer: https://stackoverflow.com/questions/36251149/validating-us-phone-number-in-wtfforms

    def validate_phone(form, field):
        if len(field.data) > 16:
            raise ValidationError('Invalid phone number.')
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')
        except:
            input_number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')

    image_link = StringField(
        'image_link',
        validators=[URL()]
    )
    website_link = StringField(
        'website_link',
        validators=[URL()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices = genres_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    seek_talents = RadioField(
        'seek_talents',
        choices=[('yes','Yes'),('no','No')]
    )
    seek_description = TextAreaField(
        'seek_description'
    )

class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    phone = StringField(
        'phone', 
        validators=[DataRequired()]
    )
    def validate_phone(form, field):
        if len(field.data) > 16:
            raise ValidationError('Invalid phone number.')
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')
        except:
            input_number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')

    image_link = StringField(
        'image_link',
        validators=[URL()]
    )
    website_link = StringField(
        'website_link',
        validators=[URL()]
    )
    genres = SelectMultipleField(
        'genres', 
        validators = [DataRequired()],
        choices = genres_choices
    )
    facebook_link = StringField(
        'facebook_link', 
        validators=[URL()]
    )
    seek_venues = RadioField(
        'seek_venues',
        choices=[('yes','Yes'),('no','No')]
    )
    seek_description = TextAreaField(
        'seek_description'
    )

# TODO(DONE) IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM
