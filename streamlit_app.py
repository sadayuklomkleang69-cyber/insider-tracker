import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime

# --- 1. CONFIGURATION & DARK UI ---
st.set_page_config(page_title="Chairman Nu Command Center V5", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #121212; color: white; }
    h1, h2, h3 { color: #4FA3FF !important; }
    .buy-card { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 5px solid #2ECC71; margin-bottom: 10px; }
    .sell-card { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 5px solid #E74C3C; margin-bottom: 10px; }
    .metric-box { background-color: #262730; padding: 15px; border-radius: 10px; border: 1px solid #4FA3FF; }
    </style>
    """, unsafe_allow_html=True)

LINE_ACCESS_TOKEN = "Tt4FXXuT6v9qP2m9p9p9p9p9p9p9p9p9" 
USER_ID = "U60411800f135b37699709f1938507c31"

def send_line_message(message):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'}
    data = {'to': USER_ID, 'messages': [{'type': 'text', 'text': message}]}
    try: return requests.post(url, headers=headers, json=data)
    except: return None

# --- 2. DATA ENGINE ---
watchlist = ['NVDA', 'TSM', 'MSFT', 'PLTR', 'UPST', 'SOFI', 'GOOGL', 'AMD', 'TSLA', 'ARM', 'MU']

@st.cache_data(ttl=600)
def fetch_all_data():
    all_buys, all_sells = [], []
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
                
                buys = df[df['Text'].str.contains('Purchase', case=False, na=False)]
                sells = df[df['Text'].str.contains('Sale', case=False, na=False)]
                
                if not buys.empty: all_buys.append(buys)
                if not sells.empty: all_sells.append(sells)
        except: continue
        
    buy_df = pd.concat(all_buys) if all_buys else pd.DataFrame()
    sell_df = pd.concat(all_sells) if all_sells else pd.DataFrame()
    return buy_df, sell_df, prices

# --- 3
