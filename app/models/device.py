from typing import Literal, Optional

from pydantic import BaseModel
from pydantic_mongo import PydanticObjectId


class Device(BaseModel):
    id: Optional[PydanticObjectId] = None
    name: str
    type: Literal["lamp", "fan", "door", "motion-sensor"]
    pin: int
