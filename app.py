import json
import os
import time
import streamlit as st
from google import genai

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Góc Lắng Nghe - THCS Phan Đình Phùng",
    page_icon="🌱",
    layout="wide",
)

# 1. QUẢN LÝ DỮ LIỆU THỐNG KÊ MINH BẠCH (Chỉ lưu con số nhóm chủ đề, KHÔNG lưu nội dung)
STATS_FILE = "stats.json"


def load_stats():
    default_stats = {
        "total_questions": 0,
        "helpful_yes": 0,
        "helpful_no": 0,
        "topics": {
            "Mâu thuẫn bạn bè": 0,
            "Áp lực học tập / Thi cử": 0,
            "Gia đình & Cha mẹ": 0,
            "Bắt nạt / Tẩy chay": 0,
            "Bất an về bản thân": 0,
            "Khác": 0,
        },
    }
    if not os.path.exists(STATS_FILE):
        return default_stats
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Đồng bộ trường nếu file cũ thiếu
            if "topics" not in data:
                data["topics"] = default_stats["topics"]
            return data
    except Exception:
        return default_stats


def save_stats(stats):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


stats = load_stats()

# 2. SYSTEM PROMPT: VAI TRÒ CHUYÊN GIA TÂM LÝ HỌC ĐƯỜNG LỨA TUỔI THCS
SYSTEM_PROMPT = """
Bạn là một Chuyên gia Tâm lý Học đường giàu kinh nghiệm, chuyên sâu về tâm lý lứa tuổi dậy thì và Trung học Cơ sở (11-15 tuổi), đang đồng hành cùng học sinh trường THCS Phan Đình Phùng.

ĐẶC TRƯNG TÂM LÝ LỨA TUỔI CẦN NẮM VỮNG:
- Học sinh THCS rất nhạy cảm với sự tôn trọng, dễ tự ái, có nhu cầu khẳng định bản thân và rất coi trọng nhóm bạn đồng trang lứa.
- Thù ghét sự áp đặt, giáo điều, trách móc hoặc bị so sánh với người khác.
- Dễ hành động bột phát khi cảm thấy bị xúc phạm hoặc bị cô lập.

NGUYÊN TẮC THAM VẤN CỐT LÕI:
1. Giọng điệu: Ấm áp, kiên nhẫn, bình đẳng, không phán xét, sử dụng đại từ xưng hô thân mật: "Thầy/Cô chuyên gia" và "Em" (hoặc "Mình" và "Bạn").
2. Tuyệt đối KHÔNG hỏi tên, tuổi, lớp, địa chỉ hoặc bất kỳ thông tin nhận dạng cá nhân nào.
3. CẤU TRÚC PHẢN HỒI BẮT BUỘC THEO 3 PHẦN ĐÁNH DẤU CHÍNH XÁC NHƯ SAU ĐỂ HỆ THỐNG HIỂN THỊ THÀNH THẺ:

[PHAN_1: THẤU HIỂU & GỌI TÊN CẢM XÚC]
- Gọi tên chính xác cảm xúc em đang trải qua (ấm ức, tổn thương, lo sợ, tủi thân hay tức giận).
- Thừa nhận và bình thường hóa cảm xúc đó (Ví dụ: "Cảm thấy tức giận khi bị bạn bè nói xấu là phản ứng rất tự nhiên của bất kỳ ai...").

[PHAN_2: GÓC NHÌN ĐA CHIỀU]
- Giúp em nhìn sự việc dưới lăng kính khách quan, tách biệt giữa "hành vi của bạn" và "giá trị bản thân em".
- Gợi mở xem điều gì có thể đang diễn ra ở phía đối phương mà không bênh vực hành vi sai trái.

[PHAN_3: KẾ HOẠCH HÀNH ĐỘNG VĂN MINH]
- Đưa ra 2 đến 3 bước hành động rất cụ thể, khả thi và giữ vững lòng tự trọng.
- Hướng dẫn câu nói mẫu nếu em cần đối thoại trực tiếp để đặt ranh giới.
- Nhắc nhở tìm đến sự trợ giúp nếu tình huống vượt quá khả năng tự giải quyết.
"""

# 3. GIAO DIỆN CHÍNH
st.title("🌱 Góc Lắng Nghe - THCS Phan Đình Phùng")
st.caption(
    "Không gian tư vấn tâm lý học đường ẩn danh & đồng hành an toàn cùng học sinh"
)
st.info(
    "🔒 **Cam kết bảo mật tuyệt đối:** Ứng dụng không yêu cầu đăng nhập, không ghi nhận danh tính, không lưu lại nội dung tin nhắn và không gửi về cho giáo viên."
)

