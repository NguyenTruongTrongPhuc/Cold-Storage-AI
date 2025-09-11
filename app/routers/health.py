from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.simulation import storage 

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/health", tags=["Pages"], include_in_schema=False)
async def get_health_page(request: Request):
    """Phục vụ trang HTML Sức khỏe Thiết bị."""
    return templates.TemplateResponse("health.html", {"request": request, "active_page": "health"})

@router.get("/api/equipment-health", tags=["API"])
async def get_equipment_health_data():
    """Cung cấp dữ liệu sức khỏe của tất cả thiết bị."""
    # Kết hợp dữ liệu chi tiết vào danh sách thiết bị chính
    detailed_equipment = []
    for device in storage.equipment:
        device_id = device.get("id")
        if device_id in storage.equipment_details:
            device_with_details = device.copy()
            device_with_details.update(storage.equipment_details[device_id])
            detailed_equipment.append(device_with_details)
    
    return detailed_equipment