from flask import Blueprint, render_template

devices_bp = Blueprint("devices", __name__, url_prefix="/devices")


@devices_bp.route("/add", methods=["GET"])
def add_device():
    return render_template("devices/add_device.html")
