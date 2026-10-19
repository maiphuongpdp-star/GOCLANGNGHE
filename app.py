# CÀI ĐẶT ẢNH NỀN SÂN TRƯỜNG MỜ ẢO DỊU NHẸ
def set_bg():
    bg_file = "school_bg.png" if os.path.exists("school_bg.png") else ("school_bg.jpg" if os.path.exists("school_bg.jpg") else None)
    if bg_file:
        with open(bg_file, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: linear-gradient(rgba(255, 255, 255, 0.88), rgba(255, 255, 255, 0.88)), url("data:image/png;base64,{b64}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

set_bg()
