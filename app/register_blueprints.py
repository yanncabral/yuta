from flask import Flask

from app.endpoints.devices.devices_blueprint import devices_bp


def register_blueprints(app: Flask):
    app.register_blueprint(devices_bp)
