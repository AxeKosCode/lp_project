from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from webapp.advert.models import Advert


class CommentForm(FlaskForm):
    advert_id = HiddenField('ID объявления', validators=[DataRequired()])
    comment_text = StringField('Ваш комментарий', validators=[DataRequired()], render_kw={"class": "form-control"})
    submit = SubmitField('Отправить!',render_kw={"class": "btn btn-primary"})

    def validate_advert_id(self, advert_id):
        if not Advert.query.get(advert_id.data):
            raise ValidationError('Объявления с таким id не существует')

