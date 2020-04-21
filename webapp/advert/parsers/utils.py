import requests
from webapp.db import db
from webapp.advert.models import Advert

headers = {
    'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0'
}

def get_html(url):
    try:
        result = requests.get(url, headers=headers)
        result.raise_for_status()
        return result.text
    except(requests.RequestException, ValueError):
        print("Сетевая ошибка")
        return False


def save_adverts(title, url, price, published):
    adverts_exists = Advert.query.filter(Advert.url == url).count()
    if not adverts_exists:
        new_advert = Advert(title=title, url=url, price=price, published=published)
        db.session.add(new_advert)
        db.session.commit()
