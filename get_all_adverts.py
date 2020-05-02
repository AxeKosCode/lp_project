from webapp import create_app
from webapp.advert.parsers.avito import get_adverts_snippets, get_adverts_content

app = create_app()
url = 'https://www.avito.ru/sankt-peterburg/muzykalnye_instrumenty/gitary_i_drugie_strunnye-ASgBAgICAUTEAsYK?p='

p = 2 # УКАЗЫВАЕМ, СКОЛЬКО СТРАНИЦ ПАРСИТЬ

with app.app_context():
    # for page in range(2, p+1):
    #     url_search = url + str(page)
    #     print(f'ПАРСИТСЯ СТРАНИЦА № {page}')
        
    get_adverts_snippets()#url_search)
    get_adverts_content()

