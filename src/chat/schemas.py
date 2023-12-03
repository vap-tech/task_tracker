from pydantic import BaseModel


class MessagesModel(BaseModel):
    id: int
    message: str

    class ConfigDict:
        from_attributes = True
