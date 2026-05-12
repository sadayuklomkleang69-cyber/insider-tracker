import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time
from datetime import datetime, timedelta

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V14.6", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

# --- UI ENHANCEMENT (NEON TACTICAL CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Kanit:wght@300;500&display=swap');
    .main { background-color: #050505; }
    h1, h2, h3 { font-family: 'Orbitron', 'Kanit', sans-serif; color: #00FFC8; text-shadow: 0 0 10px rgba(0, 255, 200, 0.5); }
    div[data-testid="stMetricValue"] { font-family: 'Orbitron', sans-serif; font-size: 2.2rem !important; color: #00FFC8 !important; }
    div[data-testid="stMetric"] { background: rgba(16, 20, 24, 0.9); border: 1px solid #30363D; border-left: 5px solid #00FFC8; padding: 20px; border-radius: 10px; }
    .news-card { background: linear-gradient(90deg, rgba(0,255,200,0.05), rgba(0,0,0,0)); border: 1px solid #30363D; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #00FFC8; }
    .news-tag { background: #00FFC8; color: #000; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-right: 8px; }
    .old-news { opacity: 0.6; border-left: 4px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# 2. ข้อมูลพอร์ต & หน่วยความจำข่าว (Persistence)
if 'my_assets' not in st.session_state:
    st.session_state.my_assets = {
        "TSM": {"Val": 55244.24, "PL": 10.28}, "NVDA": {"Val": 46038.54, "PL": 18.95},
        "MU": {"Val": 40188.92, "PL": 68.75}, "MSFT": {"Val": 27148.52, "PL": 4.69},
        "AVGO": {"Val": 25391.97, "PL": 18.89}, "GOOGL": {"Val": 24350.15, "PL": 22.86},
        "PLTR": {"Val": 16743.23, "PL": -7.75}, "ARM": {"Val": 16132.26, "PL": 29.81},
        "AMD": {"Val": 13374.89, "PL": 61.00}, "AMZN": {"Val": 12972.02, "PL": 18.21},
        "ASML": {"Val": 11166.77, "PL": 8.95}, "RKLB": {"Val": 6495.83, "PL": 41.11},
        "NBIS": {"Val": 2955.28, "PL": 16.69}
    }
if 'cash_balance' not in st.session_state: st.session_state.cash_balance = 2970.05
if 'news_archive' not in st.session_state: st.session_state.news_archive = []

# 3. Intelligence Engine (New Archiving Logic)
def update_intel_archive(ticker_list):
    current_time = datetime.now()
    # 1. คัดข่าวที่เก่ากว่า 3 วันออก
    st.session_state.news_archive = [n for n in st.session_state.news_archive 
                                    if datetime.strptime(n['FetchTime'], '%Y-%m-%d %H:%M') > current_time - timedelta(days=3)]
    
    # 2. สแกนหาข่าวใหม่
    new_found = []
    for sym in ["MU", "NVDA", "TSM", "GOOGL", "^GSPC"]:
        try:
            t_obj = yf.Ticker(sym)
            for n in t_obj.news[:2]:
                title = n.get('title')
                # เช็คว่าข่าวนี้นี้มีอยู่ในคลังหรือยัง (ป้องกันซ้ำ)
                if title and not any(archived['Title'] == title for archived in st.session_state.news_archive):
                    new_found.append({
                        "Tag": "MARKET" if sym == "^GSPC" else sym,
                        "Title": title,
                        "Source": n.get('publisher', 'Intel Source'),
                        "FetchTime": current_time.strftime('%Y-%m-%d %H:%M')
                    })
        except: continue
    
    # 3. เพิ่มข่าวใหม่เข้าไปในคลัง (เอาอันล่าสุดไว้บน)
    st.session_state.news_archive = new_found + st.session_state.news_archive

@st.cache_data(ttl=60)
def get_market_data(ticker_list):
    stock_results = {}
    for s in ticker_list:
        try:
            t = yf.Ticker(s)
            df = t.history(period="5d", interval="15m")
            if df.empty: continue
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            curr = float(df['Close'].iloc[-1])
            chg = ((curr - t.fast_info['previous_close']) / t.fast_info['previous_close']) * 100
            stock_results[s] = {"Price": curr, "Chg": chg, "RSI": rsi}
        except: continue
    return stock_results

# --- EXECUTION ---
update_intel_archive(list(st.session_state.my_assets.keys()))
m_data = get_market_data(list(st.session_state.my_assets.keys()))
total_wealth = sum(info['Val'] * (1 + (m_data.get(t, {}).get("Chg", 0) / 100)) for t, info in st.session_state.my_assets.items())

# --- HEADER ---
st.markdown("<h1 style='text-align: center;'>⚡ CHAIRMAN NU : INTELLIGENCE ARCHIVE ⚡</h1>", unsafe_allow_html=True)

col_info, col_actions = st.columns([3, 2])
with col_info:
    st.markdown(f"""<div style='background:rgba(16,20,24,0.9); padding:20px; border-radius:10px; border-left:5px solid #00FFC8;'>
    <span style='color:#888; font-size:0.8rem;'>💰 NET WORTH (REAL-TIME)</span><br>
    <span style='font-family:Orbitron; font-size:2rem; color:#00FFC8;'>{total_wealth:,.2f} THB</span>
    <span style='color:#FF4B4B; font-size:1rem;'> ({(total_wealth - 298225.25):+,.2f})</span>
    </div>""", unsafe_allow_html=True)
with col_actions:
    st.metric("🔥 กระสุนคงเหลือ", f"{st.session_state.cash_balance:,.2f} THB")
    with st.popover("⚙️ จัดการรบ"):
        target = st.selectbox("เป้าหมาย", list(st.session_state.my_assets.keys()))
        spent = st.number_input("งบประมาณ", min_value=0.0)
        if st.button("FIRE!"):
            if spent <= st.session_state.cash_balance:
                st.session_state.cash_balance -= spent
                st.session_state.my_assets[target]["Val"] += spent
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- NEWS SECTION (3-DAY PERSISTENCE) ---
st.subheader("🌐 GLOBAL INTEL ARCHIVE (ย้อนหลัง 3 วัน)")
if st.session_state.news_archive:
    for n in st.session_state.news_archive[:10]: # แสดง 10 ข่าวล่าสุดที่มีในคลัง
        st.markdown(f"""<div class='news-card'>
        <span class='news-tag'>{n['Tag']}</span> <b>{n['Title']}</b> 
        <span style='color:#666; font-size:0.7rem; margin-left:10px;'>[{n['FetchTime']}]</span>
        </div>""", unsafe_allow_html=True)
else:
    st.info("📡 กำลังสร้างคลังข้อมูลข่าว... กรุณารอสักครู่ครับประธาน")

st.markdown("<br>", unsafe_allow_html=True)

# --- ASSETS TABLE ---
st.subheader("📊 STRATEGIC PORTFOLIO")
p_display = []
for t, info in st.session_state.my_assets.items():
    chg = m_data.get(t, {}).get("Chg", 0)
    rsi = m_data.get(t, {}).get("RSI", 0)
    mood = "🔥 ช้อนด่วน!" if rsi < 35 else "📉 เริ่มถูกแล้ว" if rsi < 45 else "⚖️ ถือรอดูเชิง"
    p_display.append({"ชื่อหุ้น": t, "มูลค่า (บาท)": f"{info['Val'] * (1 + (chg / 100)):,.2f}", "กำไรสะสม": f"{(info['PL'] + chg):+.2f}%", "ราคา ($)": f"{m_data.get(t, {}).get('Price', 0):.2f}", "วันนี้": f"{chg:+.2f}%", "RSI": f"{rsi:.1f}", "ยุทธวิธี": mood})
st.table(pd.DataFrame(p_display))
