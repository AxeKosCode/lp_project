from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SelectField, RadioField, TextAreaField, FloatField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from webapp.advert.models import Advert
from webapp.user.models import User


class CommentForm(FlaskForm):
    advert_id = HiddenField('ID объявления', validators=[DataRequired()])
    comment_text = StringField('Ваш комментарий', validators=[DataRequired()], render_kw={"class": "form-control"})
    submit = SubmitField('Отправить!',render_kw={"class": "btn btn-success"})

    def validate_advert_id(self, advert_id):
        if not Advert.query.get(advert_id.data):
            raise ValidationError('Объявления с таким id не существует')


class NewAdvertForm(FlaskForm):
    user_id = HiddenField('ID пользователя', validators=[DataRequired()])
    theme = SelectField(u'Тематика', choices=[('Гитары и другие струнные', 'Гитары, струнные инструменты в Санкт-Петербурге')])
    title = StringField('Название товара', validators=[DataRequired()], render_kw={"class": "form-control"})
    description = TextAreaField('Описание товара', validators=[DataRequired()], render_kw={"class": "form-control"})
    address = StringField('Где находится товар? <span class="gray">(Город, улица, метро..)</span>', validators=[DataRequired()], render_kw={"class": "form-control"})
    price = StringField('Стоимость товара <span class="gray"> (Укажите стоимость цифрами в формате "12345.67")</span>', validators=[DataRequired()], render_kw={"class": "form-control"})
    phone = StringField('Номер телефона продавца <span class="gray">(в формате 9991234567)</span>', validators=[DataRequired()], render_kw={"class": "form-control"})
    company = RadioField(u'Компания или Частное лицо?', choices=[(0, 'Частное лицо'), (1, 'Компания')], default=0)
    submit = SubmitField('Опубликовать!',render_kw={"class": "btn btn-success"})

    def validate_user_id(self, user_id):
        if not User.query.get(user_id.data):
            raise ValidationError('Пользователя с таким id не существует')


class UploadFilesForm(FlaskForm):
    user_id = HiddenField('ID пользователя', validators=[DataRequired()])
    advert_id = HiddenField('ID объявления', validators=[DataRequired()])
    photos = MultipleFileField(label='Фотографии товара <span class="gray">(можно выбрать сразу несколько)</span>', render_kw={"class":"form-control-file"}, validators=[DataRequired()])
    submit = SubmitField('Загрузить!',render_kw={"class": "btn btn-success btn-lg btn-block"})

    def validate_user_id(self, user_id):
        if not User.query.get(user_id.data):
            raise ValidationError('Пользователя с таким id не существует')
    def validate_advert_id(self, advert_id):
        if not Advert.query.get(advert_id.data):
            raise ValidationError('Объявления с таким id не существует')


