from flask import render_template
from flask_openapi3 import APIView, Tag

devices_view = APIView(view_tags=[Tag(name="Devices")])


@devices_view.route("/devices/add")
def add_device_view():
    return render_template("devices/add_device.html")
