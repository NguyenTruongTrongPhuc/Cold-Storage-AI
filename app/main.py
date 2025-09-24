# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import asyncio

# Thêm "state" vào dòng import
from .routers import dashboard, energy, health, reports, ai_agent, state
from .simulation import run_simulation

app = FastAPI(title="Cold Storage AI Platform")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(dashboard.router)
app.include_router(energy.router)
app.include_router(health.router)
app.include_router(reports.router)
app.include_router(ai_agent.router)

# Thêm dòng này
app.include_router(state.router)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_simulation())
    asyncio.create_task(dashboard.broadcast_dashboard_data())