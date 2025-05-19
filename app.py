# =============================
# 🔹 IMPORT MODULES
# =============================
import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image

# =============================
# 🔹 PAGE CONFIG
# =============================
st.set_page_config(page_title="ระบบรายงานสุขภาพ", layout="centered")

# =============================
# 🔹 LOAD GOOGLE SHEET
# =============================
service_account_info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)

spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1B_W02AlW7RoV2_qbOHAfVTTYUkKgfyqvjl_IgqQVmzc")
worksheet = spreadsheet.sheet1
data_all = pd.DataFrame(worksheet.get_all_records())
data_all['เลขบัตรประชาชน'] = data_all['เลขบัตรประชาชน'].astype(str)

# =============================
# 🔹 HELPER FUNCTIONS
# =============================
def load_data_by_citizen_id(citizen_id):
    data = data_all[data_all['เลขบัตรประชาชน'] == citizen_id]
    if not data.empty:
        return data.reset_index(drop=True)
    else:
        return None

def calculate_bmi(weight, height_cm):
    try:
        height_m = height_cm / 100
        return round(weight / (height_m ** 2), 1)
    except:
        return None

def interpret_bmi(bmi):
    if not bmi or bmi == 0 or pd.isna(bmi):
        return "-"
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

# =============================
# 🔹 HOMEPAGE
# =============================
import streamlit.components.v1 as components

def homepage():
    components.iframe("https://github.com/praetinee/health-check-app/blob/main/index.html", height=650, scrolling=False)

    # แสดง input แยกถัดจากภาพ
    st.markdown("### ")
    st.markdown("### ")
    st.markdown("### ")
    st.markdown("## 🔍 กรุณาใส่เลขบัตรประชาชน 13 หลัก")
    id_input = st.text_input("หมายเลขบัตรประชาชน", max_chars=13, label_visibility="collapsed", placeholder="กรอกเลขบัตรประชาชน 13 หลัก")

    if st.button("ตรวจสอบ"):
        if id_input:
            st.session_state["citizen_id"] = id_input
            st.session_state["page"] = "report"
        else:
            st.warning("กรุณากรอกเลขบัตรประชาชนให้ครบถ้วน")

# =============================
# 🔹 SHOW BMI
# =============================
def show_bmi(df):
    st.header("⚖️ น้ำหนัก / ส่วนสูง / BMI รายปี")

    years = list(range(61, 69))  # พ.ศ. 2561 - 2568

    weights, heights, bmis, results = [], [], [], []

    for year in years:
        w_col = f"น้ำหนัก{year}"
        h_col = f"ส่วนสูง{year}"

        weight = df.iloc[0].get(w_col, None)
        height = df.iloc[0].get(h_col, None)

        try:
            weight = float(weight)
        except:
            weight = None

        try:
            height = float(height)
        except:
            height = None

        bmi = calculate_bmi(weight, height)
        result = interpret_bmi(bmi)

        weights.append(str(int(weight)) if weight else "-")
        heights.append(str(int(height)) if height else "-")
        bmis.append(f"{bmi:.1f}" if bmi else "-")
        results.append(result)

    years_display = [f"พ.ศ. 25{y}" for y in years]

    st.markdown("### 📆 ปีที่ตรวจ:")
    st.markdown(" / ".join(years_display))
    st.markdown("### ⚖️ น้ำหนัก (กก.):")
    st.markdown(" / ".join(weights))
    st.markdown("### 📏 ส่วนสูง (ซม.):")
    st.markdown(" / ".join(heights))
    st.markdown("### 🧮 BMI:")
    st.markdown(" / ".join(bmis))
    st.markdown("### ✅ แปลผล:")
    st.markdown(" / ".join(results))

# =============================
# 🔹 ROUTING (PAGE SWITCH)
# =============================
if "page" not in st.session_state:
    st.session_state["page"] = "home"

if st.session_state["page"] == "home":
    homepage()

elif st.session_state["page"] == "report":
    citizen_id = st.session_state.get("citizen_id", "")
    df = load_data_by_citizen_id(citizen_id)

    if df is not None:
        show_bmi(df)
        # 🔁 ต่อด้วย show_blood(df), show_ekg(df) ได้เลย
    else:
        st.error("ไม่พบข้อมูลในระบบ กรุณาตรวจสอบเลขบัตรประชาชนอีกครั้ง")
