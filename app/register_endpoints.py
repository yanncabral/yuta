from flask import Flask

from app.controllers.devices_controller import devices_controller
from app.views.devices_view import devices_view


def register_endpoints(app: Flask):
    app.register_api(devices_controller)
    app.register_api(devices_view)
