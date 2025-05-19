import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="ระบบรายงานสุขภาพ", layout="centered")

# โหลดจาก Secrets
service_account_info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)

# โหลดข้อมูลจาก Google Sheets
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1B_W02AlW7RoV2_qbOHAfVTTYUkKgfyqvjl_IgqQVmzc")
worksheet = spreadsheet.sheet1
df = pd.DataFrame(worksheet.get_all_records())
df['เลขบัตรประชาชน'] = df['เลขบัตรประชาชน'].astype(str)

# ฟังก์ชันแปลผล BMI
def interpret_bmi(bmi):
    if bmi < 18.5:
        return "ผอมเกินไป"
    elif bmi < 23:
        return "ปกติ"
    elif bmi < 25:
        return "น้ำหนักเกิน"
    elif bmi < 30:
        return "อ้วนระดับ 1"
    else:
        return "อ้วนระดับ 2"

# ฟังก์ชันแสดงหมวด BMI
def show_bmi(df):
    st.header("⚖️ น้ำหนัก / ส่วนสูง / BMI")

    year_options = [str(y) for y in range(61, 69)]
    selected_year = st.selectbox("เลือกปี พ.ศ.", year_options[::-1])

    weight_col = f"น้ำหนัก{selected_year}"
    height_col = f"ส่วนสูง{selected_year}"
    bmi_col = f"BMI{selected_year}"
    waist_col = f"รอบเอว{selected_year}"

    try:
        weight = float(df.iloc[0][weight_col])
        height_cm = float(df.iloc[0][height_col])
        bmi = float(df.iloc[0][bmi_col])
        waist = float(df.iloc[0][waist_col])

        st.metric("น้ำหนัก (กก.)", weight)
        st.metric("ส่วนสูง (ซม.)", height_cm)
        st.metric("BMI", bmi)
        st.metric("รอบเอว (ซม.)", waist)
        st.success(f"แปลผล: {interpret_bmi(bmi)}")

    except:
        st.warning("⚠️ ไม่มีข้อมูลในปีที่เลือก")

# --- หน้าแรกของระบบ ---
st.title("👨‍⚕️ ระบบรายงานผลตรวจสุขภาพ")
id_card = st.text_input("กรอกเลขบัตรประชาชน 13 หลัก")

if id_card:
    person = df[df["เลขบัตรประชาชน"] == id_card]

    if person.empty:
        st.error("ไม่พบข้อมูลในระบบ")
    else:
        df = person  # ใช้ข้อมูลของคนนั้น
        name = df.iloc[0]["ชื่อ-สกุล"]
        st.success(f"คุณ {name}")

        st.subheader("📂 กรุณาเลือกหมวดหมู่:")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("⚖️ น้ำหนัก / BMI"):
                show_bmi(df)

        with col2:
            if st.button("🩸 ผลตรวจเลือด"):
                st.info("ฟังก์ชันนี้ยังไม่เปิดใช้งาน")

        with col3:
            if st.button("💓 ความดัน / ชีพจร"):
                st.info("ฟังก์ชันนี้ยังไม่เปิดใช้งาน")
