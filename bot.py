import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN, WEBAPP_HOST, WEBAPP_PORT
from db.mysql import db
from db.redis import redis
from middlewares.access import OperatorMiddleware
from handlers import admin, accounting
from web.app import app
import uvicorn

# 配置日志
logging.basicConfig(level=logging.INFO)

# 创建机器人实例
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# 创建调度器
dp = Dispatcher()

# 注册中间件
dp.message.middleware(OperatorMiddleware())

# 注册路由
dp.include_router(admin.router)
dp.include_router(accounting.router)

# 启动函数
async def main():
    # 初始化数据库连接
    await db.create_pool()
    await redis.create_connection()
    
    # 启动机器人
    await dp.start_polling(bot)

# 启动Web服务器
def run_webapp():
    uvicorn.run(app, host=WEBAPP_HOST, port=WEBAPP_PORT)

if __name__ == "__main__":
    # 在单独的线程中启动Web服务器
    import threading
    webapp_thread = threading.Thread(target=run_webapp)
    webapp_thread.start()
    
    # 启动机器人
    asyncio.run(main())
