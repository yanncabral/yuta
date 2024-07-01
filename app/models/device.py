from enum import Enum
from typing import List, Optional

from pydantic import BaseModel
from pydantic_mongo import PydanticObjectId


class DeviceType(str, Enum):
    fan = "fan"
    door = "door"
    motion_sensor = "motion-sensor"
    led = "led"
    rgb = "rgb"
    buzzer = "buzzer"
    light_sensor = "sensor_luz"

    @staticmethod
    def pin_count(device_type: "DeviceType") -> int:
        pin_mapping = {
            DeviceType.fan: 1,
            DeviceType.door: 2,
            DeviceType.motion_sensor: 1,
            DeviceType.led: 1,
            DeviceType.rgb: 3,
            DeviceType.buzzer: 1,
            DeviceType.light_sensor: 1,
        }

        return pin_mapping[device_type]

    @staticmethod
    def label(device_type: "DeviceType") -> str:
        name_mapping = {
            DeviceType.fan: "Ventilador",
            DeviceType.door: "Porta",
            DeviceType.motion_sensor: "Sensor de movimento",
            DeviceType.led: "LED",
            DeviceType.rgb: "LED RGB",
            DeviceType.buzzer: "Campainha",
            DeviceType.light_sensor: "Sensor de luz",
        }

        return name_mapping[device_type]


class PinType(str, Enum):
    digital = "digital"
    analog = "analog"

    @staticmethod
    def label(pin_type: "PinType") -> str:
        name_mapping = {
            PinType.digital: "Digital",
            PinType.analog: "Analógico",
        }

        return name_mapping[pin_type]


class Device(BaseModel):
    id: Optional[PydanticObjectId] = None
    name: str
    type: DeviceType
    digital_pins: List[int]
    analogic_pins: List[int]
    pins_type: PinType
