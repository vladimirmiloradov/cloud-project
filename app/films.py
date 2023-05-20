from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app import db
from models import Film, User, Review, Genre, Join, Image, Selection, FilmSelection
from tools import FilmsFilter, ImageSaver, ReviewsFilter
from auth import check_rights
import os
import markdown
import bleach
from sqlalchemy import exc



bp = Blueprint('films', __name__, url_prefix='/films')

PER_PAGE = 1
PER_PAGE_REVIEWS = 10

FILM_PARAMS = ['name', 'short_desc', 'publication_year', 'author', 'volume']
REVIEW_PARAMS = ['film_id', 'user_id', 'rating', 'text']
SELECTION_PARAMS = ['name','user_id']

def params():
    return { p: request.form.get(p) for p in FILM_PARAMS }

def selection_params():
    return { p: request.form.get(p) for p in SELECTION_PARAMS }

def review_params():
    return { p: request.form.get(p) for p in REVIEW_PARAMS }
    
def search_params():
    return {'name': request.args.get('name')}

def search_params_review(film_id):
    return {
        'name': request.args.get('name'),
        'film_id': film_id
    }


@bp.route('/<int:film_id>/delete', methods=['POST'])
@login_required
@check_rights('delete')
def delete(film_id):
    film = Film.query.filter_by(id=film_id).one()
    img = Image.query.filter_by(film_id=film.id).one()
    img = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images') + '\\' + img.storage_filename
    db.session.delete(film)
    db.session.commit()
    flash('Фильм был успешно удален!', 'success')
    return redirect(url_for('index'))

@bp.route('/new')
@login_required
@check_rights('create')
def new():
    genres = Genre.query.all()
    return render_template('films/new.html', genres=genres)

@bp.route('/create', methods=['POST'])
@login_required
@check_rights('create')
def create():
    film = Film(**params())
    film.short_desc = bleach.clean(film.short_desc)
    try:
        db.session.add(film)
        db.session.commit()
    except exc.SQLAlchemyError:
        db.session.rollback()
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        return redirect(url_for('films.new'))
    film = Film.query.order_by(Film.id.desc()).first()
    f = request.files.get('background_img')
    if f and f.filename:
        img = ImageSaver(f).save(film.id)
        if img == None:
            db.session.delete(film)
            db.session.commit()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return redirect(url_for('films.new'))
    array_genres = request.form.getlist('genre')
    if len(array_genres) == 0:
        flash('При сохранении данных возникла ошибка. Выберите жанры для фильма.', 'danger')
        return redirect(url_for('films.new'))
    for genre in array_genres:
        film_genre = Join()
        film_genre.film_id = film.id
        film_genre.genre_id = genre
        db.session.add(film_genre)
    db.session.commit()
    flash(f'Фильм {film.name} был успешно добавлен!', 'success')
    return redirect(url_for('index'))

@bp.route('/<int:film_id>/edit')
@login_required
@check_rights('update')
def edit(film_id):
    genres = Genre.query.all()
    genres_arr = Join.query.filter_by(film_id=film_id).all()
    selected = []
    for genre in genres_arr:
        selected.append(genre.genre.id)
    film = Film.query.filter_by(id=film_id).one()
    return render_template('films/edit.html', genres=genres, selected=selected, film=film)

@bp.route('/<int:film_id>/update', methods=['POST'])
@login_required
@check_rights('update')
def update(film_id):
    film = Film.query.filter_by(id=film_id).one()
    parameters = params()
    film.name = parameters['name']
    film.short_desc = parameters['short_desc']
    film.short_desc = bleach.clean(film.short_desc)
    film.publiation_year = parameters['publication_year']
    film.author = parameters['author']
    film.volume = parameters['volume']
    db.session.commit()
    flash(f'Фильм {film.name} был успешно обновлен!', 'success')
    return redirect(url_for('index'))  

@bp.route('/<int:film_id>')
@login_required
def show(film_id):
    films = Film.query.get(film_id)
    films.short_desc = markdown.markdown(films.short_desc)
    reviews = Review.query.filter_by(film_id=film_id).limit(5)
    user_review = None
    if current_user.is_authenticated is True:
        user_review = Review.query.filter_by(film_id=film_id, user_id=current_user.id).first()
        if user_review:
            user_review.text = markdown.markdown(user_review.text)
    users = User.query.all()
    film_genres = Join.query.filter_by(film_id=film_id).all()
    genres=[]
    for genre in film_genres:
        genres.append(genre.genre.name)
    genres = ', '.join(genres)
    img = Image.query.filter_by(film_id=film_id).first()
    img = img.url
    selections = Selection.query.filter_by(user_id=current_user.id).all()
    return render_template('films/show.html', film=films, review=reviews, users=users, user_review=user_review, genres=genres, image=img, selections=selections)

