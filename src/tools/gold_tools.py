import pandas as pd
import numpy as np
import requests
import yfinance as yf

# --- CÁC HÀM XỬ LÝ LÕI ---
def get_current_gold_price(args=""):
    try:
        # Sử dụng API mới thay thế
        url = "https://www.vang.today/api/prices?type=SJL1L10" 
        
        # Thêm User-Agent giả lập trình duyệt để không bị hệ thống chặn (Anti-bot)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*'
        }
        
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        
        if response.status_code == 200:
            # Phân tích dữ liệu JSON trả về từ API mới
            data = response.json()
            
            # Bóc tách dữ liệu an toàn và linh hoạt hơn
            if isinstance(data, dict):
                data = data.get('data', data.get('results', data))
                
            item = data[0] if isinstance(data, list) and len(data) > 0 else data
            
            buy = item.get('buy', item.get('buyPrice', 'Không rõ'))
            sell = item.get('sell', item.get('sellPrice', 'Không rõ'))
            
            return f"Giá vàng SJC trong nước Real-time: Mua vào {buy} - Bán ra {sell}."
            
        # NẾU SJC THẤT BẠI HOẶC KHÔNG TÌM THẤY DỮ LIỆU -> DÙNG YFINANCE (VÀNG THẾ GIỚI)
        gold = yf.Ticker("GC=F")
        current_price = gold.history(period="5d")['Close'].iloc[-1]
        usd_vnd_rate = yf.Ticker("VND=X").history(period="5d")['Close'].iloc[-1]
        price_vnd = (current_price * 1.20565 * usd_vnd_rate) / 1_000_000
        return f"Không thể lấy SJC. Giá vàng thế giới quy đổi: {price_vnd:.2f} triệu VNĐ/lượng."
    except Exception as e:
        try:
            # Dự phòng yfinance nếu request SJC văng lỗi Exception (vd: mất mạng, timeout)
            gold = yf.Ticker("GC=F")
            current_price = gold.history(period="5d")['Close'].iloc[-1]
            usd_vnd_rate = yf.Ticker("VND=X").history(period="5d")['Close'].iloc[-1]
            price_vnd = (current_price * 1.20565 * usd_vnd_rate) / 1_000_000
            return f"Giá vàng thế giới quy đổi: {price_vnd:.2f} triệu VNĐ/lượng."
        except Exception as fallback_e:
            return f"Lỗi lấy giá vàng: API chính ({str(e)}), Fallback ({str(fallback_e)})."

def analyze_30day_gold_trend(args=""):
    try:
        # Sử dụng yfinance để lấy dữ liệu giá vàng thế giới 30 ngày qua (Mã GC=F: Gold Futures)
        gold = yf.Ticker("GC=F")
        hist = gold.history(period="1mo")
        
        if hist.empty:
            return "Không lấy được dữ liệu lịch sử 30 ngày từ yfinance."
            
        usd_vnd_rate = yf.Ticker("VND=X").history(period="1d")['Close'].iloc[-1]
        prices_usd = hist['Close'].values
        
        # Quy đổi mảng giá sang Triệu VNĐ / Lượng (1 lượng = 1.20565 ounce)
        prices_vnd = (prices_usd * 1.20565 * usd_vnd_rate) / 1_000_000
        
        start_p, end_p = prices_vnd[0], prices_vnd[-1]
        pct_change = ((end_p - start_p) / start_p) * 100
        
        return f"Phân tích 30 ngày qua (Quy đổi VNĐ/lượng): Giá thấp nhất {min(prices_vnd):.2f} triệu, giá cao nhất {max(prices_vnd):.2f} triệu. Mức biến động là {pct_change:.2f}%."
    except Exception as e:
        return f"Lỗi lấy dữ liệu lịch sử ({str(e)}). Không thể lấy giá vàng lúc này. Vui lòng thử lại sau."


# --- ĐÓNG GÓI THÀNH TOOL DEFINITIONS ---
gold_tools = [
    {
        "name": "get_current_gold_price",
        "description": "Lấy giá vàng mới nhất của ngày hôm nay. Không cần tham số đầu vào.",
        "function": get_current_gold_price
    },
    {
        "name": "analyze_30day_gold_trend",
        "description": "Phân tích xu hướng giá vàng 30 ngày qua. Không cần tham số đầu vào.",
        "function": analyze_30day_gold_trend
    }
]