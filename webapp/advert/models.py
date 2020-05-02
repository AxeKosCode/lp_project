from webapp.db import db
from datetime import datetime
from sqlalchemy.orm import relationship


class Advert(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    theme = db.Column(db.String, nullable = True)
    url = db.Column(db.String, unique = True, nullable = False)
    price = db.Column(db.Float, nullable = True)
    published = db.Column(db.DateTime, nullable = False)
    description = db.Column(db.Text, nullable = True)
    address = db.Column(db.Text, nullable = True)
    seller = db.Column(db.String, nullable = True)
    company = db.Column(db.Boolean, nullable = True)
    phone = db.Column(db.Text, nullable = True)
    foto = db.Column(db.Integer, nullable = True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable = True,
        index=True
    )
    closed = db.Column(db.Boolean, default = False)
    fail_check = db.Column(db.Integer, default = 0)

    def comments_count(self):
        return Comment.query.filter(Comment.advert_id == self.id).count()

    def __repr__(self):
        return f'<Advert {self.title} {self.url}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.Text, nullable = False)
    created = db.Column(db.DateTime, nullable = False, default=datetime.now())
    advert_id = db.Column(
        db.Integer,
        db.ForeignKey('advert.id', ondelete='CASCADE'),
        index=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        index=True
    )
    advert = relationship("Advert", backref='comments')
    user = relationship("User", backref='comments')

    def __repr__(self):
        return f'<Comment {self.id}>'
