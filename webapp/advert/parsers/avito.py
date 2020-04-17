from webapp.advert.models import Advert
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import locale
import platform

from webapp.db import db
from webapp.advert.models import Advert
from webapp.advert.parsers.utils import get_html, save_adverts



if platform.system()=='Windows':
    locale.setlocale(locale.LC_ALL, 'russian')
else:
    locale.setlocale(locale.LC_TIME, 'ru_RU.utf-8')

def parse_avito_date(date_str):
    return datetime.strptime('20 '+date_str, "%y %d %B %H:%M")

def get_adverts_snippets():
    html = get_html('https://www.avito.ru/sankt-peterburg/muzykalnye_instrumenty/gitary_i_drugie_strunnye-ASgBAgICAUTEAsYK')
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        all_adverts = soup.find('div', class_="snippet-list js-catalog_serp").findAll('div', class_="description item_table-description", limit=10)
        result_adverts = []
        for advert in all_adverts:
            title = advert.find('a', class_='snippet-link').text
            url = 'https://www.avito.ru' + advert.find('a', class_='snippet-link')['href']
            price = advert.find('span', class_='snippet-price').text.strip()
            published = advert.find('div', class_="snippet-date-info")['data-tooltip']
            try:
                published = parse_avito_date(published)
            except ValueError:
                pass
            save_adverts(title, url, price, published)

def get_adverts_content():
    advert_without_text = Advert.query.filter(Advert.text.is_(None))
    for advert in advert_without_text:
        html = get_html(advert.url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            advert_text = soup.find('div', class_="item-view-content").decode_contents()
            if advert_text:
                advert.text = advert_text
                db.session.add(advert)
                db.session.commit()

