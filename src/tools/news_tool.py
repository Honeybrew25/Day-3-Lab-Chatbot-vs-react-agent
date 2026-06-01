from bs4 import BeautifulSoup
import requests

def search_financial_news(query=""):
    try:
        url = "https://news.google.com/rss/search"
        # Nếu Agent không truyền từ khóa, mặc định tìm "thị trường vàng tài chính"
        search_query = query if query else "thị trường vàng tài chính"
        
        # Tham số truy vấn: hl=vi (tiếng Việt), gl=VN (Vùng Việt Nam)
        params = {
            "q": search_query,
            "hl": "vi",
            "gl": "VN",
            "ceid": "VN:vi"
        }
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'xml')
            # Lấy 3 tin tức mới nhất (tránh nhồi quá nhiều text vào context của LLM)
            items = soup.find_all('item', limit=3)
            
            if not items:
                return f"Không tìm thấy tin tức nào cho từ khóa: {search_query}"
            
            news_results = [f"- {item.title.text} ({item.pubDate.text})" for item in items]
            return f"Tin tức vĩ mô mới nhất về '{search_query}':\n" + "\n".join(news_results)
        else:
            return "Lỗi khi kết nối đến nguồn Google News."
    except Exception as e:
        return f"Lỗi lấy tin tức ({str(e)}). Không tìm thấy tin tức nào."

# Định nghĩa cấu trúc tool để Agent có thể hiểu và sử dụng
news_tools = [
    {
        "name": "search_financial_news",
        "description": "Tìm kiếm tin tức kinh tế vĩ mô. Tham số đầu vào: từ khóa tìm kiếm.",
        "function": search_financial_news
    }
]