from flask import Blueprint, render_template, current_app, abort, flash, redirect, request, url_for, send_file, send_from_directory
from flask_login import current_user, login_required
from datetime import datetime
# from werkzeug import secure_filename
import time
import os

from webapp.user.views import login
from webapp.advert.models import Advert, Comment
from webapp.user.models import User
from webapp.advert.forms import CommentForm, NewAdvertForm, UploadFilesForm
from webapp.db import db
from webapp.weather import weather_by_city
from webapp.utils import get_redirect_target


blueprint = Blueprint('advert', __name__)

@blueprint.route('/')
# @blueprint.route('/<int:page>')
def index():
    title = 'Объявления с Avito'
    title_mini = 'Гитары, струнные инструменты в Санкт-Петербурге'
    weather = weather_by_city(current_app.config['WEATHER_DEFAULT_CITY'])
    adverts_list = Advert.query.filter(Advert.description.isnot(None)).order_by(Advert.published.desc()) #.all()
    
    pages = adverts_list.paginate(page=None, per_page=4, error_out=False)
    # если запрошена страница свыше максимальной, то выдаётся последняя:
    if not pages.items:
        p = (pages.total//pages.per_page)
        if (pages.total%pages.per_page):
            pages = adverts_list.paginate(page=p+1, per_page=pages.per_page, error_out=False)
        else:
            pages = adverts_list.paginate(page=p, per_page=pages.per_page, error_out=False)
        print('ИЗМЕНЕНО pages.page=',pages.page)
    return render_template('advert/index.html', pages=pages, page_title=title, mini_title=title_mini, weather=weather)


@blueprint.route('/adverts/<int:advert_id>')
def single_advert(advert_id):
    one_advert = Advert.query.filter(Advert.id == advert_id).first()
    if not one_advert:
        abort(404)
    comment_form = CommentForm(advert_id=one_advert.id)
    img = url_for('static', filename=str(advert_id)+'/guitar.jpg')
    return render_template('advert/single_advert.html', page_title=one_advert.title, advert=one_advert, image=img, comment_form=comment_form)


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


@blueprint.route('/adverts/new-advert')
@login_required
def new_advert():
    form_data = {}
    if request.args:
        param_list = ['title', 'description', 'address', 'phone']
        for param in request.args:
            if param in param_list:
                form_data[param] = request.args.get(param)
    form = NewAdvertForm(
        user_id=current_user.id, 
        title=form_data.get('title'), 
        description=form_data.get('description'), 
        address=form_data.get('address'), 
        phone=form_data.get('phone')
        )
    page_title = 'Новое объявление!'
    return render_template('advert/create_advert_step1.html', page_title=page_title, form=form)


@blueprint.route('/adverts/creating', methods=['POST'])
@login_required
def creating_advert():
    form = NewAdvertForm()
    valid = True
    try:
        form.price.data = float((form.price.data).strip(' pPsS$rRрР,.').replace(' ', '').replace(',', '.'))
    except (TypeError, ValueError):
        valid = False
        flash(f'Ошибка в поле "Стоимость товара": - Укажите стоимость цифрами в формате "12345.67"')
    try:
        form.company.data = bool(int(form.company.data))
    except (TypeError, ValueError):
        valid = False
        flash(f'Ошибка в поле "Компания или Частное лицо"')
    if form.validate_on_submit() and valid:
        new_advert = Advert(
            title=form.title.data,
            theme = form.theme.data,
            url = str(time.time()),
            price = form.price.data,
            published = datetime.now(),
            description = form.description.data,
            address = form.address.data,
            seller = current_user.username,
            company = form.company.data,
            phone = form.phone.data,
            foto = None, #len(request.files),
            user_id = current_user.id,
            closed = False,
            fail_check = None
        )
        db.session.add(new_advert)
        db.session.commit()
        flash('Объявление успешно создано!')
        advert_id = Advert.query.filter(Advert.url == new_advert.url).all()
        print('\n\nADVERT ID =', advert_id[0].id)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Ошибка в поле "{getattr(form, field).label.text}": - {error}')
        return redirect(url_for('advert.new_advert', 
            title=form.title.data, 
            description=form.description.data, 
            address = form.address.data, 
            phone = form.phone.data
            ))
    return redirect(url_for('advert.upload_files', advert_id=advert_id[0].id))


@blueprint.route('/adverts/<int:advert_id>/upload')
@login_required
def upload_files(advert_id):
    my_advert = Advert.query.filter(Advert.id == advert_id).first()
    if not my_advert:
        abort(404)
    if not current_user.id == my_advert.user_id:
        flash('Нельзя редактировать чужие объявления')
        redirect(get_redirect_target())
    form = UploadFilesForm(
        user_id=current_user.id,
        advert_id=my_advert.id
        )
    page_title = 'Новое объявление!'
    return render_template('advert/create_advert_step2.html', page_title=page_title, advert=my_advert, form=form)


@blueprint.route('/adverts/uploading', methods=['POST'])
@login_required
def uploading():
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']
    if request.method == 'POST':

        print('=============КОЛ-ВО ФАЙЛОВ', request.files)#rf) #request.files['photos'])
        # ============request.files===КОЛ-ВО ФАЙЛОВ ImmutableMultiDict([('photos', <FileStorage: 'QCY BOX2 1.jpg' ('image/jpeg')>), ('photos', <FileStorage: 'QCY BOX2 2.jpg' ('image/jpeg')>), ('photos', <FileStorage: 'QCY BOX2 3.jpg' ('image/jpeg')>)])
        #     file = request.files[rfile]
        #     # if file and allowed_file(file.filename):
        #     filename = file.filename
        #     file.save(os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], filename))
        # return redirect(url_for('advert.index'))
