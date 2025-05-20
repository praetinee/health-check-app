import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# ===============================
# PAGE CONFIG + FONTS
# ===============================
st.set_page_config(page_title="ระบบรายงานสุขภาพ", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun&display=swap');
    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# ===============================
# LOAD GOOGLE SHEETS
# ===============================
service_account_info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)

sheet_url = "https://docs.google.com/spreadsheets/d/1B_W02AlW7RoV2_qbOHAfVTTYUkKgfyqvjl_IgqQVmzc"
spreadsheet = client.open_by_url(sheet_url)
worksheet = spreadsheet.sheet1
df = pd.DataFrame(worksheet.get_all_records())
df['เลขบัตรประชาชน'] = df['เลขบัตรประชาชน'].astype(str)

# ===============================
# HEALTH FUNCTIONS
# ===============================
def calc_bmi(w, h):
    try:
        h = float(h)
        w = float(w)
        return round(w / ((h / 100) ** 2), 1)
    except:
        return None

def interpret_bmi(bmi):
    if not bmi: return "-"
    if bmi > 30: return "อ้วนมาก"
    elif bmi >= 25: return "อ้วน"
    elif bmi >= 23: return "น้ำหนักเกิน"
    elif bmi >= 18.5: return "ปกติ"
    else: return "ผอม"

def interpret_bp(sbp, dbp):
    try:
        sbp, dbp = float(sbp), float(dbp)
        if sbp == 0 or dbp == 0: return "-"
        if sbp >= 160 or dbp >= 100: return "ความดันโลหิตสูง"
        elif sbp >= 140 or dbp >= 90: return "ความดันสูงเล็กน้อย"
        elif sbp < 120 and dbp < 80: return "ความดันปกติ"
        else: return "ปกติค่อนข้างสูง"
    except:
        return "-"

def assess_waist(waist, threshold=90):
    try:
        waist = float(waist)
        if waist == 0: return "-"
        return "เกินเกณฑ์" if waist > threshold else "ปกติ"
    except:
        return "-"

# ===============================
# SEARCH UI
# ===============================
st.markdown("<h1 style='text-align:center;'>ระบบรายงานผลตรวจสุขภาพ</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center; color:gray;'>- กลุ่มงานอาชีวเวชกรรม รพ.สันทราย -</h4>", unsafe_allow_html=True)

citizen_id = st.text_input("กรอกเลขบัตรประชาชน", max_chars=13, placeholder="เช่น 1234567890123")

if st.button("ตรวจสอบ"):
    if not citizen_id.strip():
        st.warning("⚠️ กรุณากรอกเลขบัตรประชาชน")
    else:
        matched = df[df["เลขบัตรประชาชน"] == citizen_id.strip()]
        if matched.empty:
            st.error("ไม่พบข้อมูล กรุณาตรวจสอบอีกครั้ง")
        else:
            person = matched.iloc[0]
            st.success(f"✅ พบข้อมูล: {person.get('ชื่อ-สกุล', '-')}")
            st.markdown(f"**เพศ:** {person.get('เพศ', '-')}")

            # ปีที่จะแสดงผล
            years = list(range(61, 69))  # พ.ศ. 2561 - 2568
            display_years = [f"พ.ศ. 25{y}" for y in years]

            # เตรียมข้อมูล
            def get_values(prefix):
                return [person.get(f"{prefix}{y}", "-") for y in years]

            weights = get_values("น้ำหนัก")
            heights = get_values("ส่วนสูง")
            waists = get_values("รอบเอว")
            sbps = get_values("SBP")
            dbps = get_values("DBP")

            # คำนวณ BMI และผล
            bmis = []
            bmi_results = []
            bp_results = []
            waist_results = []

            for w, h, sbp, dbp, waist in zip(weights, heights, sbps, dbps, waists):
                bmi = calc_bmi(w, h)
                bmis.append(f"{bmi:.1f}" if bmi else "-")
                bmi_results.append(interpret_bmi(bmi))
                bp_results.append(interpret_bp(sbp, dbp))
                waist_results.append(assess_waist(waist))

            # สร้าง DataFrame แสดงผล
            summary_df = pd.DataFrame({
                "ปี พ.ศ.": display_years,
                "น้ำหนัก (กก.)": weights,
                "ส่วนสูง (ซม.)": heights,
                "รอบเอว (ซม.)": waists,
                "BMI": bmis,
                "แปลผล BMI": bmi_results,
                "ความดันโลหิต": bp_results,
                "ประเมินรอบเอว": waist_results,
            })

            st.markdown("### 📊 ผลประเมินสุขภาพรายปี")
            st.dataframe(summary_df.set_index("ปี พ.ศ.").T, use_container_width=True)
