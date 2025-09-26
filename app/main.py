# app/main.py (Phiên bản cuối cùng, đã thêm CORS)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware # Thêm dòng import này
import asyncio

from .routers import dashboard, energy, health, reports, ai_agent, state
from .simulation import run_simulation

app = FastAPI(title="Cold Storage AI Platform")

# --- THÊM KHỐI CODE NÀY VÀO ---
# Cấu hình CORS
# Dấu "*" có nghĩa là cho phép TẤT CẢ các tên miền gọi đến API của bạn.
# Điều này rất tiện cho việc phát triển.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Cho phép tất cả các method (GET, POST, etc.)
    allow_headers=["*"], # Cho phép tất cả các header
)
# ---------------------------------


app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(dashboard.router)
app.include_router(energy.router)
app.include_router(health.router)
app.include_router(reports.router)
app.include_router(ai_agent.router)
app.include_router(state.router)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_simulation())
    asyncio.create_task(dashboard.broadcast_dashboard_data())