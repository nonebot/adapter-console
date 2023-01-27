from pydantic import BaseModel

EMOJI = "😄😆😊😃😏😍😘😚😳😌😆😁😉😜😝😀😗😙😛😴😟😦😧😮😬😕😯😑😒😅😓😥😩😔😞😖😨😰😣😢😭😂😲😱😫😠😡😤😪😋😷😎😵👿😈😐😶😇👽💛"


class Config(BaseModel):
    console_headless_mode: bool = False
