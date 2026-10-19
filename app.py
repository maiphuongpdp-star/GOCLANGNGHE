from datetime import datetime
import json
import os
import time
import streamlit as st
from google import genai

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Góc Lắng Nghe - Cô Tư Phùng (THCS Phan Đình Phùng)",
    page_icon="🌱",
    layout="wide",
)

# ----------------- 1. QUẢN LÝ DỮ LIỆU LƯU TRỮ -----------------
STATS_FILE = "stats.json"
SOS_FILE = "sos_alerts.json"


def load_stats():
  default_stats = {
      "total_questions": 0,
      "helpful_yes": 0,
      "helpful_no": 0,
      "topics": {
          "Mâu thuẫn bạn bè": 0,
          "Áp lực học tập / Điểm số": 0,
          "Gia đình & Cha mẹ": 0,
          "Bắt nạt / Trấn lột / Tẩy chay": 0,
          "Bạo lực mạng (Cyberbullying)": 0,
          "Bất an về bản thân / Khác": 0,
      },
  }
  if not os.path.exists(STATS_FILE):
    return default_stats
  try:
    with open(STATS_FILE, "r", encoding="utf-8") as f:
      data = json.load(f)
      for k in default_stats["topics"]:
        if k not in data.get("topics", {}):
          data.setdefault("topics", {})[k] = 0
      return data
  except Exception:
    return default_stats


def save_stats(stats):
  try:
    with open(STATS_FILE, "w", encoding="utf-8") as f:
      json.dump(stats, f, ensure_ascii=False, indent=2)
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

# ----------------- 2. SYSTEM PROMPT: CÔ TƯ PHÙNG (THCS PHAN ĐÌNH PHÙNG) -----------------
SYSTEM_PROMPT = """
Bạn là "Cô Tư Phùng" - Nhân vật người đồng hành tâm lý học đường ấm áp, nhân hậu và tận tụy của trường THCS Phan Đình Phùng (Thanh Khê, Đà Nẵng).

TRI THỨC THỰC TẾ VỀ TRƯỜNG THCS PHAN ĐÌNH PHÙNG:
1. Không gian trường:
- Phòng Đoàn Đội: Tầng 1 (dãy phòng chính). Bên ngoài hành lang có đặt "Hộp thư Điều em muốn nói" bằng giấy.
- Phòng Ban Giám Hiệu: Tầng 2 khu Hiệu bộ (Phòng Cô Hiệu trưởng Nguyễn Thị Thu Hà, Phòng Cô Phó Hiệu trưởng Trần Thị Quế).
- Phòng Giáo viên & Thư viện: Tầng 1-2, nơi các thầy cô thường nghỉ giờ ra chơi.
- Các "điểm nóng" dễ xảy ra va chạm/xích mích: Nhà vệ sinh các tầng 1, 2, 3; bãi giữ xe học sinh; khu vực trước cổng trường bên ngoài; hành lang lúc chuyển tiết hoặc 15 phút sau khi tan học.
2. Thầy cô luôn sẵn sàng lắng nghe và bảo vệ học sinh:
- Cô Nguyễn Thị Mai Phương (SĐT: 0945.215.665) & Cô Nguyễn Thị Hằng (SĐT: 0985.275.556): Phụ trách tư vấn tâm lý, giờ ra chơi có mặt tại phòng giáo viên hoặc thư viện.
- Thầy Đoàn Đình Thành: Tổng phụ trách Đội (SĐT trực ban: 0905.659.995), trực tại Phòng Đoàn Đội tầng 1 vào giờ ra chơi các ngày (trừ thứ 3).
- Cô Nguyễn Thị Thu Hà (Hiệu trưởng - 0905.654.888) & Cô Trần Thị Quế (Phó HT - 0983.225.126): Luôn lắng nghe, bảo vệ sự an toàn của học sinh.
3. Các vấn đề học sinh Phan Đình Phùng hay gặp phải:
- Bị trêu chọc ngoại hình, lôi tên ba mẹ ra chế giễu, cô lập không cho chơi chung, ép cho mượn tiền rồi đòi lãi, gọi người ngoài trường đến chặn đường.
- Bị bạo lực mạng: Lập nhóm chat Zalo/Messenger nói xấu, đăng ảnh dìm lên TikTok/Facebook, confession bôi nhọ, thách thức nhau.

PHONG CÁCH VÀ QUY TẮC PHẢN HỒI CỦA CÔ TƯ PHÙNG:
- Luôn xưng hô thân thương: "Cô Tư Phùng" và "Em" (hoặc "con"). Giọng điệu ấm áp, đồng cảm, dịu dàng, như người mẹ hiền/người cô giáo thân quen.
- Tuyệt đối KHÔNG gặng hỏi danh tính cá nhân.
- Lời khuyên PHẢI GẮN LIỀN VỚI THỰC TẾ TRƯỜNG PHAN ĐÌNH PHÙNG: Chỉ dẫn cụ thể vị trí lánh nạn an toàn (về phòng Đoàn Đội, tìm cô Mai Phương, cô Hằng ở phòng giáo viên, hoặc bỏ thư vào Hộp thư Điều em muốn nói).
- CẤU TRÚC PHẢN HỒI BẮT BUỘC 3 PHẦN CHO LƯỢT ĐẦU:
[PHAN_1: THẤU HIỂU & GỌI TÊN CẢM XÚC]
(Đồng cảm sâu sắc, xoa dịu tổn thương, khẳng định việc em buồn hay tức giận là hoàn toàn dễ hiểu).
[PHAN_2: GÓC NHÌN ĐA CHIỀU]
(Tách bạch giá trị bản thân em với hành vi sai trái của người khác; phân tích nguyên nhân tâm lý vì sao bạn lại làm vậy).
[PHAN_3: KẾ HOẠCH HÀNH ĐỘNG VĂN MINH]
(2-3 bước hành động khéo léo; câu nói mẫu để từ chối hoặc đối đáp tự tin; địa chỉ thầy cô trường Phan Đình Phùng em có thể tìm gặp ngay).
"""

