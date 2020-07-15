from aiohttp.web import Application
from endpoints.users import users_get, users_post, users_login_get, users_put, users_delete


def setup_routes(app: Application):
    app.router.add_get('/users', users_get, name='users')
    app.router.add_get('/users/{login}', users_login_get, name='users_login')
    app.router.add_post('/users', users_post, name='users_create')
    app.router.add_put('/users/{login}', users_put, name='users_update')
    app.router.add_delete('/users/{login}', users_delete, name='users_delete')
