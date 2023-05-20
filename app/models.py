import sqlalchemy as sa
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from flask import url_for
from app import db, app
import os
from users_policy import UsersPolicy 


class Film(db.Model):
    __tablename__ = 'films'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_desc = db.Column(db.Text, nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    volume = db.Column(db.Integer, nullable=False)
    rating_sum = db.Column(db.Integer, nullable=False, default=0)
    rating_num = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())

    def __repr__(self):
        return '<Film %r>' % self.name
    
    @property
    def rating(self):
        if self.rating_num > 0:
            return self.rating_sum / self.rating_num
        return 0

class Roles(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Roles %r>' % self.name

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return ' '.join([self.last_name, self.first_name, self.middle_name or ''])
    
    @property
    def is_admin(self):
        return app.config.get('ADMIN_ROLE_ID') == self.role_id
    
    @property
    def is_moder(self):
        return app.config.get('MODER_ROLE_ID') == self.role_id
    
    @property
    def is_user(self):
        return app.config.get('USER_ROLE_ID') == self.role_id

    def __repr__(self):
        return '<User %r>' % self.login

    def can(self, action, record=None):
        users_policy = UsersPolicy(record=record)
        method = getattr(users_policy, action, None)
        if method is not None:
            return method()
        return False

class Selection(db.Model):
    __tablename__ = 'selections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    user = db.relationship('User')

    def __repr__(self):
        return '<Selection %r>' % self.name

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('films.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())

    film = db.relationship('Film')
    user = db.relationship('User')

    def __repr__(self):
        return '<Review %r>' % self.text

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.String(100), primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    md5_hash = db.Column(db.String(100), nullable=False)
    film_id = db.Column(db.Integer, db.ForeignKey('films.id', ondelete='CASCADE'))
    object_id = db.Column(db.Integer)
    object_type = db.Column(db.String(100))

    film = db.relationship('Film')

    def __repr__(self):
        return '<Image %r>' % self.filename
    
    @property
    def storage_filename(self):
        _, ext = os.path.splitext(self.filename)
        return self.id + ext
    
    @property
    def url(self):
        return url_for('image', image_id=self.id)

class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return '<Genre %r>' % self.name

class Join(db.Model):
    __tablename__ = 'join'

    id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('films.id', ondelete='CASCADE'))
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id', ondelete='CASCADE'))

    film = db.relationship('Film')
    genre = db.relationship('Genre')

    def __repr__(self):
        return '<Join %r>' % self.id

class FilmSelection(db.Model):
    __tablename__ = 'film_selection'

    id = db.Column(db.Integer, primary_key=True)
    selection_id = db.Column(db.Integer, db.ForeignKey('selections.id', ondelete='CASCADE'), nullable=False)
    film_id = db.Column(db.Integer, db.ForeignKey('films.id', ondelete='CASCADE'))

    selection = db.relationship('Selection')
    film = db.relationship('Film')

    def __repr__(self):
        return '<FilmSelection %r>' % self.id


















