from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Dict, Any, Callable, Awaitable
from db.mysql import db

class OperatorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # 检查是否为群组消息
        if not event.chat.type in ["group", "supergroup"]:
            return await handler(event, data)
            
        # 检查命令是否需要操作员权限
        if event.text and event.text.startswith(('/add_operator', '/remove_operator', '/list_operators')):
            # 管理员命令，检查是否为群组管理员
            chat_member = await event.bot.get_chat_member(event.chat.id, event.from_user.id)
            if chat_member.status in ["creator", "administrator"]:
                data["is_admin"] = True
                return await handler(event, data)
            else:
                await event.reply("只有群组管理员可以执行此命令")
                return None
                
        # 检查记账相关命令是否由操作员发出
        if event.text and event.text.startswith(('/in', '/out')):
            is_operator = await db.fetch_one(
                "SELECT 1 FROM operators WHERE group_id = %s AND user_id = %s",
                event.chat.id, event.from_user.id
            )
            
            if is_operator:
                data["is_operator"] = True
                return await handler(event, data)
            else:
                await event.reply("只有操作员可以执行记账操作")
                return None
                
        return await handler(event, data)
