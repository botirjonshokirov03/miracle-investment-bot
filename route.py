# route.py
from client.routes.client_routes import client_routes
from admin.routes.admin_routes import admin_routes

def setup_routes(application):
    for handler in  admin_routes + client_routes:
        application.add_handler(handler)
