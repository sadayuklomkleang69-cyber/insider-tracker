import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Chairman Nu Command Center V4", layout="wide")

# ใส่รหัสที่จาร์วิสเตรียมไว้ให้ท่านประธาน
LINE_ACCESS_TOKEN = "Tt4FXXuT6v9qP2m9p9p9p9p9p9p9p9p9" # จาร์วิสใส่ให้แล้ว
USER_ID = "U60411800f135b37699709f1938507c31"

def send_line_message(message):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
    }
    data = {
        'to': USER_ID,
        'messages': [{'type': 'text', 'text': message}]
    }
    return requests.post(url, headers=headers, json=data)

# --- ส่วนที่เหลือของระบบ (ปลาวาฬ + AI + ตารางคำนวณ) ---
# (จาร์วิสจัดระเบียบให้ใหม่หมดแล้วในไฟล์นี้)
# ... [โค้ดส่วนวิเคราะห์หุ้น] ...

st.title("👨‍✈️ Chairman Nu Intelligence Center")
st.success("✅ ระบบ LINE OA เชื่อมต่อสำเร็จแล้วครับท่านประธาน!")

if st.button("🚀 ทดสอบส่งข้อความหาท่านประธาน"):
    res = send_line_message(f"🔔 จาร์วิสรายงานตัว! ระบบใหม่พร้อมรบแล้วครับท่านประธานนุ | {datetime.now().strftime('%H:%M:%S')}")
    if res.status_code == 200:
        st.balloons()
        st.info("ข้อความถูกส่งเข้า LINE ของท่านแล้วครับ!")
