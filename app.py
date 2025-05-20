# =========================
# 🔹 IMPORT MODULES
# =========================
import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# =========================
# 🔹 PAGE CONFIG (ต้องมาก่อนทุกอย่าง)
# =========================
st.set_page_config(page_title="ระบบรายงานสุขภาพ", layout="centered")

# =========================
# 🔹 โหลดข้อมูลจาก Google Sheet
# =========================
service_account_info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)

sheet_url = "https://docs.google.com/spreadsheets/d/1B_W02AlW7RoV2_qbOHAfVTTYUkKgfyqvjl_IgqQVmzc"
spreadsheet = client.open_by_url(sheet_url)
worksheet = spreadsheet.sheet1
df = pd.DataFrame(worksheet.get_all_records())

# แปลงเลขบัตรประชาชนให้เป็น string เสมอ
df['เลขบัตรประชาชน'] = df['เลขบัตรประชาชน'].astype(str)

# =========================
# 🔹 ฟังก์ชันค้นหาข้อมูล
# =========================
def find_person_by_id(citizen_id):
    filtered = df[df["เลขบัตรประชาชน"] == citizen_id]
    if not filtered.empty:
        return filtered.iloc[0]
    return None

# =========================
# 🔹 UI
# =========================
st.markdown("<h1 style='text-align:center; color:#008080;'>ระบบรายงานผลตรวจสุขภาพ</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center; color:gray;'>- กลุ่มงานอาชีวเวชกรรม รพ.สันทราย -</h4>", unsafe_allow_html=True)

st.markdown("### 🔍 กรุณาใส่เลขบัตรประชาชน 13 หลัก")
citizen_id = st.text_input("เลขบัตรประชาชน", max_chars=13, label_visibility="collapsed", placeholder="กรอกเลขบัตรประชาชน")

if st.button("ตรวจสอบ"):
    if citizen_id.strip() == "":
        st.warning("⚠️ กรุณากรอกเลขบัตรประชาชน")
    else:
        row = find_person_by_id(citizen_id.strip())

        if row is not None:
            st.success("✅ พบข้อมูลผู้ใช้งาน")
            st.markdown(f"**ชื่อ-สกุล:** {row.get('ชื่อ-สกุล', '-')}")
            st.markdown(f"**เพศ:** {row.get('เพศ', '-')}")
            st.markdown(f"**อายุ:** {row.get('อายุ', '-')}")
        else:
            st.error("❌ ไม่พบข้อมูลในระบบ กรุณาตรวจสอบเลขบัตรประชาชนอีกครั้ง")