# TÍNH NĂNG 2: TRẠM DỪNG BÌNH TĨNH & GIẢI TỎA CẢM XÚC TỨC THÌ
with st.expander("🧘 Trạm Dừng Bình Tĩnh (Giải tỏa cơn bốc đồng tức thì)", expanded=False):
    tab_breath, tab_tear = st.tabs(["🌬️ Hít thở sâu 4-7-8", "🗑️ Viết rồi xé bỏ"])

    with tab_breath:
        st.write(
            "Nếu bạn đang rất tức giận, tim đập nhanh hoặc muốn khóc, hãy bấm nút dưới đây và làm theo nhịp thở để lấy lại sự kiểm soát trước khi hành động:"
        )
        if st.button("Bắt đầu nhịp thở 4-7-8 (1 chu kỳ)"):
            box = st.empty()
            # Hít vào 4 giây
            for i in range(4, 0, -1):
                box.info(f"🌿 **HÍT VÀO** từ từ bằng mũi... ({i}s)")
                time.sleep(1)
            # Giữ hơi 7 giây
            for i in range(7, 0, -1):
                box.warning(f"⏸️ **GIỮ HƠI** và thả lỏng hai vai... ({i}s)")
                time.sleep(1)
            # Thở ra 8 giây
            for i in range(8, 0, -1):
                box.success(f"💨 **THỞ RA** nhẹ nhàng bằng miệng... ({i}s)")
                time.sleep(1)
            box.info("✨ Tốt lắm! Cảm xúc của bạn đã dần dịu xuống rồi đấy.")

    with tab_tear:
        st.write(
            "Trút hết những uất ức, tức giận mà bạn không dám nói với ai vào đây, sau đó bấm **Xé bỏ & Thổi bay** để giải phóng chúng mà không làm tổn thương ai."
        )
        vent_text = st.text_area(
            "Xả giận tự do (Nội dung này sẽ biến mất hoàn toàn khi bấm nút):",
            key="vent_box",
            height=100,
        )
        if st.button("🔥 Xé bỏ & Thổi bay"):
            st.success("Tất cả những bực bội đã được xóa bỏ hoàn toàn. Bạn rất dũng cảm khi không dùng bạo lực để đáp trả!")

st.divider()

# KHUNG NHẬP TÌNH HUỐNG THAM VẤN
col_input1, col_input2 = st.columns([2, 1])

with col_input1:
    user_question = st.text_area(
        "Em đang gặp chuyện gì hoặc có điều gì bận lòng cần chuyên gia lắng nghe?",
        placeholder="Ví dụ: Bạn thân nói xấu sau lưng em; Em bị các bạn tẩy chay không rõ lý do; Em rất muốn đánh bạn vì bị trêu chọc ngoại hình...",
        height=130,
    )

with col_input2:
    selected_topic = st.selectbox(
        "Chủ đề liên quan đến chuyện này:",
        [
            "Mâu thuẫn bạn bè",
            "Áp lực học tập / Thi cử",
            "Gia đình & Cha mẹ",
            "Bắt nạt / Tẩy chay",
            "Bất an về bản thân",
            "Khác",
        ],
    )

# TÍNH NĂNG 4: BỘ LỌC BÁO ĐỘNG ĐỎ (SOS ALERT)
CRITICAL_KEYWORDS = [
    "tự tử", "tự hại", "cắt tay", "chết đi", "đánh hội đồng",
    "quay clip", "lột đồ", "đe dọa giết", "mang dao", "vũ khí",
]

is_emergency = any(kw in user_question.lower() for kw in CRITICAL_KEYWORDS) if user_question else False

if is_emergency:
    st.error(
        """
        🚨 **THÔNG BÁO HỖ TRỢ KHẨN CẤP:**
        Tình huống của em có dấu hiệu nguy cơ tổn hại nghiêm trọng. Em không phải gánh chịu điều này một mình!
        - 📞 **Tổng đài Quốc gia Bảo vệ Trẻ em: 111** (Gọi miễn phí 24/7, luôn lắng nghe và bảo vệ em ngay lập tức).
        - 🏫 **Phòng Tư vấn Tâm lý / Ban Giám hiệu THCS Phan Đình Phùng:** Hãy gặp trực tiếp thầy cô để được bảo vệ an toàn.
        """
    )

# NÚT GỬI CÂU HỎI
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key) if api_key else None

