from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from flask import url_for
import locale
import platform
import requests
import os

from webapp.advert.parsers.utils import get_html, log_img_errors, verify_existence, save_adverts, save_foto_links
from webapp.advert.models import Advert
from webapp.db import db

prefix = 'https:'
# start_lists = ('l', 'm', 's')


if platform.system()=='Windows':
    locale.setlocale(locale.LC_ALL, 'russian')
else:
    locale.setlocale(locale.LC_TIME, 'ru_RU.utf-8')


def parse_avito_date(date_str):
    try:
        return datetime.strptime('20 '+date_str, "%y %d %B %H:%M")
    except ValueError:
        return datetime.now()

def foto_links(list_of_divs, result_list):
    if not 's' in result_list:
        for div in list_of_divs:
            try:
                link = div['data-url']
            except KeyError:
                link = ''
            if 'video' in link:
                continue
            result_list.append(prefix + link)
    else:
        for div in list_of_divs:
            try:
                link = div.img['src']
            except (AttributeError, KeyError):
                link = ''
            if 'video' in link:
                continue
            result_list.append(prefix + link)



def download_imgs(list_of_links, current_path):
    '''
    Функция создаёт каталоги, скачивает изображения по данным ссылкам 
    и сохраняет их в виде файлов в созданных каталогах.
    INPUT: список ссылок на изображения, id объявления
    OUTPUT: None
    '''
    try:
        path = current_path + list_of_links[0] + '/' #url_for('static')
        print(path)#######################
        # return False######################
    except (TypeError, IndexError):
        print('Ошибка создания пути для каталога. Сбор данных прерван')
        return False
    try:
        if not os.path.isdir(path):
            print('Каталога по адресу', path, 'не существует')
            os.makedirs(path)
            print('Но теперь', path, 'успешно создан!')
        else:
            print('Каталог', path, 'уже есть. Будем сохранять в него!')
    except OSError:
        print('Ошибка создания каталога. Сбор данных прерван')
        return False

    for c, link in enumerate(list_of_links[1:], 1):
        try:
            filename = str(c)+'.'+link.split('.')[-1]
        except IndexError:
            filename = str(c)+'.jpg'

        response = get_html(link)#requests.get(link)

        try:
            if not os.path.exists(path+filename):
                f = open(path+filename, 'wb')
                f.write(response.content)
                print(f'Файл {filename} записан!')
                f.close()
            else:
                print(f'Файл {filename} уже существует!')
        except OSError:
            print(f'Ошибка создания файла {filename}')
    # сохраняем файл с линками фото
    save_foto_links(list_of_links, current_path)


def get_adverts_snippets():#url_search):
    url = 'https://www.avito.ru/sankt-peterburg/muzykalnye_instrumenty/gitary_i_drugie_strunnye-ASgBAgICAUTEAsYK'
    html = get_html(url)#(url_search)
    if html:
        soup = BeautifulSoup(html.text, 'html.parser')
        try:
            all_adverts = soup.find('div', class_="snippet-list js-catalog_serp").findAll('div', class_="description item_table-description", limit=3)
        except AttributeError:
            print('Что-то пошло не так. Парсинг откладывается')
            return
        for advert in all_adverts:
            try:
                url = 'https://www.avito.ru' + advert.find('a', class_='snippet-link')['href']
            except KeyError:
                print('-1 неудача =(')
                continue
            try:
                title = advert.find('a', class_='snippet-link').text
            except AttributeError:
                title = 'Объявление'
            if verify_existence(url):
                print('Это объявление уже есть в Базе ===', title)
                continue
            # try:
            #     price = advert.find('span', class_='snippet-price').text.strip()
            # except AttributeError:
            #     price = '0'
            try:
                published = advert.find('div', class_="snippet-date-info")['data-tooltip']
                published = parse_avito_date(published)
            except KeyError:
                published = datetime.now()
                print('Время публикации сброшено')

            save_adverts(title, url, published)


