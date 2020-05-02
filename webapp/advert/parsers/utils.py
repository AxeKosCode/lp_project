import requests
from datetime import datetime
from flask import url_for
from webapp.db import db
from webapp.advert.models import Advert

headers = {
    'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0'
}

def get_html(url):
    try:
        result = requests.get(url, headers=headers)
        result.raise_for_status()
        return result#.text
    except(requests.RequestException, ValueError):
        print("Сетевая ошибка")
        return False

def verify_existence(url):
    return Advert.query.filter(Advert.url == url).count()


def save_adverts(title, url, published):
    # adverts_exists = Advert.query.filter(Advert.url == url).count()
    # if not adverts_exists:
    new_advert = Advert(title=title, url=url, published=published)
    db.session.add(new_advert)
    db.session.commit()
    print('+1 в Базу! ===', title)


def save_foto_links(list_links, path):
    try:
        file = open(path+'links.txt', 'a') #images/#url_for('static', filename='')
        for link in list_links:
            file.write(link+'\n')
        file.close()
    except OSError:
        print("Файл links.txt недоступен")


def log_img_errors(string, base_path):
    try:
        err = open(base_path+'img_errors.txt', 'a') #images/#'webapp/advert/images/'
        # err = open(url_for('static', filename='')+'img/adv/'+'img_errors.txt', 'a') #images/#'webapp/advert/images/'
        err.write(str(datetime.now())+string+'\n')
        err.close()
    except OSError:
        print("Файл img_errors.txt недоступен")
