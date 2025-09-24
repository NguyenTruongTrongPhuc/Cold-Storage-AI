# app/routers/state.py (Tạo file mới)

from fastapi import APIRouter
from app.simulation import storage

router = APIRouter(
    prefix="/api",
    tags=["State"]
)

@router.get("/state")
async def get_current_state():
    """
    Đây là endpoint chính, cung cấp một snapshot chứa toàn bộ trạng thái
    hiện tại của kho lạnh. UI trên coreIoT sẽ gọi endpoint này đầu tiên.
    """
    return storage.get_full_state()