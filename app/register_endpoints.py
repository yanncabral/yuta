from flask import Flask

from app.controllers.devices_controller import devices_controller
from app.views.devices_view import devices_bp
from app.views.chat_view import chat_bp


def register_endpoints(app: Flask):
    app.register_api(devices_controller)
    app.register_blueprint(devices_bp)
    app.register_blueprint(chat_bp)
