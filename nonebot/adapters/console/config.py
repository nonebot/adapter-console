from pydantic import BaseModel


class BaseInfo(BaseModel):
    nickname: str
    user_id: str
    color: str = "green"


class BotConfig(BaseInfo):
    nickname: str = "TestBot"
    color: str = "blue"


class UserInfo(BaseInfo):
    ...