# ----------------- 3. GIAO DIỆN CHÍNH -----------------

# Thanh thông báo & Nút khẩn cấp "VÒNG TAY CHE CHỞ"
st.markdown(
    """
    <style>
    .emergency-box {
        background: linear-gradient(135deg, #ff7675 0%, #d63031 100%);
        padding: 15px 20px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }
    .custom-card {
        background-color: #f8fbf8;
        padding: 18px;
        border-radius: 15px;
        border: 1px solid #d5ebd5;
        margin-bottom: 15px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

with st.expander(
    "🛡️ VÒNG TAY CHE CHỞ (BẤM VÀO ĐÂY NẾU EM ĐANG GẶP NGUY HIỂM / BỊ ĐE DỌA KHẨN"
    " CẤP)",
    expanded=False,
):
  st.error(
      "🚨 **HỖ TRỢ KHẨN CẤP DÀNH RIÊNG CHO HỌC SINH THCS PHAN ĐÌNH PHÙNG:**\n"
      "Nếu em đang bị đe dọa đánh nhau, bị chặn đường, hoặc cảm thấy cực kỳ"
      " hoảng loạn, hãy gọi ngay hoặc chọn vị trí để thầy cô can thiệp lập"
      " tức:"
  )
  col_hotline1, col_hotline2, col_hotline3 = st.columns(3)
  with col_hotline1:
    st.info(
        "📞 **Thầy Thành (TPT Đội):**\n"
        "**0905.659.995**\n*(Phòng Đoàn Đội Tầng 1)*"
    )
  with col_hotline2:
    st.info(
        "📞 **Cô Hà (Hiệu trưởng):**\n"
        "**0905.654.888**\n*(Tầng 2 Khu Hiệu Bộ)*"
    )
  with col_hotline3:
    st.info(
        "📞 **Tổng đài Quốc gia 111:**\n"
        "**111**\n*(Bảo vệ Trẻ em miễn phí 24/7)*"
    )

  st.write("---")
  st.subheader("Gửi tín hiệu báo nguy nhanh đến Tổ Hỗ Trợ Nhà Trường:")
  with st.form("sos_form"):
    sos_loc = st.selectbox(
        "Em đang gặp nguy hiểm ở vị trí nào trong trường?",
        [
            "Nhà xe học sinh",
            "Cầu thang dãy phòng học (Tầng 1/2/3)",
            "Khu vực ngoài cổng trường (giờ tan học)",
            "Khu vực nhà vệ sinh (WC tầng 1, 2 hoặc 3)",
            "Trong lớp học",
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
          "✅ Tín hiệu của em đã được gửi bảo mật đến hệ thống hỗ trợ khẩn cấp"
          " của trường! Thầy cô sẽ có mặt can thiệp sớm nhất. Em hãy di chuyển"
          " ngay về phía Phòng Đoàn Đội tầng 1 hoặc Phòng Y tế/Văn phòng để được"
          " an toàn nhé!"
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
      "> *“Chào em thân yêu! Hôm nay ở trường thế nào? Có chuyện gì ở lớp, bạn"
      " bè hay trên mạng xã hội làm em chưa vui không? Cứ ngồi xuống đây kể cho"
      " Cô Tư Phùng nghe nhé, mọi chuyện rồi sẽ ổn thôi...”*"
  )
  st.caption(
      "🔒 **Cam kết bảo mật tuyệt đối:** Ứng dụng không ghi nhận tên tuổi, không"
      " lưu danh tính, không gửi nội dung cho phụ huynh hay giáo viên bộ môn."
  )

# Banner sân trường nếu có
if os.path.exists("school_bg.jpg"):
  st.image("school_bg.jpg", use_container_width=True)

# TRẠM DỪNG BÌNH TĨNH
with st.expander(
    "🧘 Trạm Dừng Bình Tĩnh (Nhịp thở 4-7-8 & Hộp Xả Giận)", expanded=False
):
  tab_breath, tab_tear = st.tabs(["🌬️ Hít thở hạ hỏa 4-7-8", "🗑️ Viết rồi xé bỏ"])
  with tab_breath:
    st.write(
        "Nếu em đang rất uất ức, tim đập nhanh, hãy thở theo nhịp cùng Cô Tư"
        " Phùng để không hành động bộc phát nhé:"
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
          "✨ Tuyệt vời lắm! Cơn giận đã nguôi bớt rồi, giờ mình cùng bình tĩnh"
          " tìm cách giải quyết nhé."
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

# ----------------- 4. KHÔNG GIAN LỰA CHỌN CẢM XÚC -----------------
st.subheader("Hôm nay lòng em thấy thế nào?")
col_e1, col_e2, col_e3, col_e4 = st.columns(4)

with col_e1:
  if st.button(
      "🌧️ Em buồn & tủi thân lắm\n(Bị nói xấu, tẩy chay...)",
      use_container_width=True,
  ):
    st.session_state["selected_emotion_prompt"] = (
        "Em đang rất buồn và tủi thân vì bị bạn bè cô lập, nói xấu sau lưng và"
        " không cho em chơi cùng..."
    )
with col_e2:
  if st.button(
      "⚡ Em sợ hãi, bị đe dọa\n(Bị chặn đường, trấn lột...)",
      use_container_width=True,
  ):
    st.session_state["selected_emotion_prompt"] = (
        "Em đang rất sợ hãi vì bị một nhóm bạn đe dọa đánh nhau và chặn ở khu"
        " vực nhà xe / cầu thang..."
    )
with col_e3:
  if st.button(
      "🌐 Em mệt mỏi vì bạo lực mạng\n(Bị bêu xấu trên FB/TikTok...)",
      use_container_width=True,
  ):
    st.session_state["selected_emotion_prompt"] = (
        "Em cảm thấy kiệt sức vì bị lập nhóm chat bôi nhọ, cắt ghép ảnh chế dìm"
        " hàng trên mạng xã hội..."
    )
with col_e4:
  if st.button(
      "🍃 Em muốn tâm sự nhẹ nhàng\n(Áp lực học tập, chuyện riêng...)",
      use_container_width=True,
  ):
    st.session_state["selected_emotion_prompt"] = (
        "Em đang có nhiều áp lực về việc học và điểm số, muốn được nghe lời khuyên"
        " từ cô..."
    )

# KHUNG NHẬP NỘI DUNG TÂM SỰ
default_text = st.session_state.get("selected_emotion_prompt", "")
col_txt1, col_txt2 = st.columns([3, 1])
with col_txt1:
  user_question = st.text_area(
      "Kể chi tiết hơn cho Cô Tư Phùng nghe nhé:",
      value=default_text,
      placeholder=(
          "Ví dụ: Bạn thân trong lớp đem chuyện riêng của em kể cho lớp khác;"
          " Bạn cùng bàn hay lấy tên ba mẹ em ra trêu đùa trước lớp..."
      ),
      height=120,
      key="user_msg_input",
  )
with col_txt2:
  selected_topic = st.selectbox(
      "Chuyện này liên quan đến:",
      [
          "Mâu thuẫn bạn bè",
          "Áp lực học tập / Điểm số",
          "Gia đình & Cha mẹ",
          "Bắt nạt / Trấn lột / Tẩy chay",
          "Bạo lực mạng (Cyberbullying)",
          "Bất an về bản thân / Khác",
      ],
  )

# HÀM GỌI API GEMINI VỚI CƠ CHẾ DỰ PHÒNG CHUẨN XÁC
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get(
    "GEMINI_API_KEY", ""
)
client = genai.Client(api_key=api_key) if api_key else None


def get_ai_reply(prompt):
  candidate_models = [
      "gemini-3.6-flash",
      "gemini-3.5-flash-lite",
      "gemini-3.8-flash",
  ]
  for m in candidate_models:
    try:
      res = client.models.generate_content(
          model=m,
          contents=prompt,
          config={
              "system_instruction": SYSTEM_PROMPT,
              "max_output_tokens": 2500,
              "temperature": 0.6,
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
      reply, err = get_ai_reply(user_question)
      if reply:
        stats["total_questions"] += 1
        stats["topics"][selected_topic] = (
            stats["topics"].get(selected_topic, 0) + 1
        )
        save_stats(stats)

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
            .replace("KẾ HOẠCH HÀNH ĐỘNG VĂN MINH]", "")
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
      stats["helpful_yes"] += 1
      save_stats(stats)
      st.success("Thương em! Cố lên nhé, cô luôn ở bên cạnh đồng hành cùng em.")
      st.session_state["show_follow_up"] = False
  with c_btn2:
    if st.button("👎 Em vẫn còn thấy lo lắng và bối rối..."):
      stats["helpful_no"] += 1
      save_stats(stats)
      st.session_state["show_follow_up"] = True

  if st.session_state.get("show_follow_up", False):
    st.info(
        "💡 **Đừng giữ trong lòng một mình nhé!** Em muốn cô giải thích rõ hơn"
        " ở điểm nào, hoặc em sợ điều gì khi làm theo hướng dẫn?"
    )
    follow_up_msg = st.text_area(
        "Viết tiếp điều em băn khoăn:",
        placeholder=(
            "Ví dụ: Cô ơi nhưng nếu bạn ấy không chịu lắng nghe mà còn thách"
            " thức thì sao ạ?"
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
              "Hãy trả lời ân cần, chỉ rõ từng bước để học sinh Phan Đình Phùng"
              " biết cách ứng phó an toàn."
          )
          sub_reply, sub_err = get_ai_reply(ctx)
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
  # MỤC QUẢN TRỊ BÍ MẬT DÀNH CHO THẦY CÔ
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
