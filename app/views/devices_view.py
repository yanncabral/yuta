from flask import render_template
from flask import Blueprint

devices_bp = Blueprint("devices_bp", __name__)


@devices_bp.route("/devices/add")
def add_device():
    return render_template("devices/add_device.html")


@devices_bp.route("/devices/")
def list_devices():
    return render_template(
        "devices/list_devices.html",
        devices_data=[
            [
                "1",
                "Sensor",
                "Sensor de temperatura",
                [1, 2, 3],
            ]
        ],
    )