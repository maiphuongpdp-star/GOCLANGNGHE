import json
import os
import streamlit as st
from google import genai

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Góc Lắng Nghe - THCS Phan Đình Phùng",
    page_icon="🌱",
    layout="centered",
)

# 1. Quản lý Thống kê (Chỉ lưu con số, KHÔNG lưu nội dung câu hỏi hay thông tin học sinh)
STATS_FILE = "stats.json"


def load_stats():
    if not os.path.exists(STATS_FILE):
        return {"total_questions": 0, "helpful_yes": 0, "helpful_no": 0}
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"total_questions": 0, "helpful_yes": 0, "helpful_no": 0}


def save_stats(stats):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f)
    except Exception:
        pass


stats = load_stats()

# 2. Bộ khung nguyên tắc sư phạm cốt lõi
SYSTEM_PROMPT = """
Bạn là "Góc Lắng Nghe" – người bạn đồng hành tâm lý ấm áp, nhân văn và đáng tin cậy dành cho học sinh THCS Phan Đình Phùng.

Khi học sinh chia sẻ một tình huống, hãy trả lời súc tích, gần gũi theo 4 bước sư phạm:
Bước 1: Lắng nghe, gọi tên cảm xúc và đồng cảm chân thành.
Bước 2: Giúp bạn bình tĩnh lại, nhắc hít thở sâu trước khi hành động.
Bước 3: Đưa ra 2-3 gợi ý hành xử văn minh, tôn trọng bản thân và người khác.
Bước 4: Nếu có dấu hiệu bạo lực nghiêm trọng hoặc nguy cơ tổn hại thân thể, khuyên bạn liên hệ ngay với thầy cô, cha mẹ hoặc Tổng đài Trẻ em 111.

Nguyên tắc an toàn: Tuyệt đối KHÔNG hỏi tên, lớp hay thông tin cá nhân của học sinh.
"""

# 3. Giao diện ứng dụng
st.title("🌱 Góc Lắng Nghe")
st.caption(
    "Không gian tư vấn tâm lý học đường ẩn danh - Trường THCS Phan Đình Phùng"
)
st.info(
    "🔒 **Cam kết an toàn & bảo mật:** Ứng dụng không yêu cầu đăng nhập, không thu thập danh tính và không lưu lại bất kỳ nội dung nào bạn chia sẻ."
)

# Kết nối API
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get(
    "GEMINI_API_KEY", ""
)
client = genai.Client(api_key=api_key) if api_key else None

user_question = st.text_area(
    "Bạn đang gặp chuyện gì hoặc có điều gì bận lòng cần chia sẻ không?",
    placeholder="Ví dụ: Bạn thân nói xấu sau lưng mình; Bị các bạn cô lập; Muốn đánh nhau vì bị trêu chọc...",
    height=120,
)

if st.button("Lắng nghe & Gợi ý cách giải quyết", type="primary"):
    if not user_question.strip():
        st.warning("Bạn hãy viết một chút về tình huống của mình nhé.")
    elif not client:
        st.error(
            "Chưa nhận diện được API Key. Vui lòng kiểm tra lại mục Secrets trên Streamlit Cloud."
        )
    else:
        with st.spinner("Đang suy ngẫm cùng bạn..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=user_question,
                    config={
                        "system_instruction": SYSTEM_PROMPT,
                        "max_output_tokens": 800,
                        "temperature": 0.7,
                    },
                )

                # Tăng số lượt hỏi
                stats["total_questions"] += 1
                save_stats(stats)

                # Hiển thị câu trả lời
                st.markdown("### 💬 Lời nhắn gửi đến bạn:")
                st.markdown(response.text)
                st.session_state["has_response"] = True
            except Exception as e:
                st.error(f"Đã có lỗi xảy ra: {e}")

# 4. Đánh giá chất lượng ẩn danh
if st.session_state.get("has_response", False):
    st.divider()
    st.write("**Gợi ý trên có giúp ích cho bạn không?**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Có, giúp mình bình tĩnh hơn"):
            stats["helpful_yes"] += 1
            save_stats(stats)
            st.success("Cảm ơn bạn! Chúc bạn một ngày tốt lành.")
            st.session_state["has_response"] = False
    with col2:
        if st.button("👎 Chưa, mình vẫn thấy bối rối"):
            stats["helpful_no"] += 1
            save_stats(stats)
            st.info(
                "Đừng giữ một mình nhé, hãy thử tâm sự với người lớn mà bạn tin tưởng!"
            )
            st.session_state["has_response"] = False

# 5. Cột thông tin thống kê minh bạch
with st.sidebar:
    st.header("📊 Minh bạch hoạt động")
    st.metric("Tổng lượt tham vấn", stats["total_questions"])
    total_feedbacks = stats["helpful_yes"] + stats["helpful_no"]
    rate = (
        (stats["helpful_yes"] / total_feedbacks * 100)
        if total_feedbacks > 0
        else 0
    )
    st.metric("Tỷ lệ thấy hữu ích", f"{rate:.1f}%")
