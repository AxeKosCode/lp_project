from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user

from webapp.user.forms import LoginForm, RegistrationForm
from webapp.user.models import User
from webapp.utils import get_redirect_target
from webapp.db import db
# from webapp.temp_var import reff
# from . import reff

blueprint = Blueprint('user', __name__, url_prefix='/users')
@blueprint.route('/login')
def login():
    if current_user.is_authenticated:
        print('!!! USER is authenticated !!!')
        return redirect(get_redirect_target())
    title = 'Авторизация'
    login_form = LoginForm()
    return render_template('user/login.html', page_title=title, form=login_form)

@blueprint.route('/process_login', methods=['POST'])
def process_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Вы успешно вошли на сайт')
            return redirect(get_redirect_target())
        flash('Неправильные имя пользователя или пароль')
        return redirect(url_for('user.login'))

@blueprint.route('/logout')
def logout():
    logout_user()
    flash('Вы покинули сайт')
    return redirect(get_redirect_target())

@blueprint.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('advert.index'))
    # global reff
    # reff = '/'
    # if not request.referrer==request.url:
    #     if request.referrer==None:
    #         reff = '/'
    #     else:
    #         reff = request.referrer
    # print('reff\t\t=',reff,'\n'+'request.\t=',request.referrer)
    form = RegistrationForm()
    title = 'Регистрация'
    return render_template('user/registration.html', page_title=title, form=form)

@blueprint.route('/process_reg', methods=['POST'])
def process_reg():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, role='user')
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Вы успешно зарегистрировались!')
        login_user(new_user)
        flash('Вы успешно вошли на сайт')
        print(current_user.is_authenticated)
        return redirect(url_for('advert.index'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Ошибка в поле "{getattr(form, field).label.text}": - {error}')
        return redirect(url_for('user.register'))
