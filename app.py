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
def calculate_bmi(weight, height_cm):
    try:
        height_m = height_cm / 100
        return round(weight / (height_m ** 2), 1)
    except:
        return None

def interpret_bmi(bmi):
    if not bmi or bmi == 0:
        return "ไม่มีข้อมูล"
    elif bmi > 30:
        return "อ้วนมาก"
    elif 25 <= bmi <= 30:
        return "อ้วน"
    elif 23 <= bmi < 25:
        return "น้ำหนักเกิน"
    elif 18.5 <= bmi < 23:
        return "ปกติ"
    else:
        return "ผอม"

def show_bmi(df):
    st.header("⚖️ น้ำหนัก / ส่วนสูง / BMI")

    year_options = [str(y) for y in range(61, 69)]
    selected_year = st.selectbox("เลือกปี พ.ศ.", year_options[::-1])

    weight_col = f"น้ำหนัก{selected_year}"
    height_col = f"ส่วนสูง{selected_year}"
    bmi_col = f"BMI{selected_year}"
    waist_col = f"รอบเอว{selected_year}"

    weight = df.iloc[0].get(weight_col)
    height = df.iloc[0].get(height_col)
    waist = df.iloc[0].get(waist_col)

    # แปลงค่าที่มีให้อยู่ในรูป float ถ้าเป็นไปได้
    try:
        weight = float(weight)
    except:
        weight = None

    try:
        height = float(height)
    except:
        height = None

    try:
        waist = float(waist)
    except:
        waist = None

    # คำนวณ BMI จาก weight & height
    bmi = calculate_bmi(weight, height)
    bmi_result = interpret_bmi(bmi)

    # แสดงผล
    st.markdown(f"**น้ำหนัก:** {weight if weight else '-'} กก.")
    st.markdown(f"**ส่วนสูง:** {height if height else '-'} ซม.")
    st.markdown(f"**รอบเอว:** {waist if waist else '-'} ซม.")
    st.markdown(f"**BMI:** {bmi if bmi else '-'}")
    st.success(f"แปลผล: {bmi_result}")

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
