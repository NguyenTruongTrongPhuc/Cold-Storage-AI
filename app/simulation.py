import random
import asyncio
import time
from datetime import datetime, timedelta
import uuid
import pandas as pd
from prophet import Prophet

# --- Hằng số Cấu hình ---
PREDICTION_PERIOD_MINUTES = 240
CONTEXT_HOURS = 24
SPIKE_THRESHOLD = 1.25
DOOR_OPEN_ANOMALY_SECONDS = 300 # 5 phút

class ColdStorage:
    def __init__(self):
        # --- Trạng thái Môi trường & Hoạt động ---
        self.zone_A_temp = -20.0
        self.zone_B_temp = -20.2
        self.humidity = 88.0
        self.compressor_status = "ON"
        self.compressor_power_kw = 45.5
        self.defrost_status = "OFF"
        self.door_status = "CLOSED"
        self.door_open_duration_s = 0

        # --- Dữ liệu Lịch sử & Phân tích ---
        self.load_history = []
        self.energy_daily_history = []
        self.energy_baseline_range = []
        self.anomalies = []
        self.system_events = []

        # --- Trạng thái Thiết bị ---
        self.equipment = [
            {"id": "comp-01", "name": "Máy nén #1 (Hitachi)", "type": "Máy nén", "status": "Hoạt động", "health_score": 95.0},
            {"id": "comp-02", "name": "Máy nén #2 (Bitzer)", "type": "Máy nén", "status": "Hoạt động", "health_score": 78.0},
            {"id": "fan-01", "name": "Quạt dàn lạnh A1", "type": "Quạt", "status": "Hoạt động", "health_score": 62.0},
            {"id": "fan-02", "name": "Quạt dàn lạnh B1", "type": "Quạt", "status": "Tạm dừng", "health_score": 98.0}
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
        
        # --- AI Agent & Dự báo ---
        print("Khởi tạo AI Agent với mô hình Prophet...")
        self.prophet_model = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=True)
        self.ai_recommendations = []
        self.last_prediction_time = 0
        print("AI Agent đã sẵn sàng.")
        
        self._generate_fake_past_energy_data(days=90)

    def _generate_detail_history(self, base_val, trend_val, has_noise=False):
        """Hàm trợ giúp để tạo dữ liệu lịch sử đa chỉ số cho một thiết bị."""
        now_ts = int(time.time() * 1000)
        noise_factor = 0.5 if has_noise else 0.1
        return [[now_ts - (90-i)*24*60*60*1000, round(base_val + (i/90.0) * (trend_val - base_val) + random.uniform(-noise_factor, noise_factor), 2)] for i in range(90)]

    # --- CÁC HÀM CUNG CẤP DỮ LIỆU CHO API ---
    def get_full_state(self):
        """Trả về toàn bộ trạng thái hiện tại của kho, dùng cho API chính."""
        active_compressor = next((e for e in self.equipment if e["type"] == "Máy nén" and e["status"] == "Hoạt động"), self.equipment[0])
        return {
            "environment": {
                "zone_a_temp": round(self.zone_A_temp, 2),
                "zone_b_temp": round(self.zone_B_temp, 2),
                "avg_temp": round((self.zone_A_temp + self.zone_B_temp) / 2, 2),
                "humidity": round(self.humidity, 2),
            },
            "operation": {
                "compressor_status": self.compressor_status,
                "compressor_power_kw": round(self.compressor_power_kw, 2),
                "active_compressor_id": active_compressor["id"],
                "door_status": self.door_status,
                "door_open_duration_s": self.door_open_duration_s,
                "defrost_status": self.defrost_status,
            },
            "kpis": {
                "energy_efficiency": round(48.0 / self.compressor_power_kw if self.compressor_power_kw > 1 else 0, 2),
                "total_anomalies": len(self.anomalies),
                "devices_at_risk": sum(1 for e in self.equipment if e["health_score"] < 80),
            },
            "equipment_summary": self.equipment,
            "ai_agent": {
                "recommendations": self.ai_recommendations
            }
        }

    def to_dict_for_websocket(self):
        """Trả về dữ liệu rút gọn để cập nhật real-time qua WebSocket."""
        return {
            "avg_temp": round((self.zone_A_temp + self.zone_B_temp) / 2, 2),
            "humidity": round(self.humidity, 2),
            "compressor_status": self.compressor_status,
            "compressor_power_kw": round(self.compressor_power_kw, 2),
            "door_status": self.door_status,
            "heatmap_data": self._get_heatmap_data(),
            "load_history": self.load_history,
            "load_forecast": self._get_simple_forecast(),
            "compressor_schedule": self._get_compressor_schedule()
        }

    # --- CÁC HÀM TƯƠNG TÁC ---
    def fix_equipment(self, device_id: str):
        """Mô phỏng việc sửa chữa thiết bị, phục hồi điểm sức khỏe."""
        for device in self.equipment:
            if device["id"] == device_id:
                device["health_score"] = 98.0
                self.system_events.insert(0, {
                    "timestamp": int(time.time() * 1000), "type": "Bảo trì", "severity": "Thấp",
                    "message": f"Thiết bị '{device['name']}' đã được bảo trì, phục hồi điểm sức khỏe."
                })
                return True
        return False
    
    # --- CÁC HÀM LOGIC CỦA SIMULATION ---
    def update(self):
        """Hàm cập nhật chính, chạy mỗi 2 giây."""
        self._update_environmental_factors()
        self._degrade_equipment_health()
        self._update_temperature()
        self._update_compressor_power()
        self._run_ai_agent_logic()

    def _update_environmental_factors(self):
        if random.random() < 0.01 and self.door_status == "CLOSED":
            self.door_status = "OPEN"
        elif random.random() < 0.05 and self.door_status == "OPEN":
            self.door_status = "CLOSED"
        
        if self.door_status == "OPEN":
            self.door_open_duration_s += 2
            if self.door_open_duration_s == DOOR_OPEN_ANOMALY_SECONDS:
                if not any(a['reason'].startswith('Cửa kho mở') for a in self.anomalies):
                    self.anomalies.append({
                        "timestamp": int(time.time() * 1000), "value": None,
                        "reason": f"Cửa kho mở liên tục trong {DOOR_OPEN_ANOMALY_SECONDS // 60} phút."
                    })
                    self.system_events.insert(0, {"timestamp": int(time.time() * 1000), "type": "Vận hành", "severity": "Cao", "message": "Cảnh báo: Cửa kho mở quá lâu!"})
        else:
            self.door_open_duration_s = 0

    def _degrade_equipment_health(self):
        for device in self.equipment:
            if device["status"] == "Hoạt động":
                degradation = 0.005 if "Máy nén" in device["name"] else 0.01
                if device["health_score"] > 40:
                    device["health_score"] -= degradation

    def _update_temperature(self):
        self.zone_A_temp += random.uniform(0.01, 0.03)
        self.zone_B_temp += random.uniform(0.01, 0.03)
        
        if self.door_status == "OPEN":
            self.zone_A_temp += random.uniform(0.1, 0.2)
            self.zone_B_temp += random.uniform(0.1, 0.2)
            
        if self.compressor_status == "ON":
            self.zone_A_temp -= random.uniform(0.1, 0.3)
            self.zone_B_temp -= random.uniform(0.1, 0.3)
            
        avg_temp = (self.zone_A_temp + self.zone_B_temp) / 2
        if avg_temp > -19.5 and self.compressor_status == "OFF":
            self.compressor_status = "ON"
        elif avg_temp < -20.5 and self.compressor_status == "ON":
            self.compressor_status = "OFF"

    def _update_compressor_power(self):
        if self.compressor_status == "OFF":
            self.compressor_power_kw = 0.5 + random.uniform(-0.2, 0.2)
            return

        base_power = 45.0
        
        active_compressor = next((e for e in self.equipment if e["type"] == "Máy nén" and e["status"] == "Hoạt động"), self.equipment[0])
        health_score = active_compressor['health_score']
        efficiency_factor = 1 + (100 - health_score) / 150
        
        door_penalty = 10.0 if self.door_status == "OPEN" else 0.0
        
        self.compressor_power_kw = (base_power * efficiency_factor) + door_penalty + random.uniform(-1.0, 1.0)
        
        self.load_history.append([int(time.time() * 1000), self.compressor_power_kw])
        if len(self.load_history) > 1500:
            self.load_history.pop(0)
    
    def _run_ai_agent_logic(self):
        now_ts = time.time()
        if now_ts - self.last_prediction_time < 900:
            return

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] AI Agent bắt đầu chạy dự báo với Prophet...")
        self.last_prediction_time = now_ts

        history_points = [p for p in self.load_history if datetime.fromtimestamp(p[0]/1000) > datetime.now() - timedelta(hours=CONTEXT_HOURS)]
        
        if len(history_points) < 20:
            print("Chưa đủ dữ liệu lịch sử để dự báo.")
            return

        df = pd.DataFrame(history_points, columns=['ds', 'y'])
        df['ds'] = pd.to_datetime(df['ds'], unit='ms')

        m = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=True).fit(df)
        future_df = m.make_future_dataframe(periods=PREDICTION_PERIOD_MINUTES, freq='min')
        forecast = m.predict(future_df)
        
        current_load = df['y'].iloc[-1]
        future_forecast = forecast[forecast['ds'] > df['ds'].iloc[-1]]
        max_predicted_load = future_forecast['yhat'].max()

        print(f"Tải hiện tại: {current_load:.1f} kW. Tải dự báo cao nhất trong {PREDICTION_PERIOD_MINUTES//60} giờ tới: {max_predicted_load:.1f} kW")

        if max_predicted_load > current_load * SPIKE_THRESHOLD and not any(rec['type'] == 'PREDICTIVE_COOLING' for rec in self.ai_recommendations):
            self.ai_recommendations.append({
                "id": str(uuid.uuid4()), "type": "PREDICTIVE_COOLING",
                "title": "AI Dự báo Tải nhiệt Tăng cao",
                "reason": f"Mô hình Prophet dự báo tải nhiệt có thể tăng lên tới {max_predicted_load:.1f} kW trong vài giờ tới.",
                "action_suggestion": "Kích hoạt chế độ 'Làm lạnh trước' (Pre-cooling) để ổn định nhiệt độ.",
                "created_at": time.time()
            })
        
        self.ai_recommendations = [rec for rec in self.ai_recommendations if now_ts - rec['created_at'] < 3600]

    def _get_heatmap_data(self):
        hot_spot_row, hot_spot_col = (2, 1) if self.door_status == "OPEN" else (4, 8)
        base_temp = (self.zone_A_temp + self.zone_B_temp) / 2
        heatmap = [[0.0 for _ in range(10)] for _ in range(5)]
        for r in range(5):
            for c in range(10):
                distance = abs(r - hot_spot_row) + abs(c - hot_spot_col)
                heatmap[r][c] = base_temp + distance * 0.15 + random.uniform(-0.1, 0.1)
        return heatmap

    def _get_simple_forecast(self):
        now_ts = int(time.time() * 1000)
        return [[now_ts + (i+1)*30*60*1000, self.compressor_power_kw + random.uniform(-5, 5)] for i in range(6)]
    
    def _get_compressor_schedule(self):
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        def to_ts(hour): return int((start_of_day + timedelta(hours=hour)).timestamp() * 1000)
        
        return [
            {"name": "Giá rẻ", "start": to_ts(0), "end": to_ts(4), "color": "#008FFB"},
            {"name": "Bật", "start": to_ts(0.5), "end": to_ts(3.5), "color": "#775DD0"},
            {"name": "Bình thường", "start": to_ts(4), "end": to_ts(9), "color": "#FEB019"},
            {"name": "Bật", "start": to_ts(7), "end": to_ts(8.5), "color": "#775DD0"},
            {"name": "Giá cao", "start": to_ts(9), "end": to_ts(12), "color": "#FF4560"},
            {"name": "Bình thường", "start": to_ts(12), "end": to_ts(24), "color": "#FEB019"},
            {"name": "Bật", "start": to_ts(14), "end": to_ts(16), "color": "#775DD0"},
            {"name": "Bật", "start": to_ts(20), "end": to_ts(23), "color": "#775DD0"}
        ]

    def _generate_fake_past_energy_data(self, days=90):
        """Hàm này tạo dữ liệu quá khứ cho một số ngày nhất định."""
        print(f"Bắt đầu tạo dữ liệu giả lập cho {days} ngày qua...")
        today = datetime.now()
        history_data, baseline_min_data, baseline_max_data, anomalies_data = [], [], [], []
        for i in range(days):
            current_date = today - timedelta(days=(days-1)-i)
            timestamp = int(datetime(current_date.year, current_date.month, current_date.day).timestamp() * 1000)
            base_kwh = 450 + (i % 7) * 10 + random.uniform(-10, 10)
            min_kwh, max_kwh = base_kwh - 25, base_kwh + 25
            actual_kwh = base_kwh + random.uniform(-15, 15)
            if random.random() < 0.1 and i > 5:
                actual_kwh = max_kwh + random.uniform(30, 50)
                reason = random.choice(["Cửa kho mở quá lâu.", "Hiệu suất máy nén #2 giảm."])
                anomalies_data.append({"timestamp": timestamp, "value": round(actual_kwh, 2), "reason": reason})
                self.system_events.append({"timestamp": timestamp, "type": "Năng lượng", "severity": "Cao", "message": f"Bất thường năng lượng: {actual_kwh:.1f} kWh. Lý do: {reason}"})
            history_data.append([timestamp, round(actual_kwh, 2)])
            baseline_min_data.append(round(min_kwh, 2))
            baseline_max_data.append(round(max_kwh, 2))
        self.energy_daily_history = history_data
        self.energy_baseline_range = list(zip(baseline_min_data, baseline_max_data))
        self.anomalies = anomalies_data
        print(f"Đã tạo xong dữ liệu năng lượng lịch sử {days} ngày.")

def _get_hourly_load_pattern():
    """Tạo ra một mẫu tải thay đổi theo giờ trong ngày để Prophet có thể học được."""
    hour = datetime.now().hour
    if 6 <= hour < 12: return 0.5
    elif 12 <= hour < 18: return 1.5 
    elif 18 <= hour < 22: return 1.0
    else: return 0.2

storage = ColdStorage()

async def run_simulation():
    """Chạy vòng lặp vô tận để cập nhật trạng thái kho."""
    print("Đang tạo dữ liệu lịch sử ban đầu cho Prophet...")
    initial_now_s = time.time()
    for i in range(1500):
        past_time_s = initial_now_s - (1500 - i) * 600
        past_dt = datetime.fromtimestamp(past_time_s)
        hour = past_dt.hour
        pattern = 0
        if 6 <= hour < 12: pattern = 0.5
        elif 12 <= hour < 18: pattern = 1.5 
        elif 18 <= hour < 22: pattern = 1.0
        else: pattern = 0.2
        storage.load_history.append([int(past_time_s * 1000), 40 + random.uniform(-3, 3) + 5 * (1 + pattern)])
    print("Hoàn tất tạo dữ liệu lịch sử ban đầu.")

    while True:
        storage.update()
        await asyncio.sleep(2)