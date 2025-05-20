import streamlit as st
import gspread
import pandas as pd
import json
from oauth2client.service_account import ServiceAccountCredentials

# ===== PAGE CONFIG =====
st.set_page_config(page_title="ระบบรายงานผลตรวจสุขภาพ", layout="centered")

# ===== HEADER STYLE =====
st.markdown(
    """
    <div style='text-align: center; padding-top: 50px; padding-bottom: 10px;'>
        <h1 style='color: #006d77; font-size: 42px;'>ระบบรายงานผลตรวจสุขภาพ</h1>
        <h4 style='color: #4f4f4f;'>- กลุ่มงานอาชีวเวชกรรม รพ.สันทราย -</h4>
    </div>
    """,
    unsafe_allow_html=True
)

# ===== เชื่อมต่อ Google Sheets =====
@st.cache_data
def load_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(st.secrets["GCP_SERVICE_ACCOUNT"]),
        scope
    )
    client = gspread.authorize(credentials)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1B_W02AlW7RoV2_qbOHAfVTTYUkKgfyqvjl_IgqQVmzc")
    worksheet = sheet.get_worksheet(0)  # ใช้ Sheet แรก
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    df['เลขบัตรประชาชน'] = df['เลขบัตรประชาชน'].astype(str)
    return df

df = load_google_sheet()

# ===== INPUT FORM =====
st.markdown("### 🔍 กรุณาใส่เลขบัตรประชาชน 13 หลัก")

citizen_id = st.text_input("หมายเลขบัตรประชาชน", max_chars=13, placeholder="กรอกเลขบัตรประชาชน", label_visibility="collapsed")

if st.button("ตรวจสอบ"):
    if not citizen_id:
        st.warning("กรุณากรอกเลขบัตรประชาชนให้ครบถ้วน")
    else:
        matched = df[df['เลขบัตรประชาชน'] == citizen_id]

        if matched.empty:
            st.error("ไม่พบข้อมูลในระบบ กรุณาตรวจสอบเลขบัตรอีกครั้ง")
        else:
            row = matched.iloc[0]
            st.success("✅ พบข้อมูลผู้ใช้งาน")
            st.markdown(f"**ชื่อ-สกุล:** {row['ชื่อ']} {row['สกุล']}")
            st.markdown(f"**เพศ:** {'ชาย' if row['คำนำหน้า'] in ['นาย', 'Mr.'] else 'หญิง'}")
