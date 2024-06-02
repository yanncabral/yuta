from pydantic_mongo import AbstractRepository

from app.models.device import Device


class DevicesRepository(AbstractRepository[Device]):
    class Meta:
        collection_name = "devices"
