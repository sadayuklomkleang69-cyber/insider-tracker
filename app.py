import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V13.0", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

# --- UI ENHANCEMENT (CUSTOM CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    div[data-testid="stMetricValue"] { font-size: 2rem; color: #00FFC8 !important; }
    div[data-testid="stMetricDelta"] { color: #FF4B4B !important; }
    .stTable { background-color: #161B22; border-radius: 10px; border: 1px solid #30363D; }
    h1, h2, h3 { color: #FFFFFF; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    .stButton>button { background-color: #00FFC8; color: #000000; border-radius: 5px; font-weight: bold; width: 100%; border: none; }
    .stButton>button:hover { background-color: #00D1A4; color: #FFFFFF; }
    .status-badge { padding: 4px 10px; border-radius: 15px; font-size: 0.8rem; font-weight: bold; }
    .glow-card { border: 1px solid #00FFC8; padding: 15px; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 255, 200, 0.2); }
    </style>
    """, unsafe_allow_html=True)

# 2. ข้อมูลพอร์ต (Persistent Session State)
if 'my_assets' not in st.session_state:
    st.session_state.my_assets = {
        "TSM": {"Val": 55244.24, "PL": 10.28},
        "NVDA": {"Val": 46038.54, "PL": 18.95},
        "MU": {"Val": 40188.92, "PL": 68.75},
        "MSFT": {"Val": 27148.52, "PL": 4.69},
        "AVGO": {"Val": 25391.97, "PL": 18.89},
        "GOOGL": {"Val": 24350.15, "PL": 22.86},
        "PLTR": {"Val": 16743.23, "PL": -7.75},
        "ARM": {"Val": 16132.26, "PL": 29.81},
        "AMD": {"Val": 13374.89, "PL": 61.00},
        "AMZN": {"Val": 12972.02, "PL": 18.21},
        "ASML": {"Val": 11166.77, "PL": 8.95},
        "RKLB": {"Val": 6495.83, "PL": 41.11},
        "NBIS": {"Val": 2955.28, "PL": 16.69}
    }

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 2970.05
if 'battle_log' not in st.session_state:
    st.session_state.battle_log = []

# 3. Market Data Engine
@st.cache_data(ttl=60)
def get_market_data(ticker_list):
    results = {}
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
            prev = t.fast_info['previousClose']
            chg = ((curr - prev) / prev) * 100
            results[s] = {"Price": curr, "Chg": chg, "RSI": rsi}
        except: continue
    return results

# --- HEADER SECTION ---
st.markdown("# 🛡️ Chairman Nu Command Center <span style='font-size:15px; color:#00FFC8;'>v13.0 ELITE</span>", unsafe_allow_html=True)

m_data = get_market_data(list(st.session_state.my_assets.keys()))
total_wealth = sum(info['Val'] * (1 + (m_data.get(t, {}).get("Chg", 0) / 100)) for t, info in st.session_state.my_assets.items())

col_info, col_actions = st.columns([3, 2])

with col_info:
    c1, c2 = st.columns(2)
    c1.metric("💰 NET WORTH (REAL-TIME)", f"{total_wealth:,.2f} THB", delta=f"{(total_wealth - 298225.25):+,.2f}")
    c2.metric("🔥 AMMO REMAINING", f"{st.session_state.cash_balance:,.2f} THB")

with col_actions:
    a1, a2 = st.columns(2)
    with a1.popover("📥 TOP-UP"):
        topup = st.number_input("Amount", min_value=0.0)
        if st.button("EXECUTE TOP-UP"): st.session_state.cash_balance += topup; st.rerun()
    with a2.popover("🎯 FIRE AMMO"):
        target = st.selectbox("Target", list(st.session_state.my_assets.keys()))
        spent = st.number_input("Amount (THB)", min_value=0.0)
        if st.button("CONFIRM FIRE"):
            if spent <= st.session_state.cash_balance:
                st.session_state.cash_balance -= spent
                st.session_state.my_assets[target]["Val"] += spent
                st.session_state.battle_log.append({"Time": time.strftime("%H:%M"), "Action": f"ช้อน {target}", "Amt": f"{spent:,.0f}"})
                st.balloons(); st.rerun()

st.markdown("<hr style='border: 0.5px solid #30363D;'>", unsafe_allow_html=True)

# --- SECTION 1: ASSETS TABLE ---
st.subheader("📁 STRATEGIC ASSET OVERVIEW")
p_display = []
for t, info in st.session_state.my_assets.items():
    chg = m_data.get(t, {}).get("Chg", 0)
    rsi = m_data.get(t, {}).get("RSI", 0)
    mood = "🔥 BUY NOW" if rsi < 35 else "📉 CHEAP" if rsi < 45 else "⚖️ HOLD"
    p_display.append({
        "ASSET": t,
        "VALUE (THB)": f"{info['Val'] * (1 + (chg / 100)):,.2f}",
        "OVERALL P/L": f"{(info['PL'] + chg):+.2f}%",
        "PRICE ($)": f"{m_data.get(t, {}).get('Price', 0):.2f}",
        "TODAY": f"{chg:+.2f}%",
        "RSI": f"{rsi:.1f}",
        "SIGNAL": mood
    })

st.table(pd.DataFrame(p_display))

# --- SECTION 2: BATTLE LOG ---
if st.session_state.battle_log:
    with st.expander("📜 RECENT BATTLE LOGS"):
        st.table(pd.DataFrame(st.session_state.battle_log).iloc[::-1])

st.caption("Chairman Nu Strategic System Overdrive | Powered by Jarvis AI")