@bp.route('/<int:film_id>', methods=['POST'])
@login_required
def apply_review(film_id):
    films = Film.query.filter_by(id=film_id).first()
    review = Review(**review_params())
    review.text = bleach.clean(review.text)
    if not review.text:
        review.text = None
    films.rating_sum += int(review.rating)
    films.rating_num += 1
    try:
        db.session.add(review)
        db.session.commit()
        flash('Ваш отзыв успешно записан!', 'success')
        return redirect(url_for('films.show', film_id=films.id))
    except exc.SQLAlchemyError:
        db.session.rollback()
        flash('Ошибка записи отзыва! Отзыв не может быть пустым!', 'danger')
        return redirect(url_for('films.apply_review', film_id=films.id))



@bp.route('/<int:film_id>/reviews')
@login_required
def reviews(film_id):
    param = request.args.get('param')
    page = request.args.get('page', 1, type=int)
    reviews = ReviewsFilter(film_id).sorting(param)
    films = Film.query.filter_by(id=film_id).first()
    pagination = reviews.paginate(page=page, per_page=PER_PAGE_REVIEWS, error_out=False)
    reviews = pagination.items
    return render_template('films/reviews.html', reviews=reviews, films=films, pagination=pagination, search_params=search_params_review(film_id), param=param)

@bp.route('/user_selections')
@login_required
@check_rights('create_selection')
def user_selections():
    endpoint = '/films/user_selections'
    selections = Selection.query.filter_by(user_id=current_user.id).all()
    array_counts = []
    for selection in selections:
        sel_id = selection.id
        count = len(FilmSelection.query.filter_by(selection_id=sel_id).all())
        array_counts.append(count)
    return render_template('films/selections.html', endpoint=endpoint, selections=selections, array_counts=array_counts)

@bp.route('/user_selections/<int:selection_id>/show_user_selection')
@login_required
@check_rights('create_selection')
def show_user_selection(selection_id):
    array_films_ids = []
    rows = FilmSelection.query.filter_by(selection_id=selection_id).all()
    for row in rows:
        array_films_ids.append(row.film_id)
    films = []
    for id in array_films_ids:
        film = Film.query.filter_by(id=id).first()
        films.append(film)
    print(films)
    images_for_films = []
    film_genres = []
    for film in films:
        image = Image.query.filter_by(film_id=film.id).first()
        images_for_films.append(image.url)
        genres_rows = Join.query.filter_by(film_id=film.id).all()
        genres = []
        for genre in genres_rows:
            genres.append(genre.genre.name)
        genres_str =', '.join(genres)
        film_genres.append(genres_str)
    selection_id = selection_id
    return render_template('films/user_selection.html', films=films, search_params=search_params(), images=images_for_films, genres=film_genres, selection_id=selection_id)

@bp.route('/<int:user_id>/create_selection', methods=['POST'])
@login_required
@check_rights('create_selection')
def create_selection(user_id):
    selection = Selection(**selection_params())
    selection.user_id = user_id
    db.session.add(selection)
    db.session.commit()
    flash(f'Подборка {selection.name} была успешно добавлена!', 'success')
    return redirect(url_for('films.user_selections'))

@bp.route('/<int:film_id>/add_film_to_selection', methods=['POST'])
@login_required
@check_rights('create_selection')
def add_film_to_selection(film_id):
    selection = request.form.get('selection')
    row = FilmSelection()
    row.film_id = film_id
    row.selection_id = selection
    try:
        db.session.add(row)
        db.session.commit()
        flash(f'Фильм был успешно добавлен в подборку!', 'success')
        return redirect(url_for('films.show', film_id=film_id))
    except exc.SQLAlchemyError:
        flash('Ошибка при добавлении фильма в подборку! Выберите подборку.', 'danger')
        return redirect(url_for('films.show', film_id=row.film_id))


# NEED FIX
@bp.route('/<int:selection_id>/delete-film-from-selection', methods=['POST'])
@login_required
def delete_film_from_selection(selection_id):
    row = FilmSelection.query.filter_by(selection_id=selection_id).one()
    print(row)
    db.session.delete(row)
    db.session.commit()
    flash('Фильм был успешно удален из подборки!', 'success')
    return redirect(url_for('films.user_selections'))
# NEED FIX
