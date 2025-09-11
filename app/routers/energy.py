from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.simulation import storage # Sử dụng import tuyệt đối

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/energy", tags=["Pages"])
async def get_energy_analysis(request: Request):
    return templates.TemplateResponse("energy.html", {"request": request, "active_page": "energy"})

@router.get("/api/energy-history", tags=["API"])
async def get_energy_history_data():
    return {
        "energy_daily_history": storage.energy_daily_history,
        "energy_baseline_range": storage.energy_baseline_range,
        "anomalies": storage.anomalies,
    }