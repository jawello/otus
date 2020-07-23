from aiohttp.web import Application
from endpoints.products import products_get, products_id_get, products_post, products_search


def setup_routes(app: Application):
    app.router.add_get('/products', products_get, name='products')
    app.router.add_get('/products/{id}', products_id_get, name='products_id')
    app.router.add_get('/products_search', products_search, name='products_search')
    app.router.add_post('/products', products_post, name='products_create')
