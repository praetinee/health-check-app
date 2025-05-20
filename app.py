import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# ================================
# 🔹 PAGE CONFIG
# ================================
st.set_page_config(page_title="ระบบรายงานผลตรวจสุขภาพ", layout="centered")

# ================================
# 🔹 HEADER
# ================================
st.markdown(
    """
    <div style='text-align: center; padding-top: 50px; padding-bottom: 10px;'>
        <h1 style='color: #006d77; font-size: 42px;'>ระบบรายงานผลตรวจสุขภาพ</h1>
        <h4 style='color: #4f4f4f;'>- กลุ่มงานอาชีวเวชกรรม รพ.สันทราย -</h4>
    </div>
    """,
    unsafe_allow_html=True
)

# ================================
# 🔹 เชื่อมต่อ Google Sheets
# ================================
@st.cache_data(ttl=600)
def load_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    service_account_info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1B_W02AlW7RoV2_qbOHAfVTTYUkKgfyqvjl_IgqQVmzc")
    worksheet = spreadsheet.sheet1
    df = pd.DataFrame(worksheet.get_all_records())
    df['เลขบัตรประชาชน'] = df['เลขบัตรประชาชน'].astype(str)
    return df

data_all = load_data()

# ================================
# 🔹 INPUT & ตรวจสอบ
# ================================
st.markdown("### 🔍 กรุณาใส่เลขบัตรประชาชน 13 หลัก")

citizen_id = st.text_input("หมายเลขบัตรประชาชน", max_chars=13, placeholder="กรอกเลขบัตรประชาชน", label_visibility="collapsed")

if st.button("ตรวจสอบ"):
    if not citizen_id:
        st.warning("⚠️ กรุณากรอกเลขบัตรประชาชนให้ครบถ้วน")
    elif len(citizen_id) != 13 or not citizen_id.isdigit():
        st.error("❌ เลขบัตรประชาชนไม่ถูกต้อง ต้องเป็นตัวเลข 13 หลัก")
    else:
        matched = data_all[data_all["เลขบัตรประชาชน"] == citizen_id]
        if not matched.empty:
            st.success("✅ พบข้อมูลในระบบ")
        else:
            st.error("❌ ไม่พบข้อมูลในระบบ กรุณาตรวจสอบอีกครั้ง")
