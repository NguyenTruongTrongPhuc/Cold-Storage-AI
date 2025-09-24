from fastapi import APIRouter, HTTPException
from app.simulation import storage
import time

router = APIRouter(
    prefix="/api/ai-agent",
    tags=["AI Agent"]
)

@router.get("/recommendations", summary="Lấy các khuyến nghị hiện tại từ AI Agent")
async def get_ai_recommendations():
    """
    Trả về một danh sách các khuyến nghị mà AI đang đề xuất.
    Frontend sẽ gọi API này để hiển thị cho người dùng.
    """
    return storage.ai_recommendations

@router.post("/recommendations/{rec_id}/act", summary="Người dùng chấp nhận một khuyến nghị")
async def act_on_recommendation(rec_id: str):
    """
    Khi người dùng nhấn "Chấp nhận" trên UI.
    Backend sẽ ghi nhận hành động này và xóa khuyến nghị khỏi danh sách.
    Trong tương lai, đây là nơi sẽ kích hoạt hành động thực tế (bật máy nén, etc.).
    """
    recommendation_index = -1
    for i, rec in enumerate(storage.ai_recommendations):
        if rec["id"] == rec_id:
            recommendation_index = i
            break
            
    if recommendation_index == -1:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec_to_act = storage.ai_recommendations.pop(recommendation_index)
    print(f"Người dùng đã CHẤP NHẬN khuyến nghị: {rec_to_act['title']}")

    # Ghi lại sự kiện hệ thống
    storage.system_events.insert(0, {
        "timestamp": int(time.time() * 1000), "type": "AI Agent", "severity": "Thấp",
        "message": f"Người dùng đã chấp nhận khuyến nghị: '{rec_to_act['action_suggestion']}'"
    })
    
    return {"status": "accepted", "recommendation_id": rec_id}

@router.post("/recommendations/{rec_id}/dismiss", summary="Người dùng bỏ qua một khuyến nghị")
async def dismiss_recommendation(rec_id: str):
    """
    Khi người dùng nhấn "Bỏ qua".
    Backend sẽ xóa khuyến nghị khỏi danh sách.
    """
    initial_len = len(storage.ai_recommendations)
    storage.ai_recommendations = [rec for rec in storage.ai_recommendations if rec["id"] != rec_id]
    
    if len(storage.ai_recommendations) == initial_len:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    print(f"Người dùng đã BỎ QUA khuyến nghị ID: {rec_id}")
    return {"status": "dismissed", "recommendation_id": rec_id}