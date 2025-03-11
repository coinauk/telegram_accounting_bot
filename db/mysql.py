import aiomysql
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

class Database:
    def __init__(self):
        self.pool = None

    async def create_pool(self):
        self.pool = await aiomysql.create_pool(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            db=MYSQL_DB,
            autocommit=True
        )
        
    async def execute(self, query, *args):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, args)
                return cursor.lastrowid
                
    async def fetch_all(self, query, *args):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, args)
                return await cursor.fetchall()
                
    async def fetch_one(self, query, *args):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, args)
                return await cursor.fetchone()
                
    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

db = Database()
