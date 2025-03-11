from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from db.mysql import db
from keyboards.inline import get_summary_keyboard
from config import WEBAPP_URL

router = Router()

@router.message(Command("in"))
async def record_income(message: Message):
    if not message.reply_to_message:
        await message.reply("请回复用户消息进行入款记录")
        return
        
    try:
        # 解析金额
        amount = float(message.text.split()[1])
        if amount <= 0:
            await message.reply("金额必须大于0")
            return
    except (IndexError, ValueError):
        await message.reply("格式错误，请使用 /in 金额")
        return
        
    target_user = message.reply_to_message.from_user
    
    # 记录交易
    await db.execute(
        """INSERT INTO transactions 
        (group_id, user_id, username, amount, transaction_type, operator_id, operator_name) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        message.chat.id, target_user.id, target_user.username or target_user.first_name,
        amount, "入款", message.from_user.id, message.from_user.username or message.from_user.first_name
    )
    
    # 获取交易摘要
    await send_transaction_summary(message.chat.id, message)

@router.message(Command("out"))
async def record_expense(message: Message):
    if not message.reply_to_message:
        await message.reply("请回复用户消息进行出款记录")
        return
        
    try:
        # 解析金额
        amount = float(message.text.split()[1])
        if amount <= 0:
            await message.reply("金额必须大于0")
            return
    except (IndexError, ValueError):
        await message.reply("格式错误，请使用 /out 金额")
        return
        
    target_user = message.reply_to_message.from_user
    
    # 记录交易
    await db.execute(
        """INSERT INTO transactions 
        (group_id, user_id, username, amount, transaction_type, operator_id, operator_name) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        message.chat.id, target_user.id, target_user.username or target_user.first_name,
        amount, "出款", message.from_user.id, message.from_user.username or message.from_user.first_name
    )
    
    # 获取交易摘要
    await send_transaction_summary(message.chat.id, message)

async def send_transaction_summary(group_id, message):
    # 获取入款统计
    income_count = await db.fetch_one(
        "SELECT COUNT(*) as count FROM transactions WHERE group_id = %s AND transaction_type = '入款'",
        group_id
    )
    
    # 获取出款统计
    expense_count = await db.fetch_one(
        "SELECT COUNT(*) as count FROM transactions WHERE group_id = %s AND transaction_type = '出款'",
        group_id
    )
    
    # 获取最近5笔交易
    recent_transactions = await db.fetch_all(
        """SELECT username, amount, transaction_type, created_at 
        FROM transactions 
        WHERE group_id = %s 
        ORDER BY created_at DESC 
        LIMIT 5""",
        group_id
    )
    
    # 计算总额
    total_income = await db.fetch_one(
        "SELECT SUM(amount) as total FROM transactions WHERE group_id = %s AND transaction_type = '入款'",
        group_id
    )
    
    total_expense = await db.fetch_one(
        "SELECT SUM(amount) as total FROM transactions WHERE group_id = %s AND transaction_type = '出款'",
        group_id
    )
    
    # 构建消息文本
    text = f"全能记账机器人\n\n"
    text += f"入款({income_count['count']} 笔):\n"
    
    income_transactions = [t for t in recent_transactions if t['transaction_type'] == '入款']
    if income_transactions:
        for t in income_transactions[:5]:
            time_str = t['created_at'].strftime("%H:%M:%S")
            text += f"{time_str} {t['amount']} {t['username']}\n"
    
    text += f"\n出款({expense_count['count']} 笔):\n"
    
    expense_transactions = [t for t in recent_transactions if t['transaction_type'] == '出款']
    if expense_transactions:
        for t in expense_transactions[:5]:
            time_str = t['created_at'].strftime("%H:%M:%S")
            text += f"{time_str} {t['amount']} {t['username']}\n"
    
    text += f"\n总入款: {total_income['total'] or 0}\n"
    text += f"总出款: {total_expense['total'] or 0}\n"
    text += f"余额: {(total_income['total'] or 0) - (total_expense['total'] or 0)}"
    
    # 发送消息
    keyboard = get_summary_keyboard(group_id)
    await message.reply(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("view_all:"))
async def view_all_transactions(callback: CallbackQuery):
    group_id = callback.data.split(":")[1]
    url = f"{WEBAPP_URL}/transactions/{group_id}"
    await callback.answer(f"打开完整账单", url=url)
