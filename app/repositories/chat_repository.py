from pydantic_mongo import AbstractRepository

from app.models.chat import Chat


class ChatRepository(AbstractRepository[Chat]):
    class Meta:
        collection_name = "chats"
