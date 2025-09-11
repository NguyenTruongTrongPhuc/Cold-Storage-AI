import random
import asyncio
import time
from datetime import datetime, date, timedelta

class ColdStorage:
    def __init__(self):
        # Dữ liệu cho trang Dashboard
        self.zone_A_temp = -20.0
        self.zone_B_temp = -20.2
        self.humidity = 88.0
        self.compressor_status = "ON"
        self.compressor_power_kw = 45.5
        self.defrost_status = "OFF"
        self.door_status = "CLOSED"
        self.predicted_load_kw = 48.0
        self.energy_efficiency = 3.5
        self.maintenance_status = "GOOD"
        self.heatmap_data = [[-20.0 for _ in range(10)] for _ in range(5)]
        self.load_history = []
        self.load_forecast = []
        self.compressor_schedule = []

        # Dữ liệu cho trang Phân tích Năng lượng
        self.energy_daily_history = []
        self.energy_baseline_range = []
        self.anomalies = []

        # Dữ liệu cho trang Sức khỏe Thiết bị
        self.equipment = [
            { "id": "comp-01", "name": "Máy nén #1 (Hitachi)", "type": "Máy nén", "status": "Hoạt động", "health_score": 95, "next_failure_forecast": "350 ngày", "recommendation": "Hoạt động bình thường" },
            { "id": "comp-02", "name": "Máy nén #2 (Bitzer)", "type": "Máy nén", "status": "Hoạt động", "health_score": 78, "next_failure_forecast": "85 ngày", "recommendation": "Kiểm tra định kỳ" },
            { "id": "fan-01", "name": "Quạt dàn lạnh A1", "type": "Quạt", "status": "Hoạt động", "health_score": 62, "next_failure_forecast": "28 ngày", "recommendation": "Nghi ngờ rung động, cần kiểm tra vòng bi" },
            { "id": "fan-02", "name": "Quạt dàn lạnh B1", "type": "Quạt", "status": "Tạm dừng", "health_score": 98, "next_failure_forecast": "400 ngày", "recommendation": "Hoạt động bình thường" }
        ]
        
        self.equipment_details = {
            "comp-01": {
                "ai_analysis": "Dòng điện và áp suất ổn định. Không phát hiện dấu hiệu bất thường.",
                "history": {
                    "Dòng điện (A)": self._generate_detail_history(8, 9),
                    "Áp suất (PSI)": self._generate_detail_history(150, 155)
                },
                "maintenance_log": [
                    "15/07/2025: Kỹ sư A - Kiểm tra định kỳ, mọi thứ ổn.",
                    "02/06/2025: Kỹ sư B - Thay dầu máy nén."
                ]
            },
            "comp-02": {
                "ai_analysis": "Hiệu suất giảm nhẹ 5% trong 2 tuần qua. Dòng khởi động có xu hướng tăng.",
                "history": {
                    "Dòng điện (A)": self._generate_detail_history(9, 11, True),
                    "Áp suất (PSI)": self._generate_detail_history(145, 140)
                },
                "maintenance_log": ["18/07/2025: Kỹ sư B - Kiểm tra định kỳ."]
            },
            "fan-01": {
                "ai_analysis": "AI phát hiện mẫu rung động bất thường ở tần số cao. Dự báo 85% khả năng vòng bi sẽ gặp sự cố trong 30 ngày tới. Khuyến nghị: Lên lịch kiểm tra trong tuần này.",
                "history": {
                    "Độ rung (mm/s)": self._generate_detail_history(0.2, 0.8, True),
                    "Dòng điện (A)": self._generate_detail_history(1.5, 1.8, True)
                },
                "maintenance_log": ["01/08/2025: Kỹ sư A - Vệ sinh cánh quạt."]
            },
            "fan-02": {
                "ai_analysis": "Thiết bị đang trong trạng thái dự phòng, các chỉ số đều trong ngưỡng an toàn.",
                "history": {
                    "Độ rung (mm/s)": self._generate_detail_history(0.1, 0.1),
                    "Dòng điện (A)": self._generate_detail_history(1.2, 1.2)
                },
                "maintenance_log": ["Chưa có ghi nhận bảo trì."]
            }
        }
        
        # Dữ liệu cho trang Báo cáo & Lịch sử
        self.system_events = []

        # Chạy hàm tạo dữ liệu lịch sử (90 ngày)
        self._generate_fake_past_energy_data(days=90)

    def _generate_fake_past_energy_data(self, days=90):
        """Hàm này tạo dữ liệu quá khứ cho một số ngày nhất định."""
        print(f"Bắt đầu tạo dữ liệu giả lập cho {days} ngày qua...")
        today = datetime.now()
        history_data = []
        baseline_min_data = []
        baseline_max_data = []
        anomalies_data = []

        for i in range(days):
            current_date = today - timedelta(days=(days-1)-i)
            timestamp = int(datetime(current_date.year, current_date.month, current_date.day).timestamp() * 1000)
            
            base_kwh = 450 + (i % 7) * 10 + random.uniform(-10, 10)
            min_kwh, max_kwh = base_kwh - 25, base_kwh + 25
            actual_kwh = base_kwh + random.uniform(-15, 15)

            if random.random() < 0.1 and i > 5: # Tạo bất thường ngẫu nhiên
                actual_kwh = max_kwh + random.uniform(30, 50)
                reason = random.choice([
                    "Cửa kho mở quá lâu do quy trình nhập hàng mới không tuân thủ.",
                    "Hiệu suất máy nén #2 giảm 15% so với bình thường, nghi ngờ rò rỉ gas."
                ])
                anomalies_data.append({"timestamp": timestamp, "value": round(actual_kwh, 2), "reason": reason})
                self.system_events.append({
                    "timestamp": timestamp, "type": "Năng lượng", "severity": "Cao",
                    "message": f"Phát hiện bất thường năng lượng. Tiêu thụ: {actual_kwh:.1f} kWh. Lý do nghi ngờ: {reason}"
                })

            history_data.append([timestamp, round(actual_kwh, 2)])
            baseline_min_data.append(round(min_kwh, 2))
            baseline_max_data.append(round(max_kwh, 2))

        self.energy_daily_history = history_data
        self.energy_baseline_range = list(zip(baseline_min_data, baseline_max_data))
        self.anomalies = anomalies_data
        print(f"Đã tạo xong dữ liệu năng lượng lịch sử {days} ngày.")

    def _generate_detail_history(self, base_val, trend_val, has_noise=False):
        """Hàm trợ giúp để tạo dữ liệu lịch sử đa chỉ số cho một thiết bị."""
        now_ts = int(time.time() * 1000)
        noise_factor = 0.5 if has_noise else 0.1
        return [[now_ts - (90-i)*24*60*60*1000, round(base_val + (i/90.0) * (trend_val - base_val) + random.uniform(-noise_factor, noise_factor), 2)] for i in range(90)]

    def update(self):
        """Hàm cập nhật trạng thái của kho theo thời gian thực."""
        # Cập nhật thông số môi trường
        avg_temp = (self.zone_A_temp + self.zone_B_temp) / 2
        if avg_temp > -19.0 and self.compressor_status == "OFF": self.compressor_status = "ON"
        elif avg_temp < -20.5 and self.compressor_status == "ON": self.compressor_status = "OFF"
        
        if self.compressor_status == "ON":
            self.zone_A_temp -= random.uniform(0.1, 0.3)
            self.zone_B_temp -= random.uniform(0.1, 0.3)
        else:
            self.zone_A_temp += random.uniform(0.05, 0.1)
            self.zone_B_temp += random.uniform(0.05, 0.1)

        self.humidity = max(85.0, min(95.0, self.humidity + random.uniform(-0.5, 0.5)))
        self.compressor_power_kw = (45.5 if self.compressor_status == "ON" else 0.5) + random.uniform(-1.0, 1.0)
        
        # Cập nhật các biểu đồ dashboard
        self._update_heatmap()
        self._update_load_charts()
        self._update_compressor_schedule()

        # Cập nhật điểm sức khỏe thiết bị và ghi lại sự kiện
        for device in self.equipment:
            if device["status"] == "Hoạt động":
                previous_score = device["health_score"]
                if device["id"] == "fan-01" and device["health_score"] > 50:
                    device["health_score"] -= random.uniform(0.01, 0.05)
                elif device["id"] == "comp-02" and device["health_score"] > 65:
                    device["health_score"] -= random.uniform(0.005, 0.02)
                
                if previous_score >= 80 and device["health_score"] < 80:
                    self.system_events.append({
                        "timestamp": int(time.time() * 1000), "type": "Thiết bị", "severity": "Trung bình",
                        "message": f"Điểm sức khỏe của '{device['name']}' đã giảm xuống dưới 80% ({device['health_score']:.1f}%)"
                    })
    
    def to_dict(self):
        """Chuyển đổi các thuộc tính cần thiết cho WebSocket của Dashboard."""
        return {
            "zone_A_temp": round(self.zone_A_temp, 2),
            "zone_B_temp": round(self.zone_B_temp, 2),
            "humidity": round(self.humidity, 2),
            "compressor_status": self.compressor_status,
            "compressor_power_kw": round(self.compressor_power_kw, 2),
            "heatmap_data": self.heatmap_data,
            "load_history": self.load_history,
            "load_forecast": self.load_forecast,
            "compressor_schedule": self.compressor_schedule,
        }

    def _update_heatmap(self):
        hot_spot_row, hot_spot_col = random.randint(2, 4), random.randint(0, 1)
        for r in range(5):
            for c in range(10):
                base_temp = (self.zone_A_temp + self.zone_B_temp) / 2
                distance = abs(r - hot_spot_row) + abs(c - hot_spot_col)
                self.heatmap_data[r][c] = base_temp + distance * 0.15 + random.uniform(-0.1, 0.1)

    def _update_load_charts(self):
        now_ts = int(time.time() * 1000)
        if not self.load_history or now_ts - self.load_history[-1][0] > 60000:
             self.load_history = [[now_ts - (12-i)*10*60*1000, 30 + (i % 6) * 5 + random.uniform(-2, 2)] for i in range(12)]
             self.load_history.append([now_ts, self.compressor_power_kw])
             self.load_forecast = [[now_ts + (i+1)*30*60*1000, 35 + random.uniform(-5, 5)] for i in range(6)]

    def _update_compressor_schedule(self):
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        def to_ts(hour): return int((start_of_day + timedelta(hours=hour)).timestamp() * 1000)
        
        self.compressor_schedule = [
            {"name": "Giá rẻ", "start": to_ts(0), "end": to_ts(4), "color": "#008FFB"},
            {"name": "Bật", "start": to_ts(0.5), "end": to_ts(3.5), "color": "#775DD0"},
            {"name": "Bình thường", "start": to_ts(4), "end": to_ts(9), "color": "#FEB019"},
            {"name": "Bật", "start": to_ts(7), "end": to_ts(8.5), "color": "#775DD0"},
            {"name": "Giá cao", "start": to_ts(9), "end": to_ts(12), "color": "#FF4560"},
            {"name": "Bình thường", "start": to_ts(12), "end": to_ts(24), "color": "#FEB019"},
            {"name": "Bật", "start": to_ts(14), "end": to_ts(16), "color": "#775DD0"},
            {"name": "Bật", "start": to_ts(20), "end": to_ts(23), "color": "#775DD0"}
        ]

storage = ColdStorage()

async def run_simulation():
    """Chạy vòng lặp vô tận để cập nhật trạng thái kho mỗi 2 giây."""
    while True:
        storage.update()
        await asyncio.sleep(2)