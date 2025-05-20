import streamlit as st

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

# ===== INPUT FORM =====
st.markdown("## ")
st.markdown("### 🔍 กรุณาใส่เลขบัตรประชาชน 13 หลัก")

citizen_id = st.text_input("หมายเลขบัตรประชาชน", max_chars=13, placeholder="กรอกเลขบัตรประชาชน", label_visibility="collapsed")

if st.button("ตรวจสอบ"):
    if citizen_id:
        st.success(f"คุณกรอกเลขบัตรประชาชน: {citizen_id}")
        # ใส่ logic ตรวจสอบ/โหลดข้อมูลภายหลัง
    else:
        st.warning("กรุณากรอกเลขบัตรประชาชนให้ครบถ้วน")