def get_adverts_content():
    advert_without_text = Advert.query.filter(Advert.description.is_(None), Advert.closed.is_(False)).all()#.filter(Advert.closed.is_(False)).all()
    print(f'Объявлений для сбора: {len(advert_without_text)}')
    if advert_without_text:
        print('Начинаем сбор данных')
    for advert in advert_without_text:
        print('___ №', advert.id)
        html = get_html(advert.url)
        if html:
            soup = BeautifulSoup(html.text, 'html.parser')

            if soup.findAll('span', class_='item-closed-warning__content') or \
                soup.find('div', class_='snippet-list js-catalog_serp'):
                advert.closed = True
                print('!!! Объявление уже закрыто !!!')
            else:
                try:
                    advert.theme = soup.findAll('a', class_='js-breadcrumbs-link-interaction')[-1]['title']
                except (IndexError, KeyError):
                    advert.theme = 'Объявления'
                try:
                    advert.title = soup.find('span', class_='title-info-title-text').text
                except AttributeError:
                    pass #advert.title = #'Подробности уточняйте у продавца'#advert.title
                try:
                    advert.price = float(soup.find('span', class_='js-item-price')['content'])
                except (KeyError, TypeError):
                    advert.price = 0
                try:
                    advert.description = soup.find('div', class_="item-description-text").decode_contents().strip()
                except AttributeError:
                    try:
                        advert.description = soup.find('div', class_="item-description-html").decode_contents().strip()
                    except AttributeError:
                        try:
                            advert.description = soup.find('div', class_="item-description").decode_contents().strip()
                        except AttributeError:
                            pass
                try:
                    advert.address = soup.find('div', class_='item-address').span.text.strip()
                    try:
                        georeferences = soup.findAll('span', class_='item-address-georeferences-item__content')
                        for geo in georeferences:
                            advert.address += ' | ' + geo.text
                    except AttributeError:
                        pass
                except AttributeError:
                    advert.address = 'Точный адрес уточняйте у продавца'
                try:
                    advert.seller = soup.find('div', class_='seller-info-name').text.strip()
                except AttributeError:
                    advert.seller = 'Продавец'
                try:
                    advert.company = (False if ("Частное лицо" in (soup.find('div', class_='seller-info-col').text)) else True)
                except AttributeError:
                    advert.company = None
                
                foto_l = soup.findAll('div', class_='js-gallery-extended-img-frame')
                foto_m = soup.findAll('div', class_='js-gallery-img-frame')
                foto_s = soup.findAll('div', class_='gallery-list-item-link')

                # prefix = 'https:'# перенесён наверх
                # start_lists
                #print('##### large в самом начале', large)
                large = ['l']
                middle = ['m']
                small = ['s']
                
                base_path = 'webapp/static/img/adv/'
                current_path = 'webapp/static/img/adv/' + str(advert.id) + '/' # +'webapp/advert/images/' 'images/'
                # current_path = '//img/adv/' + str(advert.id) + '/' # +'webapp/advert/images/' 'images/'
                # current_path = url_for('static', filename='') + 'img/adv/' + str(advert.id) + '/' # вылетает ошибка "RuntimeError: Application was not able to create a URL adapter for request independent URL generation. You might be able to fix this by setting the SERVER_NAME config variable."
                
                # foto_links(foto_l, large) # упрощено до цикла for (ниже)
                # foto_links(foto_m, middle)
                # foto_links(foto_s, small)
                for links_of_divs, result_list in (foto_l, large), \
                                                  (foto_m, middle), \
                                                  (foto_s, small):
                    foto_links(links_of_divs, result_list)

                for links in (large, middle, small):
                    download_imgs(links, current_path)
                
                print('_# Должно быть загружено по === ', len(large)-1, ' === файлов')
                # проверка соответствия количества фотографий между папками l, m, s
                check_foto = set()
                for d in 'lms':
                    try:
                        check_foto.add(len(os.listdir(current_path+d)))
                    except FileNotFoundError:
                        print(f'Каталог {d} отсутствует')
                if len(check_foto) == 1:
                    advert.foto = check_foto.pop()
                else:
                    # при несоответствии кол-ва заносим в Базу минимальное кол-во из всех, делаем пометку в файле
                    try:
                        advert.foto = min(check_foto)
                    except ValueError:
                        pass
                    error_string = ' - Разное количество изобр. по адресу ='+current_path
                    log_img_errors(error_string, base_path)
            
            db.session.add(advert)
            db.session.commit()
            print(f'<< {advert.title} >>\n  Сбор данных завершён\n')
        else:
            advert.fail_check += 1
            print('FAIL_CHECK +1\n')
