from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId


class ChatMessage(BaseModel):
    id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId)
    content: str
    role: Literal["user", "assistant"]
    created_at: datetime = Field(default_factory=datetime.now)


class Chat(BaseModel):
    id: Optional[PydanticObjectId] = None
    messages: List[ChatMessage]
