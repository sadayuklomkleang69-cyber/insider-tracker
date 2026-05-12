import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Chairman Nu Command Center V4.4", layout="wide")

LINE_ACCESS_TOKEN = "Tt4FXXuT6v9qP2m9p9p9p9p9p9p9p9p9" 
USER_ID = "U60411800f135b37699709f1938507c31"

def send_line_message(message):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'}
    data = {'to': USER_ID, 'messages': [{'type': 'text', 'text': message}]}
    try: return requests.post(url, headers=headers, json=data)
    except: return None

# --- 2. DATA FETCHING ---
watchlist = ['NVDA', 'TSM', 'MSFT', 'PLTR', 'UPST', 'SOFI', 'GOOGL', 'AMD', 'TSLA', 'ARM', 'MU']

@st.cache_data(ttl=600)
def fetch_all_data():
    all_data = []
    prices = {}
    for ticker in watchlist:
        try:
            t = yf.Ticker(ticker)
            live_p = t.info.get('regularMarketPrice') or t.info.get('currentPrice') or 0
            prices[ticker] = live_p
            df = t.insider_transactions
            if df is not None and not df.empty:
                df['Date'] = pd.to_datetime(df['Start Date'] if 'Start Date' in df.columns else df.index)
                df['Symbol'] = ticker
                df['DisplayPrice'] = df['Price'].apply(lambda x: live_p if x == 0 or pd.isna(x) else x)
                all_data.append(df)
        except: continue
    return pd.concat(all_data) if all_data else pd.DataFrame(), prices

# --- 3. MAIN LOGIC ---
with st.sidebar:
    st.title("👨‍✈️ Command Center")
    menu = st.radio("เลือกโหมด:", ["🐳 จับตาปลาวาฬ (ทุกรายการ)", "🧮 ตารางคำนวณ", "📡 ระบบ LINE"])
    st.info(f"อัปเดต: {datetime.now().strftime('%H:%M:%S')}")

try:
    full_df, current_prices = fetch_all_data()

    if menu == "🐳 จับตาป
