from models import Image, Review, Film
import hashlib
import uuid
import os
from werkzeug.utils import secure_filename
from flask import request, flash
from app import db, app
from sqlalchemy import exc


class FilmsFilter:
    def __init__(self, name):
        self.name = name
        self.query = Film.query
    
    def perform(self):
        self.__filter_by_name()
        return self.query.order_by(Film.created_at.desc())
    
    def __filter_by_name(self):
        if self.name:
            self.query = self.query.filter(Film.name.ilike('%' + self.name + '%'))
    


class ReviewsFilter:
    def __init__(self, film_id):
        self.query = Review.query.filter_by(film_id=film_id)

    def perform_date_desc(self):
        return self.query.order_by(Review.created_at.desc())

    def perform_date_asc(self):
        return self.query.order_by(Review.created_at.asc())

    def perform_rating_desc(self):
        return self.query.order_by(Review.rating.desc())

    def perform_rating_asc(self):
        return self.query.order_by(Review.rating.asc())

    def sorting(self, param):
        reviews = self.perform_date_desc()
        if param == 'old':
            reviews = self.perform_date_asc()
        elif param == 'good':
            reviews = self.perform_rating_desc()
        elif param == 'bad':
            reviews = self.perform_rating_asc()
        return reviews

class ImageSaver:
    def __init__(self, file):
        self.file = file
    
    def save(self, film_id):
        self.img = self.__find_by_md5_hash()
        flag = False
        if self.img is not None:
            flag = True
        file_name = secure_filename(self.file.filename)
        self.img = Image(
            id=str(uuid.uuid4()), 
            filename=file_name, 
            mime_type=self.file.mimetype, 
            md5_hash=self.md5_hash
        )
        if flag != True:
            self.file.save(os.path.join(app.config['UPLOAD_FOLDER'], self.img.storage_filename ))
        self.img.film_id = film_id
        try:
            db.session.add(self.img)
            db.session.commit()
        except exc.SQLAlchemyError: 
            db.session.rollback()
            return flash('Фильм с такой обложкой уже существует!', 'danger')      
        return self.img


    def __find_by_md5_hash(self):
        self.md5_hash = hashlib.md5(self.file.read()).hexdigest()
        self.file.seek(0)
        return Image.query.filter(Image.md5_hash == self.md5_hash).first()
