from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from db.mysql import db

router = Router()

@router.message(Command("add_operator"))
async def add_operator(message: Message):
    if not message.reply_to_message:
        await message.reply("请回复要添加为操作员的用户消息")
        return
        
    target_user = message.reply_to_message.from_user
    
    # 检查群组是否已注册
    group = await db.fetch_one("SELECT 1 FROM groups WHERE group_id = %s", message.chat.id)
    if not group:
        await db.execute(
            "INSERT INTO groups (group_id, group_name) VALUES (%s, %s)",
            message.chat.id, message.chat.title
        )
    
    # 添加操作员
    try:
        await db.execute(
            "INSERT INTO operators (group_id, user_id, username) VALUES (%s, %s, %s)",
            message.chat.id, target_user.id, target_user.username or target_user.first_name
        )
        await message.reply(f"已将 {target_user.username or target_user.first_name} 添加为操作员")
    except Exception:
        await message.reply(f"{target_user.username or target_user.first_name} 已经是操作员")

@router.message(Command("remove_operator"))
async def remove_operator(message: Message):
    if not message.reply_to_message:
        await message.reply("请回复要移除操作员权限的用户消息")
        return
        
    target_user = message.reply_to_message.from_user
    
    # 移除操作员
    result = await db.execute(
        "DELETE FROM operators WHERE group_id = %s AND user_id = %s",
        message.chat.id, target_user.id
    )
    
    if result:
        await message.reply(f"已移除 {target_user.username or target_user.first_name} 的操作员权限")
    else:
        await message.reply(f"{target_user.username or target_user.first_name} 不是操作员")

@router.message(Command("list_operators"))
async def list_operators(message: Message):
    operators = await db.fetch_all(
        "SELECT user_id, username FROM operators WHERE group_id = %s",
        message.chat.id
    )
    
    if not operators:
        await message.reply("当前群组没有设置操作员")
        return
        
    text = "当前群组的操作员:\n"
    for i, op in enumerate(operators, 1):
        text += f"{i}. {op['username']} (ID: {op['user_id']})\n"
        
    await message.reply(text)
