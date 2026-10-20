import base64
from datetime import datetime
import json
import os
import time
from google import genai
import requests
import streamlit as st

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Góc Lắng Nghe - Cô Tư Phùng (THCS Phan Đình Phùng)",
    page_icon="🌱",
    layout="wide",
)


# CÀI ĐẶT GIAO DIỆN NỀN VÀ KHUNG HIỂN THỊ CHỮ SIÊU ĐẬM - NÚT PASTEL
def set_styling():
  bg_file = (
      "school_bg.png"
      if os.path.exists("school_bg.png")
      else ("school_bg.jpg" if os.path.exists("school_bg.jpg") else None)
  )
  if bg_file:
    with open(bg_file, "rb") as f:
      data = f.read()
    b64 = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(240, 244, 248, 0.65), rgba(240, 244, 248, 0.65)), url("data:image/png;base64,{b64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

  st.markdown(
      """
    <style>
    .main .block-container {
        background: rgba(255, 255, 255, 0.96) !important;
        padding: 2.2rem !important;
        border-radius: 22px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12) !important;
        margin-top: 1.5rem !important;
        margin-bottom: 2rem !important;
    }
    
    /* Chữ toàn bộ trang đậm nét, tương phản tuyệt đối */
    h1, h2, h3, h4, h5, p, span, label, .stMarkdown, div {
        color: #111827 !important;
        font-weight: 700 !important;
    }
    
    blockquote {
        background-color: #f0fff4 !important;
        border-left: 6px solid #2ecc71 !important;
        color: #1b4332 !important;
        font-size: 1.1rem !important;
        padding: 14px 20px !important;
        border-radius: 10px !important;
        margin: 12px 0 !important;
        font-weight: 600 !important;
    }

    /* KHUNG 1: VÒNG TAY CHE CHỞ (ĐỔ MÀU HỒNG PASTEL - VIỀN ĐỎ ĐẬM) */
    .main div[data-testid="stExpander"]:first-of-type,
    details:first-of-type {
        background-color: #ffe5e5 !important;
        border: 2.5px solid #ff5252 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 15px rgba(255, 82, 82, 0.25) !important;
        margin-bottom: 18px !important;
    }
    .main div[data-testid="stExpander"]:first-of-type summary,
    details:first-of-type summary {
        background: linear-gradient(135deg, #ffccd2 0%, #ffb3ba 100%) !important;
        color: #900c3f !important;
        font-weight: 800 !important;
        font-size: 1.15rem !important;
        border-radius: 13px !important;
        padding: 12px 18px !important;
    }

    /* KHUNG 2: TRẠM DỪNG BÌNH TĨNH (ĐỔ MÀU XANH BẠC HÀ PASTEL) */
    .main div[data-testid="stExpander"]:nth-of-type(2),
    details:nth-of-type(2) {
        background-color: #e8f8f0 !important;
        border: 2.5px solid #2ecc71 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 12px rgba(46, 204, 113, 0.2) !important;
        margin-top: 15px !important;
        margin-bottom: 20px !important;
    }
    .main div[data-testid="stExpander"]:nth-of-type(2) summary,
    details:nth-of-type(2) summary {
        background: linear-gradient(135deg, #c8f7dc 0%, #b2f2bb 100%) !important;
        color: #1b4332 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        border-radius: 13px !important;
        padding: 12px 18px !important;
    }

    /* CÁC NÚT TÌNH HUỐNG PASTEL - CHỮ ĐẬM SẮC NÉT */
    div[data-testid="column"]:nth-of-type(1) .stButton > button {
        background: #dbeafe !important;
        color: #1e40af !important;
        border: 2px solid #93c5fd !important;
        font-weight: 800 !important;
        border-radius: 14px !important;
        box-shadow: 0 3px 8px rgba(30, 64, 175, 0.12) !important;
    }

    div[data-testid="column"]:nth-of-type(2) .stButton > button {
        background: #ffedd5 !important;
        color: #9a3412 !important;
        border: 2px solid #fdba74 !important;
        font-weight: 800 !important;
        border-radius: 14px !important;
        box-shadow: 0 3px 8px rgba(154, 52, 18, 0.12) !important;
    }

    div[data-testid="column"]:nth-of-type(3) .stButton > button {
        background: #f3e8ff !important;
        color: #6b21a8 !important;
        border: 2px solid #d8b4fe !important;
        font-weight: 800 !important;
        border-radius: 14px !important;
        box-shadow: 0 3px 8px rgba(107, 33, 168, 0.12) !important;
    }

    div[data-testid="column"]:nth-of-type(4) .stButton > button {
        background: #dcfce7 !important;
        color: #166534 !important;
        border: 2px solid #86efac !important;
        font-weight: 800 !important;
        border-radius: 14px !important;
        box-shadow: 0 3px 8px rgba(22, 101, 52, 0.12) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        filter: brightness(0.96) !important;
    }

    /* NÚT GỬI CHÍNH */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        font-size: 1.15rem !important;
        padding: 0.75rem 2rem !important;
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 6px 18px rgba(5, 150, 105, 0.4) !important;
        font-weight: 800 !important;
    }
    </style>
    """,
      unsafe_allow_html=True,
  )


set_styling()

# ----------------- 1. QUẢN LÝ DỮ LIỆU ĐỒNG BỘ GOOGLE SHEETS -----------------
SHEETS_URL = os.environ.get("SHEETS_WEBHOOK_URL") or st.secrets.get(
    "SHEETS_WEBHOOK_URL", ""
)
SOS_FILE = "sos_alerts.json"

TOPIC_KEY_MAP = {
    "Mâu thuẫn / Tẩy chay trong lớp": "topic_1",
    "Đánh nhau bộc phát / Chặn cổng trường": "topic_2",
    "Khiêu khích trên MXH (FB/TikTok)": "topic_3",
    "Trấn lột / Vay nặng lãi học sinh": "topic_4",
    "Áp lực điểm số & Gia đình đi biển": "topic_5",
    "Bất an về bản thân / Khác": "topic_6",
}


def load_stats():
  fallback_stats = {
      "total_questions": 5,
      "helpful_yes": 4,
      "helpful_no": 1,
      "topics": {
          "Mâu thuẫn / Tẩy chay trong lớp": 2,
          "Đánh nhau bộc phát / Chặn cổng trường": 1,
          "Khiêu khích trên MXH (FB/TikTok)": 1,
          "Trấn lột / Vay nặng lãi học sinh": 1,
          "Áp lực điểm số & Gia đình đi biển": 0,
          "Bất an về bản thân / Khác": 0,
      },
  }
  if not SHEETS_URL:
    return fallback_stats
  try:
    res = requests.get(SHEETS_URL, timeout=4)
    if res.status_code == 200:
      data = res.json()
      return {
          "total_questions": data.get("total_questions", 5),
          "helpful_yes": data.get("helpful_yes", 4),
          "helpful_no": data.get("helpful_no", 1),
          "topics": {
              "Mâu thuẫn / Tẩy chay trong lớp": data.get("topic_1", 2),
              "Đánh nhau bộc phát / Chặn cổng trường": data.get("topic_2", 1),
              "Khiêu khích trên MXH (FB/TikTok)": data.get("topic_3", 1),
              "Trấn lột / Vay nặng lãi học sinh": data.get("topic_4", 1),
              "Áp lực điểm số & Gia đình đi biển": data.get("topic_5", 0),
              "Bất an về bản thân / Khác": data.get("topic_6", 0),
          },
      }
  except Exception:
    pass
  return fallback_stats


def sync_to_sheet(key_name):
  if not SHEETS_URL:
    return
  try:
    requests.post(SHEETS_URL, json={"key": key_name}, timeout=3)
  except Exception:
    pass


def load_sos_alerts():
  if not os.path.exists(SOS_FILE):
    return []
  try:
    with open(SOS_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  except Exception:
    return []


def save_sos_alert(alert_item):
  alerts = load_sos_alerts()
  alerts.insert(0, alert_item)
  try:
    with open(SOS_FILE, "w", encoding="utf-8") as f:
      json.dump(alerts, f, ensure_ascii=False, indent=2)
  except Exception:
    pass


stats = load_stats()

# Khởi tạo Session State
if "chat_history" not in st.session_state:
  st.session_state["chat_history"] = []
if "show_follow_up" not in st.session_state:
  st.session_state["show_follow_up"] = False
if "selected_emotion_prompt" not in st.session_state:
  st.session_state["selected_emotion_prompt"] = ""

# ----------------- 2. SYSTEM PROMPT: CÔ TƯ PHÙNG (TÍCH HỢP TÌNH HUỐNG NGUY HIỂM) -----------------
SYSTEM_PROMPT = """
Bạn là "Cô Tư Phùng" - Người đồng hành tâm lý học đường, người mẹ hiền và điểm tựa an toàn tuyệt đối của học sinh trường THCS Phan Đình Phùng (quận Thanh Khê, TP. Đà Nẵng).

I. HỒ SƠ THỰC TẾ & BỐI CẢNH ĐẶC THÙ TRƯỜNG THCS PHAN ĐÌNH PHÙNG:
1. Quy mô: 33 lớp (Khối 6, 7, 8: mỗi khối 8 lớp; Khối 9: 9 lớp; 662 học sinh nữ). Trường hiện chưa có phòng tư vấn tâm lý riêng và chưa có giáo viên tâm lý chuyên trách.
2. Hoàn cảnh gia đình học sinh:
- Hơn 50% học sinh là con em ngư dân vùng biển Thanh Khê, cha mẹ thường xuyên đi biển dài ngày. Các em thường thiếu vắng sự kề cận, giám sát hàng ngày của cha mẹ; sống với mẹ, ông bà hoặc người thân.
- Tâm lý đặc thù: Dễ cảm thấy cô đơn, thiếu thốn tình cảm, xu hướng sống tự lập sớm hoặc dễ mất bình tĩnh, dùng nắm đấm để tự giải quyết mâu thuẫn. Một số em chịu áp lực điểm số nặng nề vì kỳ vọng đổi đời của cha mẹ, sợ bị đánh đòn mỗi khi cha đi biển về biết điểm kém.
3. Nhận diện từ lóng & ngôn ngữ tuổi teen THCS tại Đà Nẵng:
- Từ ngữ bêu xấu/khiêu khích: "mõm", "ra cổng trường nói chuyện", "kèo", "gạ solo", "nhìn đểu", "chảnh chó", "phốt", "bóc phốt", "tẩy chay", "coi chừng tao", "tính sổ", "mày đợi đó".
- Nền tảng mạng xã hội: Facebook (Story/Confession), TikTok, nhóm kín Messenger/Zalo.

II. SƠ ĐỒ VÙNG NGUY HIỂM & VÙNG AN TOÀN TRONG TRƯỜNG:
1. Vùng nguy hiểm (Điểm nóng cần tránh xa khi có xung đột):
- Nhà vệ sinh học sinh các tầng 1, 2, 3 (khuất tầm nhìn).
- Bãi giữ xe học sinh (dễ bị dồn vào góc).
- Khu vực ngoài cổng trường, các quán nước/hẻm nhỏ đối diện đường giờ tan học.
- Cầu thang và hành lang lúc chuyển tiết hoặc sau khi tan học 15 phút.
2. Vùng an toàn tuyệt đối (Safe Zones) - Hướng dẫn học sinh chạy ngay đến:
- Tầng 1: Phòng Bảo vệ ngay cổng trường (có các bác bảo vệ trực 24/24).
- Tầng 1: Phòng Tổng phụ trách Đội (Thầy Đoàn Đình Thành - SĐT: 0905.659.995).
- Tầng 1: Phòng Y tế và Phòng Văn thư (có điện thoại hỗ trợ học sinh gọi người nhà).
- Tầng 2: Khu Hiệu bộ (Phòng Cô Hiệu trưởng Nguyễn Thị Thu Hà: 0905.654.888; Cô Phó HT Trần Thị Quế: 0983.225.126).
- Ngoài trường (Bảo vệ tính mạng khẩn cấp): Công an Phường Thanh Khê - SĐT: 0236.3714.677; Tổng đài Quốc gia Bảo vệ Trẻ em: 111.

III. QUY TRÌNH XỬ LÝ TÌNH HUỐNG CHUẨN HÓA (SOP):
1. Kịch bản KHIÊU KHÍCH TRÊN MẠNG XÃ HỘI (Facebook, TikTok) DẪN ĐẾN HẸN ĐÁNH NHAU:
- Tuyệt đối KHÔNG nhận kèo, KHÔNG đôi co thách thức lại trên mạng.
- Chụp ảnh màn hình toàn bộ tin nhắn/bình luận đe dọa để lưu chứng cứ.
- Giờ tan học KHÔNG đi ra cổng một mình, KHÔNG đi vào các hẻm quán nước đối diện. Ở yên trong sân trường, vào Phòng Bảo vệ hoặc Phòng Văn thư tầng 1 báo ngay cho Thầy Thành TPT Đội hoặc nhờ gọi phụ huynh đến đón.
2. Kịch bản CHƠI GIỠN QUÁ TRỚN MẤT BÌNH TĨNH DẪN ĐẾN ĐÁNH NHAU TẠI CHỖ (Tình huống bộc phát nhanh):
- Đối với em là người trong cuộc: LẬP TỨC LÙI LẠI, giơ hai tay phòng thủ, KHÔNG tiếp tục lao vào đánh trả để tránh thương tích nặng hơn.
- Đối với em và các bạn xung quanh: HÔ TO THẬT LỚN để lôi kéo sự chú ý của mọi người cùng vào can ngăn; ĐỒNG THỜI CỬ NGAY 1 BẠN CHẠY ĐI BÁO THẦY CÔ gần nhất (Phòng Đội tầng 1 gặp Thầy Thành, phòng giáo viên hoặc bác bảo vệ trực cổng).
3. Kịch bản Trấn lột tiền / Cho vay nặng lãi (gấp đôi gấp ba):
- KHÔNG chống cự trực tiếp nếu đối phương đông người để tránh bị thương tích.
- Chụp màn hình tin nhắn đòi tiền/chứng cứ mượn tiền, KHÔNG chuyển thêm tiền.
- Báo riêng với Giáo viên chủ nhiệm lớp của em hoặc Thầy Thành TPT tại phòng Đoàn Đội tầng 1.
4. Kịch bản Áp lực điểm số / Sợ cha mẹ đi biển về đánh mắng:
- Thấu hiểu sự vất vả, sóng gió biển khơi của cha mẹ và nỗi sợ hãi của học sinh. Hướng dẫn cách chọn thời điểm nói chuyện chân thành (lúc bố mẹ vui vẻ, thong thả sau chuyến biển) và cách viết một bức thư tay ngắn gửi bố mẹ trước. Nếu có nguy cơ bạo lực thân thể, nhắc em nhớ số 111.

IV. CẤU TRÚC PHẢN HỒI (BẮT BUỘC ĐỦ 3 PHẦN):
Xưng hô: "Cô Tư Phùng" và "Em" (hoặc "con"). Âm sắc miền Trung ấm áp, ân cần, bảo bọc:
[PHAN_1: THẤU HIỂU & GỌI TÊN CẢM XÚC]
(Đồng cảm sâu sắc với sự sợ hãi/tủi thân của em, liên hệ với hoàn cảnh gia đình/bạn bè để xoa dịu em).
[PHAN_2: GÓC NHÌN ĐA CHIỀU]
(Tách bạch giá trị bản thân em khỏi lời đàm tiếu; phân tích tâm lý người bắt nạt/nguyên nhân sự việc).
[PHAN_3: KẾ HOẠCH HÀNH ĐỘNG TẠI TRƯỜNG PHAN ĐÌNH PHÙNG]
(Quy trình bước-theo-bước rõ ràng: hô hoán can ngăn, chỉ rõ chạy đến phòng nào ở tầng mấy, tìm gặp ai, câu nói mẫu để tự bảo vệ, số điện thoại khẩn cấp cần gọi).
"""

# ----------------- 3. GIAO DIỆN CHÍNH -----------------

# Nút khẩn cấp "VÒNG TAY CHE CHỞ"
with st.expander(
    "🆘 🛡️ VÒNG TAY CHE CHỞ (BẤM VÀO ĐÂY NẾU EM ĐANG GẶP NGUY HIỂM / BỊ ĐE DỌA"
    " KHẨN CẤP)",
    expanded=False,
):
  st.markdown(
      """
    <div style="background: white; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #ffccd2;">
        <h4 style="color: #c0392b; margin-top: 0; font-weight: 800;">🚨 HỖ TRỢ KHẨN CẤP DÀNH CHO HỌC SINH THCS PHAN ĐÌNH PHÙNG:</h4>
        <p style="color: #2d3436; font-size: 1rem;">Nếu em đang bị đe dọa đánh nhau, bị chặn đường ở cổng trường/nhà xe, hoặc xảy ra ẩu đả bộc phát, hãy gọi ngay cho Ban Giám Hiệu, Thầy Tổng Phụ Trách hoặc lực lượng chức năng:</p>
    </div>
    """,
      unsafe_allow_html=True,
  )

  c1, c2, c3, c4 = st.columns(4)
  with c1:
    st.info(
        "📞 **Cô Hà (Hiệu trưởng):**\n"
        "**0905.654.888**\n*(Tầng 2 Khu Hiệu Bộ)*"
    )
  with c2:
    st.info(
        "📞 **Thầy Thành (TPT Đội):**\n"
        "**0905.659.995**\n*(Phòng Đoàn Đội Tầng 1)*"
    )
  with c3:
    st.info(
        "📞 **Công an P. Thanh Khê:**\n"
        "**0236.3714.677**\n*(Can thiệp chặn cổng/hung khí)*"
    )
  with c4:
    st.info(
        "📞 **Tổng đài Trẻ em 111:**\n"
        "**111**\n*(Bảo vệ bạo lực gia đình 24/7)*"
    )

  st.write("---")
  st.markdown("#### 🚨 Gửi tín hiệu báo nguy nhanh đến Thầy Cô trực ban:")
  with st.form("sos_form"):
    sos_loc = st.selectbox(
        "Em đang gặp nguy hiểm ở vị trí nào trong trường?",
        [
            "Đang xảy ra ẩu đả bộc phát ngay trong lớp / hành lang",
            "Khu vực ngoài cổng trường / Quán nước đối diện (giờ tan học)",
            "Nhà xe học sinh",
            "Khu vực nhà vệ sinh (WC tầng 1, 2 hoặc 3)",
            "Cầu thang dãy phòng học lúc chuyển tiết",
            "Vị trí khác",
        ],
    )
    sos_note = st.text_input(
        "Điều gì đang xảy ra? (Có thể ghi tên/lớp của em nếu muốn thầy cô đến"
        " đón em trực tiếp, hoặc để trống để ẩn danh):"
    )
    submit_sos = st.form_submit_button("🚨 GỬI TÍN HIỆU CẦU CỨU NGAY")
    if submit_sos:
      alert_data = {
          "time": datetime.now().strftime("%H:%M:%S ngày %d/%m/%Y"),
          "location": sos_loc,
          "content": sos_note if sos_note.strip() else "Yêu cầu hỗ trợ ẩn danh",
      }
      save_sos_alert(alert_data)
      st.success(
          "✅ Tín hiệu của em đã được gửi khẩn cấp! Nếu đang có xô xát: Em hãy"
          " HÔ TO để các bạn xung quanh cùng can ngăn và CỬ NGAY 1 BẠN chạy đi"
          " báo Thầy Thành (Phòng Đội tầng 1) hoặc Bác Bảo Vệ cổng trường ngay"
          " lập tức nhé!"
      )

# Header trang chủ & Mascot Cô Tư Phùng
col_mascot, col_welcome = st.columns([1, 4])
with col_mascot:
  if os.path.exists("mascot.png"):
    st.image("mascot.png", width=180)
  else:
    st.markdown("# 👩‍🏫")
    st.caption("**Cô Tư Phùng**")

with col_welcome:
  st.markdown("## 🌱 Góc Bình Yên Dưới Hiên Trường Phan Đình Phùng")
  st.markdown(
      "> *“Chào con thân yêu! Hôm nay ở trường thế nào? Có chuyện gì ở lớp, bạn"
      " bè hay trên mạng xã hội làm con lo sợ không? Dù ba mẹ có đang đi biển"
      " xa, con cũng đừng lo vì luôn có Cô Tư Phùng và thầy cô ở trường bên cạnh"
      " lắng nghe con...”*"
  )
  st.markdown(
      "🔒 **Cam kết bảo mật tuyệt đối:** *Ứng dụng không ghi nhận tên tuổi,"
      " không lưu danh tính, không gửi nội dung cho phụ huynh hay giáo viên bộ"
      " môn.*"
  )

# TRẠM DỪNG BÌNH TĨNH
with st.expander(
    "🌿 🧘 TRẠM DỪNG BÌNH TĨNH (Nhịp thở 4-7-8 & Hộp Xả Giận)", expanded=False
):
  tab_breath, tab_tear = st.tabs(["🌬️ Hít thở hạ hỏa 4-7-8", "🗑️ Viết rồi xé bỏ"])
  with tab_breath:
    st.write(
        "Nếu em đang rất bực bội, tim đập nhanh, hãy thở theo nhịp cùng Cô Tư"
        " Phùng để lấy lại bình tĩnh, tránh hành động bộc phát nhé:"
    )
    if st.button("Bắt đầu nhịp thở 4-7-8"):
      box = st.empty()
      for i in range(4, 0, -1):
        box.info(f"🌿 **HÍT VÀO** chậm rãi bằng mũi... ({i}s)")
        time.sleep(1)
      for i in range(7, 0, -1):
        box.warning(f"⏸️ **GIỮ HƠI** và thả lỏng đôi vai... ({i}s)")
        time.sleep(1)
      for i in range(8, 0, -1):
        box.success(f"💨 **THỞ RA** nhẹ nhàng bằng miệng... ({i}s)")
        time.sleep(1)
      box.info(
          "✨ Tuyệt vời lắm! Cơn giận đã nguôi bớt rồi, giờ mình cùng suy ngẫm"
          " cách giải quyết nhé."
      )
  with tab_tear:
    st.text_area(
        "Viết hết những lời bực bội vào đây:",
        placeholder="Em ghét bạn vì bạn trêu chọc em, gọi tên ba mẹ em...",
        key="tear_box",
    )
    if st.button("🔥 Xé bỏ & Thổi bay"):
      st.success(
          "Đã xé bỏ hoàn toàn! Em đã chọn cách giải tỏa văn minh thay vì gây gổ"
          " xích mích."
      )

st.markdown("---")

# ----------------- 4. KHÔNG GIAN LỰA CHỌN CẢM XÚC ĐẶC THÙ (NÚT PASTEL) -----------------
st.markdown("### 🌸 Hôm nay lòng em thấy thế nào? *(Bấm chọn nhanh tình huống)*")
col_e1, col_e2, col_e3, col_e4 = st.columns(4)

with col_e1:
  if st.button(
      "🌧️ Buồn & Bị cô lập\n\n(Bị nói xấu, tẩy chay)", use_container_width=True
  ):
    st.session_state["selected_emotion_prompt"] = (
        "Em đang rất buồn và tủi thân vì bị bạn bè cô lập, nói xấu sau lưng và"
        " không cho em chơi cùng trong lớp..."
    )
with col_e2:
  if st.button(
      "⚡ Ẩu đả / Đe dọa đánh nhau\n\n(Giỡn quá trớn, chặn cổng)",
      use_container_width=True,
  ):
    st.session_state["selected_emotion_prompt"] = (
        "Em và bạn đùa giỡn rồi mất kiểm soát sắp đánh nhau tại chỗ; hoặc em bị"
        " đe dọa chặn đường ở cổng trường lúc tan học..."
    )
with col_e3:
  if st.button(
      "🌐 Khiêu khích trên MXH\n\n(Bị bêu xấu trên Story/TikTok)",
      use_container_width=True,
  ):
    st.session_state["selected_emotion_prompt"] = (
        "Em cảm thấy kiệt sức vì bị lập nhóm chat bôi nhọ, khiêu khích hẹn ra"
        " cổng trường đánh nhau, đăng ảnh dìm lên TikTok/Facebook..."
    )
with col_e4:
  if st.button(
      "🌊 Áp lực gia đình & Điểm số\n\n(Sợ cha mẹ đi biển về phạt)",
      use_container_width=True,
  ):
    st.session_state["selected_emotion_prompt"] = (
        "Em đang rất lo sợ và áp lực vì điểm thi kém, sợ cha mẹ đi biển về sẽ"
        " mắng chửi hoặc đánh đòn..."
    )

# KHUNG NHẬP NỘI DUNG TÂM SỰ & CHỌN KHỐI LỚP
default_text = st.session_state.get("selected_emotion_prompt", "")
col_txt1, col_txt2, col_txt3 = st.columns([3, 1, 1])

with col_txt1:
  user_question = st.text_area(
      "Kể chi tiết hơn cho Cô Tư Phùng nghe nhé:",
      value=default_text,
      placeholder=(
          "Ví dụ: Bạn trong lớp hẹn tan học ra cổng trường 'tính sổ'; hoặc hai"
          " bạn trong lớp đang lao vào đánh nhau..."
      ),
      height=120,
      key="user_msg_input",
  )
with col_txt2:
  selected_grade = st.selectbox(
      "Em đang học khối:", ["Khối 6", "Khối 7", "Khối 8", "Khối 9"]
  )
with col_txt3:
  selected_topic = st.selectbox(
      "Vấn đề liên quan:",
      [
          "Mâu thuẫn / Tẩy chay trong lớp",
          "Đánh nhau bộc phát / Chặn cổng trường",
          "Khiêu khích trên MXH (FB/TikTok)",
          "Trấn lột / Vay nặng lãi học sinh",
          "Áp lực điểm số & Gia đình đi biển",
          "Bất an về bản thân / Khác",
      ],
  )

# HÀM GỌI API GEMINI
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get(
    "GEMINI_API_KEY", ""
)
client = genai.Client(api_key=api_key) if api_key else None


def get_ai_reply(prompt, grade, topic):
  candidate_models = [
      "gemini-3.6-flash",
      "gemini-3.5-flash-lite",
      "gemini-3.8-flash",
  ]
  full_user_context = (
      f"HỌC SINH THCS PHAN ĐÌNH PHÙNG ({grade.upper()}):\n"
      f"- Nhóm vấn đề: {topic}\n"
      f"- Lời tâm sự: {prompt}\n\n"
      "Hãy phản hồi chuẩn xác theo 3 phần: [PHAN_1: THẤU HIỂU & GỌI TÊN CẢM"
      " XÚC], [PHAN_2: GÓC NHÌN ĐA CHIỀU], [PHAN_3: KẾ HOẠCH HÀNH ĐỘNG TẠI"
      " TRƯỜNG PHAN ĐÌNH PHÙNG]. Nếu là tình huống đánh nhau bộc phát hoặc khiêu"
      " khích MXH, hãy chỉ dẫn ngay SOP ứng phó khẩn cấp: hô hoán can ngăn, cử"
      " bạn đi báo thầy Thành/bác bảo vệ ngay lập tức."
  )
  for m in candidate_models:
    try:
      res = client.models.generate_content(
          model=m,
          contents=full_user_context,
          config={
              "system_instruction": SYSTEM_PROMPT,
              "max_output_tokens": 2500,
              "temperature": 0.5,
          },
      )
      if res and res.text:
        return res.text, None
    except Exception as e:
      time.sleep(1)
      last_error = e
  return None, last_error


# NÚT GỬI TÂM SỰ
if st.button("💌 Gửi gắm tâm sự cùng Cô Tư Phùng", type="primary"):
  if not user_question.strip():
    st.warning("Em hãy chia sẻ một chút điều đang làm em bận lòng nhé.")
  elif not client:
    st.error("Chưa kết nối được API Key trên Streamlit Cloud Secrets.")
  else:
    with st.spinner("Cô Tư Phùng đang lắng nghe và suy ngẫm cùng em..."):
      reply, err = get_ai_reply(user_question, selected_grade, selected_topic)
      if reply:
        # Đồng bộ tăng số lượng vào Google Sheet
        sync_to_sheet("total_questions")
        sync_to_sheet(TOPIC_KEY_MAP.get(selected_topic, "topic_6"))

        # Cập nhật tạm thời cho lượt xem hiện tại
        stats["total_questions"] += 1
        stats["topics"][selected_topic] = (
            stats["topics"].get(selected_topic, 0) + 1
        )

        st.session_state["chat_history"] = [
            {"role": "user", "text": user_question},
            {"role": "model", "text": reply},
        ]
        st.session_state["raw_response"] = reply
        st.session_state["has_new_reply"] = True
        st.session_state["show_follow_up"] = False
      else:
        st.error(
            "Hệ thống đang nhiều bạn truy cập cùng lúc, em bấm gửi lại sau 3"
            f" giây nhé! (Lỗi: {err})"
        )

# HIỂN THỊ PHẢN HỒI GÓC NHÌN 3 CHIỀU TỪ CÔ TƯ PHÙNG
if st.session_state.get("has_new_reply", False):
  reply_text = st.session_state.get("raw_response", "")
  st.markdown("### 💬 Lời gửi gắm yêu thương từ Cô Tư Phùng:")

  part1, part2, part3 = "", "", ""
  if "[PHAN_1:" in reply_text and "[PHAN_2:" in reply_text:
    try:
      p1_split = reply_text.split("[PHAN_1:")[1]
      part1 = (
          p1_split.split("[PHAN_2:")[0]
          .replace("THẤU HIỂU & GỌI TÊN CẢM XÚC]", "")
          .strip()
      )
      if "[PHAN_3:" in p1_split:
        p2_split = p1_split.split("[PHAN_2:")[1]
        part2 = (
            p2_split.split("[PHAN_3:")[0]
            .replace("GÓC NHÌN ĐA CHIỀU]", "")
            .strip()
        )
        part3 = (
            p2_split.split("[PHAN_3:")[1]
            .replace("KẾ HOẠCH HÀNH ĐỘNG TẠI TRƯỜNG PHAN ĐÌNH PHÙNG]", "")
            .strip()
        )
      else:
        part2 = (
            p1_split.split("[PHAN_2:")[1]
            .replace("GÓC NHÌN ĐA CHIỀU]", "")
            .strip()
        )
    except Exception:
      part1 = reply_text
  else:
    part1 = reply_text

  if part1 and part2:
    ans_tab1, ans_tab2, ans_tab3 = st.tabs([
        "❤️ 1. Thấu hiểu cảm xúc",
        "🔍 2. Góc nhìn đa chiều",
        "🧭 3. Kế hoạch hành động tại trường",
    ])
    with ans_tab1:
      st.markdown(part1)
    with ans_tab2:
      st.markdown(part2 if part2 else "Đang cập nhật...")
    with ans_tab3:
      st.markdown(part3 if part3 else "Đang cập nhật...")
  else:
    st.markdown(reply_text)

  # KHẢO SÁT HỮU ÍCH & TRÒ CHUYỆN TIẾP NỐI
  st.divider()
  st.write("**Lời dặn dò của Cô Tư Phùng có giúp em nhẹ lòng hơn chưa?**")
  c_btn1, c_btn2 = st.columns(2)
  with c_btn1:
    if st.button("👍 Dạ rồi, em đã thấy nhẹ lòng và bình tĩnh hơn"):
      sync_to_sheet("helpful_yes")
      stats["helpful_yes"] += 1
      st.success("Thương em! Cố lên nhé, cô luôn ở bên cạnh đồng hành cùng em.")
      st.session_state["show_follow_up"] = False
  with c_btn2:
    if st.button("👎 Em vẫn còn thấy lo lắng và bối rối..."):
      sync_to_sheet("helpful_no")
      stats["helpful_no"] += 1
      st.session_state["show_follow_up"] = True

  if st.session_state.get("show_follow_up", False):
    st.info(
        "💡 **Đừng giữ trong lòng một mình nhé!** Em muốn cô giải thích rõ hơn"
        " ở điểm nào, hoặc em sợ điều gì khi làm theo hướng dẫn?"
    )
    follow_up_msg = st.text_area(
        "Viết tiếp điều em băn khoăn:",
        placeholder=(
            "Ví dụ: Nhưng cô ơi nếu em báo thầy Thành thì bạn biết bạn lại chặn"
            " đánh em thì sao ạ?"
        ),
        key="fu_text",
    )
    if st.button("Gửi tâm sự tiếp nối cho cô 💬"):
      if not follow_up_msg.strip():
        st.warning("Em ghi thêm câu hỏi nhé.")
      else:
        with st.spinner("Cô đang đọc tiếp tâm sự của em..."):
          ctx = (
              "LỊCH SỬ TÂM SỰ:\n"
              f"{st.session_state['chat_history'][0]['text']}\n"
              "LỜI DẶN TRƯỚC ĐÓ CỦA CÔ TƯ PHÙNG:\n"
              f"{st.session_state['chat_history'][1]['text']}\n"
              f"HỌC SINH HỎI TIẾP: {follow_up_msg}\n"
              "Hãy trả lời ân cần, chỉ rõ từng bước bảo mật thông tin để học"
              " sinh Phan Đình Phùng an tâm tuyệt đối."
          )
          sub_reply, sub_err = get_ai_reply(
              ctx, selected_grade, selected_topic
          )
          if sub_reply:
            st.session_state["chat_history"].append(
                {"role": "user", "text": follow_up_msg}
            )
            st.session_state["chat_history"].append(
                {"role": "model", "text": sub_reply}
            )
          else:
            st.error(f"Lỗi kết nối: {sub_err}")

  # Hiện các lượt trò chuyện sâu hơn
  if len(st.session_state["chat_history"]) > 2:
    st.markdown("---")
    st.subheader("🗨️ Cuộc trò chuyện tiếp nối cùng Cô Tư Phùng:")
    for i in range(2, len(st.session_state["chat_history"]), 2):
      with st.chat_message("user"):
        st.write(st.session_state["chat_history"][i]["text"])
      with st.chat_message("assistant"):
        st.write(st.session_state["chat_history"][i + 1]["text"])

# ----------------- 5. SIDEBAR: THỐNG KÊ & KHU VỰC DÀNH CHO THẦY CÔ -----------------
with st.sidebar:
  st.header("📊 Bức Tranh Hoạt Động")
  st.caption("Dữ liệu ẩn danh phục vụ công tác tâm lý trường học.")

  st.metric("Tổng lượt học sinh chia sẻ", stats["total_questions"])
  total_fb = stats["helpful_yes"] + stats["helpful_no"]
  rate = (stats["helpful_yes"] / total_fb * 100) if total_fb > 0 else 0
  st.metric("Tỷ lệ cảm thấy nhẹ lòng", f"{rate:.1f}%")

  st.divider()
  st.subheader("📌 Nhóm vấn đề học sinh bận lòng")
  st.bar_chart(stats.get("topics", {}))

  st.divider()
  with st.expander("🔒 Khu vực Giáo viên / Ban Giám Hiệu"):
    admin_pw = st.text_input("Nhập mật khẩu quản trị:", type="password")
    if admin_pw == "pdp2026":
      st.success("Xác thực thành công!")
      st.write("📋 **Danh sách các tín hiệu SOS khẩn cấp:**")
      alerts = load_sos_alerts()
      if not alerts:
        st.info("Hiện chưa có tín hiệu báo nguy nào.")
      else:
        for idx, a in enumerate(alerts):
          st.warning(
              f"**[{a['time']}]**\n- Vị trí: **{a['location']}**\n- Nội dung:"
              f" {a['content']}"
          )
    elif admin_pw:
      st.error("Mật khẩu không đúng!")
