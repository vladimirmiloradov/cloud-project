from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User
import functools
from app import db
from sqlalchemy import exc

bp = Blueprint('auth', __name__, url_prefix='/auth')


def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Для доступа к данной странице необходимо пройти процедуру аутентификации.'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)
    login_manager.init_app(app)

def load_user(user_id):
    user = User.query.get(user_id)
    return user

USER_PARAMS = ['login', 'password_hash', 'last_name', 'first_name', 'middle_name', 'role_id']

def params():
    return { p: request.form.get(p) for p in USER_PARAMS }

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        if login and password:
            user = User.query.filter_by(login=login).first()
            if user and user.check_password(password):
                login_user(user)
                flash('Вы успешно аутентифицированы.', 'success')
                next = request.args.get('next')
                return redirect(next or url_for('index'))
        flash('Введены неверные логин и/или пароль.', 'danger')
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(**params())
        user.set_password(user.password_hash)
        user.role_id = 3
        print(user)
        try:
            db.session.add(user)
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка.', 'danger')
            return redirect(url_for('auth.register'))
        login_user(user)
        flash('Вы успешно зарегистрировались.', 'success')
        next = request.args.get('next')
        return redirect(next or url_for('index'))
    return render_template('auth/register.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def check_rights(action):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user = load_user(kwargs.get('user_id'))
            if not current_user.can(action, record=user):
                flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        return wrapper
    return decorator