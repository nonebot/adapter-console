from pydantic import BaseModel


class Config(BaseModel):
    console_headless_mode: bool = False