if st.button("Lắng nghe & Cho em lời khuyên", type="primary"):
    if not user_question.strip():
        st.warning("Em hãy viết một vài dòng về tình huống của mình nhé.")
    elif not client:
        st.error("Chưa cấu hình API Key. Vui lòng kiểm tra lại mục Secrets trên Streamlit Cloud.")
    else:
        with st.spinner("Chuyên gia đang suy ngẫm để tìm hướng giải quyết tốt nhất cho em..."):
            candidate_models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-3.8-flash"]
            response = None
            last_err = None

            for mod in candidate_models:
                try:
                    response = client.models.generate_content(
                        model=mod,
                        contents=user_question,
                        config={
                            "system_instruction": SYSTEM_PROMPT,
                            "max_output_tokens": 1000,
                            "temperature": 0.6,
                        },
                    )
                    if response and response.text:
                        break
                except Exception as err:
                    last_err = err
                    continue

            if response and response.text:
                stats["total_questions"] += 1
                stats["topics"][selected_topic] = stats["topics"].get(selected_topic, 0) + 1
                save_stats(stats)

                st.session_state["raw_response"] = response.text
                st.session_state["has_new_reply"] = True
            else:
                st.error(f"Máy chủ đang bận xử lý nhiều lượt truy cập cùng lúc, em vui lòng bấm gửi lại sau vài giây nhé! (Chi tiết: {last_err})")

# TÍNH NĂNG 3: HIỂN THỊ PHẢN HỒI GÓC NHÌN 3 CHIỀU
if st.session_state.get("has_new_reply", False):
    reply_text = st.session_state.get("raw_response", "")
    st.markdown("### 💬 Lời gửi gắm từ Chuyên gia Tâm lý:")

    part1 = ""
    part2 = ""
    part3 = ""

    if "[PHAN_1:" in reply_text and "[PHAN_2:" in reply_text and "[PHAN_3:" in reply_text:
        try:
            p1_raw = reply_text.split("[PHAN_1:")[1].split("[PHAN_2:")[0]
            p2_raw = reply_text.split("[PHAN_2:")[1].split("[PHAN_3:")[0]
            p3_raw = reply_text.split("[PHAN_3:")[1]

            part1 = p1_raw.replace("THẤU HIỂU & GỌI TÊN CẢM XÚC]", "").strip()
            part2 = p2_raw.replace("GÓC NHÌN ĐA CHIỀU]", "").strip()
            part3 = p3_raw.replace("KẾ HOẠCH HÀNH ĐỘNG VĂN MINH]", "").strip()
        except Exception:
            part1 = reply_text
    else:
        part1 = reply_text

    if part2 and part3:
        ans_tab1, ans_tab2, ans_tab3 = st.tabs([
            "❤️ 1. Thấu hiểu cảm xúc",
            "🔍 2. Góc nhìn đa chiều",
            "🧭 3. Kế hoạch hành động",
        ])
        with ans_tab1:
            st.markdown(part1)
        with ans_tab2:
            st.markdown(part2)
        with ans_tab3:
            st.markdown(part3)
    else:
        st.markdown(reply_text)

    # KHẢO SÁT CHẤT LƯỢNG ẨN DANH
    st.divider()
    st.write("**Lời khuyên này có giúp ích cho em không?**")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        if st.button("👍 Giúp em bình tĩnh & nhẹ lòng hơn"):
            stats["helpful_yes"] += 1
            save_stats(stats)
            st.success("Cảm ơn em! Chúc em luôn tự tin và bình an.")
            st.session_state["has_new_reply"] = False
    with f_col2:
        if st.button("👎 Em vẫn còn thấy bối rối"):
            stats["helpful_no"] += 1
            save_stats(stats)
            st.info("Đừng nản lòng nhé, em có thể thử diễn đạt rõ hơn hoặc tìm người lớn tin cậy để chia sẻ trực tiếp!")
            st.session_state["has_new_reply"] = False

# TÍNH NĂNG 5: SIDEBAR MINH BẠCH BỨC TRANH TÂM LÝ HỌC ĐƯỜNG
with st.sidebar:
    st.header("📊 Bức Tranh Hoạt Động")
    st.caption("Dữ liệu thống kê hoàn toàn ẩn danh, phục vụ đánh giá thực tiễn của dự án.")

    st.metric("Tổng lượt tham vấn", stats["total_questions"])

    total_feedbacks = stats["helpful_yes"] + stats["helpful_no"]
    helpful_rate = (stats["helpful_yes"] / total_feedbacks * 100) if total_feedbacks > 0 else 0
    st.metric("Tỷ lệ phản hồi hữu ích", f"{helpful_rate:.1f}%")

    st.divider()
    st.subheader("📌 Phân bổ chủ đề bận lòng")
    # Biểu đồ thanh phân bổ chủ đề
    st.bar_chart(stats.get("topics", {}))

    st.caption("🔒 *Dữ liệu chỉ thống kê số lần chọn chủ đề, không lưu bất kỳ nội dung cá nhân nào.*")
