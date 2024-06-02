from flask import Response
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel

from app.database import database
from app.models.device import Device
from app.repositories.devices_repository import DevicesRepository

devices_controller = APIBlueprint("devices", __name__, url_prefix="/api/devices")


class DevicesResponse(BaseModel):
    devices: list[Device]


devices_tag = Tag(name="Devices")


@devices_controller.get("/", tags=[devices_tag], responses={200: DevicesResponse})
def devices_list():
    """List devices for the authenticated user"""
    repository = DevicesRepository(database=database)
    devices = list(repository.find_by({}))

    print(devices)

    response = DevicesResponse(devices=devices).json()
    return Response(
        status=200,
        response=response,
        content_type="application/json",
    )
