from typing import Optional

from bson import ObjectId
from flask import Blueprint, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from pydantic import BaseModel
from wtforms import SelectField, SelectMultipleField, StringField
from wtforms.validators import DataRequired, Length

from app.database import database
from app.models.device import Device, DeviceType, PinType
from app.repositories.devices_repository import DevicesRepository

devices_bp = Blueprint("devices_bp", __name__)

_number_of_digital_pins = 21
_number_of_analog_pins = 16


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
    digital_pins = SelectMultipleField(
        "Pinos Digitais",
        coerce=int,
        default=[],
    )
    analog_pins = SelectMultipleField("Pinos Analógicos", coerce=int, default=[])
    pins_type = SelectField(
        "Tipo de pin",
        choices=[(pin_type.value, PinType.label(pin_type)) for pin_type in PinType],
    )

    def validate(self, extra_validators):
        if not super().validate():
            return False

        if self.pins_type.data == "digital" and not self.digital_pins.data:
            self.digital_pins.errors.append("Escolha pelo menos 1 pin digital.")
            return False

        if self.pins_type.data == "analogico" and not self.analog_pins.data:
            self.analog_pins.errors.append("Escolha pelo menos 1 pin analógico.")
            return False

        return True


class Pin(BaseModel):
    id: int
    device_name: Optional[str]
    is_free: bool


def _build_pins_list(devices: list[Device], current_device: Optional[Device] = None) -> (list[Pin], list[Pin]):
    digital_pins_list = []
    analog_pins_list = []

    for device in devices:
        if current_device and device.id == current_device.id:
            continue

        for pin in device.digital_pins:
            digital_pins_list.append(Pin(id=pin, device_name=device.name if device.name else None, is_free=False))

        for pin in device.analogic_pins:
            analog_pins_list.append(Pin(id=pin, device_name=device.name if device.name else None, is_free=False))

    all_digital_pins = set(range(1, _number_of_digital_pins + 1))
    all_analog_pins = set(range(1, _number_of_analog_pins + 1))

    used_digital_pins = {pin.id for pin in digital_pins_list}
    used_analog_pins = {pin.id for pin in analog_pins_list}

    free_digital_pins = all_digital_pins - used_digital_pins
    free_analog_pins = all_analog_pins - used_analog_pins

    for pin in free_digital_pins:
        digital_pins_list.append(Pin(id=pin, device_name=None, is_free=True))

    for pin in free_analog_pins:
        analog_pins_list.append(Pin(id=pin, device_name=None, is_free=True))

    digital_pins_list = sorted(digital_pins_list, key=lambda x: x.id)
    analog_pins_list = sorted(analog_pins_list, key=lambda x: x.id)

    return digital_pins_list, analog_pins_list


@devices_bp.route("/devices/add", methods=["GET", "POST"])
def add_device():
    repository = DevicesRepository(database=database)
    devices = list(repository.find_by({}))

    digital_pins_list, analog_pins_list = _build_pins_list(devices)

    form = AddDeviceForm()

    form.digital_pins.choices = [(str(pin.id), str(pin.id)) for pin in digital_pins_list]
    form.analog_pins.choices = [(str(pin.id), str(pin.id)) for pin in analog_pins_list]

    if request.method == "POST" and form.validate_on_submit():
        pins_count = DeviceType.pin_count(form.device_type.data)
        if form.pins_type.data == "digital" and len(form.digital_pins.data) != pins_count:
            form.digital_pins.errors.append(
                f"O dispositivo do tipo {DeviceType.label(form.device_type.data)} requer exatamente {pins_count} pino(s)."
            )

            return render_template(
                "devices/add_device_page.html",
                form=form,
                pins_type=form.pins_type.data,
                digital_pins_list=digital_pins_list,
                analog_pins_list=analog_pins_list,
            )
        elif form.pins_type.data == "analogico" and len(form.analog_pins.data) != pins_count:
            form.analog_pins.errors.append(
                f"O dispositivo do tipo {DeviceType.label(form.device_type.data)} requer exatamente {pins_count} pino(s)."
            )

            return render_template(
                "devices/add_device_page.html",
                form=form,
                pins_type=form.pins_type.data,
                digital_pins_list=digital_pins_list,
                analog_pins_list=analog_pins_list,
            )

        device = Device(
            name=form.name.data,
            type=form.device_type.data,
            digital_pins=form.digital_pins.data if form.pins_type.data == PinType.digital else [],
            analogic_pins=form.analog_pins.data if form.pins_type.data == PinType.analog else [],
            pins_type=form.pins_type.data,
        )

        repository.save(device)

        return redirect(url_for("devices_bp.list_devices"))

    return render_template(
        "devices/add_device_page.html",
        form=form,
        digital_pins_list=digital_pins_list,
        analog_pins_list=analog_pins_list,
    )


