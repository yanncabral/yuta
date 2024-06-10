from typing import Optional

from bson import ObjectId
from flask import Blueprint, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from pydantic import BaseModel
from wtforms import SelectField, SelectMultipleField, StringField
from wtforms.validators import DataRequired, Length

from app.database import database
from app.models.device import Device, DeviceType
from app.repositories.devices_repository import DevicesRepository

devices_bp = Blueprint("devices_bp", __name__)


class AddDeviceForm(FlaskForm):
    name = StringField(
        "Nome",
        validators=[
            DataRequired(message="Campo obrigatório"),
            Length(min=3, max=20, message="Deve ter entre 3 e 20 caracteres"),
        ],
    )
    device_type = SelectField(
        "Tipo de dispositivo",
        choices=[(device_type.value, DeviceType.label(device_type)) for device_type in DeviceType],
    )
    pins = SelectMultipleField(
        "pins",
        coerce=int,
        validators=[DataRequired(message="Escolha pelo menos 1 pin")],
    )


class Pin(BaseModel):
    id: int
    device_name: Optional[str]
    is_free: bool


def _build_pins_list(devices: list[Device]) -> list[Pin]:
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

    return pins_list


@devices_bp.route("/devices/add", methods=["GET", "POST"])
def add_device():
    repository = DevicesRepository(database=database)
    devices = list(repository.find_by({}))

    pins_list = _build_pins_list(devices)

    form = AddDeviceForm()

    form.pins.choices = [(str(pin.id), str(pin.id)) for pin in pins_list]

    if request.method == "POST" and form.validate_on_submit():
        pins_count = DeviceType.pin_count(form.device_type.data)
        if len(form.pins.data) != pins_count:
            form.pins.errors.append(
                f"O dispositivo do tipo {DeviceType.label(form.device_type.data)} requer exatamente {pins_count} pino(s)."
            )
            return render_template("devices/add_device.html", form=form, pins_list=pins_list)

        device = Device(name=form.name.data, type=form.device_type.data, pins=form.pins.data)
        repository.save(device)

        return redirect(url_for("devices_bp.list_devices"))

    return render_template("devices/add_device.html", form=form, pins_list=pins_list)


@devices_bp.route("/devices/")
def list_devices():
    repository = DevicesRepository(database=database)

    devices = list(repository.find_by({}))

    def dto(device: Device):
        return [device.id, DeviceType.label(device.type), device.name, ", ".join([str(pin) for pin in device.pins])]

    return render_template(
        "devices/list_devices.html",
        devices_data=[dto(device) for device in devices],
    )


@devices_bp.route("/devices/edit/<device_id>", methods=["GET", "POST"])
def edit_device(device_id: str):
    repository = DevicesRepository(database=database)

    devices = list(repository.find_by({}))

    def dto(device: Device):
        return [device.id, DeviceType.label(device.type), device.name, ", ".join([str(pin) for pin in device.pins])]

    return render_template(
        "devices/list_devices.html",
        devices_data=[dto(device) for device in devices],
    )


@devices_bp.route("/devices/delete/<device_id>", methods=["GET", "POST"])
def delete_device(device_id: str):
    repository = DevicesRepository(database=database)
    repository.delete_by_id(ObjectId(device_id))

    return redirect(url_for("devices_bp.list_devices"))
