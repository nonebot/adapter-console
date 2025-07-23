<p align="center">
  <a href="https://nonebot.dev/"><img src="https://raw.githubusercontent.com/nonebot/adapter-console/master/assets/logo.png" width="200" alt="nonebot-adapter-console"></a>
</p>

<div align="center">

# NoneBot-Adapter-Console

_✨ Console 适配 ✨_

</div>

## 配置

修改 NoneBot 配置文件 `.env` 或者 `.env.*`。

### Driver

参考 [driver](https://nonebot.dev/docs/appendices/config#driver) 配置项，直接使用 `None` 驱动器：

```dotenv
DRIVER=~none
```

### console_bot_id

配置 Bot 的 ID, 默认为 `robot`

### console_bot_name

配置 Bot 的名称, 默认为 `Bot`

### console_strict_tome

配置是否使用严格的 `ToMe` 规则。默认为 `False`。

启用后，在群聊中发送的消息需要增加 `@{bot_id}` 才能满足 `ToMe` 的条件。

## 示例

```python
from nonebot import on_command
from nonebot.adapters.console import Bot
from nonebot.adapters.console.event import MessageEvent
from nonebot.adapters.console.message import MessageSegment


matcher = on_command("test")

@matcher.handle()
async def handle_receive(bot: Bot, event: MessageEvent):
      await bot.send(event, MessageSegment.text("Hello, world!"))
```
