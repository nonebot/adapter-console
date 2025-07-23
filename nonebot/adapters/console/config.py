from pydantic import BaseModel


class Config(BaseModel):
    console_headless_mode: bool = False
    console_bot_id: str = "robot"
    console_bot_name: str = "Bot"
    console_strict_tome: bool = False
