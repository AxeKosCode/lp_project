from webapp import create_app
from webapp.advert.parsers.avito import get_adverts_snippets, get_adverts_content

app = create_app()
with app.app_context():
    # get_adverts_snippets()
    get_adverts_content()

