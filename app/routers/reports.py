from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.simulation import storage

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/reports", tags=["Pages"], include_in_schema=False)
async def get_reports_page(request: Request):
    """Phục vụ trang HTML Báo cáo & Lịch sử."""
    return templates.TemplateResponse("reports.html", {"request": request, "active_page": "reports"})

@router.get("/api/historical-data", tags=["API"])
async def get_historical_data():
    """Cung cấp toàn bộ dữ liệu lịch sử cho trang báo cáo."""
    return {
        "energy_history": storage.energy_daily_history,
        "equipment_list": storage.equipment,
        "equipment_details": storage.equipment_details,
        "system_events": sorted(storage.system_events, key=lambda x: x['timestamp'], reverse=True) # Sắp xếp mới nhất lên đầu
    }