@devices_bp.route("/devices/")
def list_devices():
    repository = DevicesRepository(database=database)

    devices = list(repository.find_by({}))

    def dto(device: Device):
        pins = device.digital_pins if device.pins_type == PinType.digital else device.analogic_pins
        return [
            device.id,
            DeviceType.label(device.type),
            device.name,
            ", ".join([str(pin) for pin in pins]),
            PinType.label(device.pins_type),
        ]

    return render_template(
        "devices/list_devices_page.html",
        devices_data=[dto(device) for device in devices],
    )


@devices_bp.route("/devices/edit/<device_id>", methods=["GET", "POST"])
def edit_device(device_id: str):
    repository = DevicesRepository(database=database)
    device = repository.find_one_by_id(ObjectId(device_id))

    if not device:
        return redirect(url_for("devices_bp.list_devices"))

    devices = list(repository.find_by({}))
    digital_pins_list, analog_pins_list = _build_pins_list(devices, device)

    form = AddDeviceForm()

    form.digital_pins.choices = [(str(pin.id), str(pin.id)) for pin in digital_pins_list]
    form.analog_pins.choices = [(str(pin.id), str(pin.id)) for pin in analog_pins_list]

    if request.method == "POST" and form.validate_on_submit():
        pins_count = DeviceType.pin_count(form.device_type.data)
        if form.pins_type.data == "digital" and len(form.digital_pins.data) != pins_count:
            form.digital_pins.errors.append(
                f"O dispositivo do tipo {DeviceType.label(form.device_type.data)} requer exatamente {pins_count} pino(s)."
            )
            return render_template(
                "devices/edit_device_page.html",
                device=device,
                form=form,
                digital_pins_list=digital_pins_list,
                analog_pins_list=analog_pins_list,
            )

        elif form.pins_type.data == "analogico" and len(form.analog_pins.data) != pins_count:
            form.analog_pins.errors.append(
                f"O dispositivo do tipo {DeviceType.label(form.device_type.data)} requer exatamente {pins_count} pino(s)."
            )
            return render_template(
                "devices/edit_device_page.html",
                device=device,
                form=form,
                digital_pins_list=digital_pins_list,
                analog_pins_list=analog_pins_list,
            )

        device.name = form.name.data
        device.type = form.device_type.data
        device.digital_pins = form.digital_pins.data if form.pins_type.data == PinType.digital else []
        device.analogic_pins = form.analog_pins.data if form.pins_type.data == PinType.analog else []
        device.pins_type = form.pins_type.data

        repository.save(device)

        return redirect(url_for("devices_bp.list_devices"))

    return render_template(
        "devices/edit_device_page.html",
        device=device,
        form=form,
        digital_pins_list=digital_pins_list,
        analog_pins_list=analog_pins_list,
    )


@devices_bp.route("/devices/delete/<device_id>", methods=["GET", "POST"])
def delete_device(device_id: str):
    repository = DevicesRepository(database=database)
    repository.delete_by_id(ObjectId(device_id))

    return redirect(url_for("devices_bp.list_devices"))
