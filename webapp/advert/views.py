from flask import Blueprint, render_template, current_app, abort, flash, redirect, request, url_for
from flask_login import current_user, login_required

from webapp.user.views import login
from webapp.advert.models import Advert, Comment
from webapp.advert.forms import CommentForm
from webapp.db import db
from webapp.weather import weather_by_city
from webapp.utils import get_redirect_target


blueprint = Blueprint('advert', __name__)

@blueprint.route('/')
def index():
    title = 'Объявления с Avito'
    title_mini = 'Гитары, струнные инструменты в Санкт-Петербурге'
    weather = weather_by_city(current_app.config['WEATHER_DEFAULT_CITY'])
    adverts_list = Advert.query.filter(Advert.text.isnot(None)).order_by(Advert.published.desc()).all()
    return render_template('advert/index.html', page_title = title, mini_title=title_mini, weather = weather, adverts_list = adverts_list)

@blueprint.route('/adverts/<int:advert_id>')
def single_advert(advert_id):
    my_advert = Advert.query.filter(Advert.id == advert_id).first()
    if not my_advert:
        abort(404)
    comment_form = CommentForm(advert_id=my_advert.id)
    return render_template('advert/single_advert.html', page_title=my_advert.title, advert=my_advert, comment_form=comment_form)

@blueprint.route('/adverts/comment', methods=['POST'])
@login_required
def add_comment():
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            text=form.comment_text.data,
            advert_id=form.advert_id.data,
            user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий успешно добавлен')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Ошибка в поле "{getattr(form, field).label.text}": - {error}')
    return redirect(get_redirect_target())
