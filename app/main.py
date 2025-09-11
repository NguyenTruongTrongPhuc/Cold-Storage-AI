from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import asyncio

from .routers import dashboard, energy, health, reports
from .simulation import run_simulation

app = FastAPI(title="Cold Storage AI Platform")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(dashboard.router)
app.include_router(energy.router)
app.include_router(health.router)
app.include_router(reports.router)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_simulation())
    asyncio.create_task(dashboard.broadcast_dashboard_data())