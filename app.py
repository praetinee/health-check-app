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
def homepage(
