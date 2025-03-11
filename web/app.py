from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from db.mysql import db

app = FastAPI()

# 设置模板目录
templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)

# 设置静态文件目录
app.mount("/static", StaticFiles(directory="web/static"), name="static")

@app.get("/transactions/{group_id}", response_class=HTMLResponse)
async def get_transactions(request: Request, group_id: int):
    # 获取所有交易记录
    transactions = await db.fetch_all(
        """SELECT id, username, amount, transaction_type, operator_name, created_at 
        FROM transactions 
        WHERE group_id = %s 
        ORDER BY created_at DESC""",
        group_id
    )
    
    # 获取群组名称
    group = await db.fetch_one(
        "SELECT group_name FROM groups WHERE group_id = %s",
        group_id
    )
    
    group_name = group['group_name'] if group else "未知群组"
    
    # 计算统计数据
    total_income = sum(t['amount'] for t in transactions if t['transaction_type'] == '入款')
    total_expense = sum(t['amount'] for t in transactions if t['transaction_type'] == '出款')
    balance = total_income - total_expense
    
    return templates.TemplateResponse(
        "transactions.html", 
        {
            "request": request, 
            "transactions": transactions,
            "group_name": group_name,
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance
        }
    )
