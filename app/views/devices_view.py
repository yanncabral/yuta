from typing import Optional

from flask import Blueprint, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from pydantic import BaseModel
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired, Length

from app.database import database
from app.models.device import Device, DeviceType
from app.repositories.devices_repository import DevicesRepository

devices_bp = Blueprint("devices_bp", __name__)


class AddDeviceForm(FlaskForm):
    name = StringField(
        "Nome", validators=[DataRequired(), Length(min=3, max=20, message="Deve ter entre 3 e 20 caracteres")]
    )
    device_type = SelectField(
        "Tipo de dispositivo",
        choices=[(device_type.value, DeviceType.label(device_type)) for device_type in DeviceType],
    )
    pins = SelectField("pins")


class Pin(BaseModel):
    id: int
    device_name: Optional[str]
    is_free: bool


@devices_bp.route("/devices/add", methods=["GET", "POST"])
def add_device():
    repository = DevicesRepository(database=database)
    devices = list(repository.find_by({}))

    print(devices)

    pins_list = []
    for device in devices:
        for pin in device.pins:
            pins_list.append(Pin(id=pin, device_name=device.name if device.name else None, is_free=False))

    all_pins = set(range(1, 11))
    used_pins = {pin.id for pin in pins_list}
    free_pins = all_pins - used_pins

    for pin in free_pins:
        pins_list.append(Pin(id=pin, device_name=None, is_free=True))

    pins_list = pins_list[:10]

    pins_list = sorted(pins_list, key=lambda x: x.id)

    form = AddDeviceForm()

    form.pins.choices = [(str(pin.id), str(pin.id)) for pin in pins_list]

    if request.method == "POST" and form.validate_on_submit():
        device = Device(name=form.name.data, type=form.device_type.data, pins=request.form.getlist("pins"))
        repository.save(device)

        return redirect(url_for("devices_bp.list_devices"))

    return render_template("devices/add_device.html", form=form, pins_list=pins_list)


@devices_bp.route("/devices/")
def list_devices():
    repository = DevicesRepository(database=database)

    devices = list(repository.find_by({}))

    def dto(self: Device):
        return [self.id, self.type.value, self.name, self.pins]

    return render_template(
        "devices/list_devices.html",
        devices_data=[dto(device) for device in devices],
    )
