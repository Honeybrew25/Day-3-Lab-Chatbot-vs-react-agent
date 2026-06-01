import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        tool_descriptions = "\n".join(
            [
                f"- {tool['name']}: {tool['description']}"
                for tool in self.tools
            ]
        )
        tool_names = ", ".join([tool["name"] for tool in self.tools])

        return f"""
        Bạn là một chuyên gia tư vấn tài chính và thị trường vàng thông minh tại Việt Nam.

        Bạn có nhiệm vụ hỗ trợ người dùng phân tích thị trường vàng, giá vàng SJC, giá vàng nhẫn, tin tức tài chính, xu hướng kinh tế và các yếu tố ảnh hưởng đến thị trường vàng tại Việt Nam.

        Bạn có quyền truy cập vào các công cụ sau:

        {tool_descriptions}

        Tên các công cụ hợp lệ:
        {tool_names}

        Bạn PHẢI tuân theo phương pháp ReAct, gồm các bước:

        1. Thought:
        - Suy nghĩ ngắn gọn về việc cần làm tiếp theo.
        - Xác định xem có cần dùng công cụ hay không.
        - Không được bịa dữ liệu, giá vàng, tin tức hoặc kết quả quan sát.

        2. Action:
        - Nếu cần dùng công cụ, ghi đúng tên công cụ cần gọi.
        - Action phải là một trong các công cụ hợp lệ đã liệt kê.
        - Không được gọi công cụ không tồn tại.

        3. Observation:
        - Đây là kết quả trả về từ công cụ.
        - Chỉ sử dụng thông tin thật có trong Observation.
        - Không tự tạo Observation.

        Quy tắc định dạng bắt buộc khi cần dùng công cụ:

        Thought: Tôi cần kiểm tra thông tin liên quan bằng công cụ phù hợp.
        Action: <tên_công_cụ>(<tham_số_đầu_vào>)

        Sau khi nhận được kết quả từ công cụ, tiếp tục theo định dạng:

        Observation: <kết_quả_từ_công_cụ>
        Thought: Tôi đã có đủ thông tin để trả lời hoặc cần dùng thêm công cụ.

        Nếu đã đủ thông tin để trả lời người dùng, kết thúc bằng:

        Final Answer: <câu_trả_lời_cuối_cùng>

        Quy tắc quan trọng:

        - Nếu câu hỏi liên quan đến giá vàng hiện tại, tin tức mới, tỷ giá, biến động thị trường hoặc dữ liệu thời gian thực, bạn nên dùng công cụ trước khi trả lời.
        - Nếu không có công cụ phù hợp hoặc dữ liệu không đủ, hãy nói rõ rằng bạn không có đủ thông tin để kết luận.
        - Không đưa ra lời khuyên đầu tư chắc chắn như “nên mua ngay”, “chắc chắn tăng”, “chắc chắn giảm”.
        - Khi phân tích tài chính, hãy trình bày theo hướng tham khảo, nêu rủi ro và điều kiện thị trường.
        - Trả lời bằng tiếng Việt, rõ ràng, dễ hiểu.
        - Không bịa nguồn, không bịa số liệu, không bịa kết quả công cụ.
        - Chỉ sử dụng Action khi thật sự cần gọi công cụ.
        - Nếu câu hỏi có thể trả lời trực tiếp mà không cần công cụ, hãy trả lời ngay bằng Final Answer.

        --- VÍ DỤ ĐỊNH DẠNG (TUYỆT ĐỐI KHÔNG COPY NỘI DUNG VÍ DỤ NÀY) ---

        Thought: Người dùng hỏi về tin tức lãi suất, tôi cần gọi công cụ tìm kiếm tin tức.
        Action: search_financial_news(lãi suất ngân hàng)

        (Hệ thống sẽ trả về Observation)
        Observation: Ngân hàng trung ương quyết định giữ nguyên lãi suất ở mức 4.5%...
        
        Thought: Tôi đã có đủ thông tin tin tức, giờ tôi sẽ tổng hợp và trả lời người dùng.

        Final Answer: Theo các tin tức mới nhất, ngân hàng trung ương đã quyết định giữ nguyên lãi suất...
        --- KẾT THÚC VÍ DỤ ---
        """.strip()

    def run(self, user_input: str) -> str:
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        current_prompt = user_input
        steps = 0

        while steps < self.max_steps:

            # 1. Gọi LLM sinh ra Thought & Action
            # (Giả định đối tượng llm có hàm generate nhận prompt và system_prompt)
            response = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            result = response.get("content", "")
            
            # Ghi nhận kết quả của LLM vào bộ nhớ tạm
            current_prompt += f"\n{result}\n"
            
            # 2. Kiểm tra xem LLM đã đưa ra câu trả lời cuối cùng chưa
            if "Final Answer:" in result:
                final_answer = result.split("Final Answer:")[-1].strip()
                logger.log_event("AGENT_END", {"steps": steps + 1, "status": "success"})
                return final_answer
            
            # 3. Sử dụng Regex để Parse phần "Action: tool_name(args)"
            # Pattern này bắt: từ khoá Action:, khoảng trắng, tên_tool, và (tham_số)
            action_match = re.search(r"Action:\s*([a-zA-Z0-9_]+)\((.*?)\)", result)
            
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_args = action_match.group(2).strip()
                
                # Hiển thị trực quan cho học viên thấy quá trình Agent suy nghĩ
                thought = result.split("Action:")[0].replace("Thought:", "").strip()
                print(f"\n🧠 [Thought]: {thought}")
                print(f"🛠️ [Action]: Gọi tool '{tool_name}' với tham số '{tool_args}'")
                
                # 4. Thực thi Tool
                observation = self._execute_tool(tool_name, tool_args)
                print(f"👀 [Observation]: Nhận được {len(observation)} ký tự dữ liệu.")
                
                # 5. Cập nhật Observation vào bộ nhớ tạm để LLM đọc ở vòng lặp sau
                current_prompt += f"Observation: {observation}\n"
            else:
                # Xử lý lỗi nếu LLM "ảo giác" (hallucinate) và in sai định dạng
                print(f"\n⚠️ [Cảnh báo - Lỗi định dạng]: LLM sinh ra nội dung không hợp lệ:\n{result}\n")
                current_prompt += "Observation: Lỗi định dạng! Hãy nhớ dùng 'Action: tool_name(args)' hoặc 'Final Answer:'.\n"
            
            steps += 1
            
        logger.log_event("AGENT_END", {"steps": steps, "status": "timeout"})
        return "Xin lỗi, tôi đã vượt quá số bước suy nghĩ cho phép mà chưa tìm ra kết quả."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Hoàn thành logic thực thi Tool động bằng con trỏ hàm
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                try:
                    # Lấy function pointer và chạy với tham số
                    func = tool['function']
                    # Nếu args trống thì gọi hàm không tham số, ngược lại truyền args vào
                    if args:
                        return str(func(args))
                    return str(func())
                except Exception as e:
                    return f"Lỗi nội bộ khi chạy tool {tool_name}: {str(e)}"
                    
        return f"Tool '{tool_name}' không tồn tại. Vui lòng kiểm tra lại tên tool."
