from flask import render_template
from flask_openapi3 import APIView, Tag

devices_view = APIView(view_tags=[Tag(name="Devices")])


@devices_view.route("/devices/add")
class AddDeviceView:
    def get(self):
        return render_template("devices/add_device.html")
