import os
import sys
from dotenv import load_dotenv

# Thêm thư mục gốc vào sys.path để import được các module trong src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Nạp cấu hình từ file .env
load_dotenv()

from src.agent.agent import ReActAgent
from src.tools.gold_tools import gold_tools
from src.tools.news_tool import news_tools

# Giả định bạn đang import class OpenAIProvider từ file src/core/openai_provider.py của bạn
from src.core.openai_provider import OpenAIProvider 

def main():
    # Gom tất cả các công cụ lại thành một danh sách duy nhất
    all_tools = gold_tools + news_tools

    # 1. Khởi tạo LLM Model một lần để tiết kiệm tài nguyên
    llm = OpenAIProvider(model_name="gpt-4o-mini") 
    
    # 2. Định nghĩa 5 test cases để kiểm tra các khả năng của Agent
    test_cases = [
        "Giá vàng SJC hôm nay bao nhiêu?",
        "Phân tích xu hướng vàng 30 ngày qua cho tôi.",
        "Có tin tức gì mới về thị trường tài chính không?",
        "Dựa vào tin tức, giá vàng có khả năng tăng hay giảm?",
        "Giá vàng hôm nay bao nhiêu? Hãy phân tích biến động 30 ngày qua và đọc tin tức để khuyên tôi có nên mua vào không."
    ]

    # 3. Chạy lần lượt từng test case
    for i, user_question in enumerate(test_cases, 1):
        print(f"\n\n{'='*25} BẮT ĐẦU TEST CASE {i}/{len(test_cases)} {'='*25}")
        
        # Khởi tạo Agent mới cho mỗi test case để reset history và các bước suy nghĩ
        agent = ReActAgent(llm=llm, tools=all_tools, max_steps=5)
        
        print(f"🙋‍♂️ USER: {user_question}\n")
        print("⏳ Agent đang suy nghĩ và thực thi...\n")
        
        final_result = agent.run(user_question)
        
        print("\n---------------------------------------------")
        print("🤖 ĐÁP ÁN CUỐI CÙNG TỪ AGENT (FINAL ANSWER):")
        print("---------------------------------------------")
        print(final_result)
        print(f"\n{'='*25} KẾT THÚC TEST CASE {i}/{len(test_cases)} {'='*25}")

if __name__ == "__main__":
    main()