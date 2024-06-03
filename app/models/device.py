from typing import Literal, Optional

from pydantic import BaseModel
from pydantic_mongo import PydanticObjectId


class Device(BaseModel):
    id: Optional[PydanticObjectId] = None
    name: str
    type: Literal["fan", "door", "motion-sensor", "led", "rgb", "motion-sensor"]
    pin: int
