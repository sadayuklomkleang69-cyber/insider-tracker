import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta  # สำหรับคำนวณ RSI ของจริง

# --- 1. CONFIG & ASSETS ---
st.set_page_config(layout="wide", page_title="Chairman Nu Command Center")

symbols = ["TSM", "NVDA", "MU", "MSFT", "AVGO", "GOOGL", "PLTR", "ARM", "AMD", "AMZN", "ASML", "RKLB", "NBIS"]

@st.cache_data(ttl=300) # Update ทุก 5 นาที
def fetch_realtime_data(tickers):
    data_list = {}
    for ticker in tickers:
        try:
            # ดึงข้อมูลย้อนหลังเพื่อคำนวณ RSI
            df = yf.download(ticker, period="1mo", interval="1d", progress=False)
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                prev_price = df['Close'].iloc[-2]
                change_pct = ((current_price - prev_price) / prev_price) * 100
                
                # คำนวณ RSI (14 days)
                rsi = ta.rsi(df['Close'], length=14).iloc[-1]
                
                data_list[ticker] = {
                    "Price": current_price,
                    "Today_%": change_pct,
                    "RSI": rsi
                }
        except:
            continue
    return data_list

# --- 2. EXECUTION ---
st.title("🚀 Chairman Nu Command Center V17.1 (Real-time)")

with st.spinner('กำลังดึงข้อมูลจากดาวเทียม...'):
    real_data = fetch_realtime_data(symbols)

# แสดงผล Dashboard
# (ส่วนของการแสดง Metric และ Table ใช้โครงเดิมของท่านได้เลย แต่เปลี่ยนตัวแปรจากสุ่มเป็น real_data)
