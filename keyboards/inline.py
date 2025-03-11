from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_summary_keyboard(group_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="完整账单", callback_data=f"view_all:{group_id}"),
                InlineKeyboardButton(text="使用说明", callback_data="help")
            ]
        ]
    )
    return keyboard
