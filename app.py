import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V14.0", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

# --- UI ENHANCEMENT (ADVANCED NEON CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .main { background-color: #050505; }
    
    /* Neon Text & Titles */
    h1, h2, h3 { 
        font-family: 'Orbitron', sans-serif; 
        color: #00FFC8; 
        text-shadow: 0 0 10px rgba(0, 255, 200, 0.5);
    }

    /* Metric Styling */
    div[data-testid="stMetricValue"] { 
        font-family: 'Orbitron', sans-serif;
        font-size: 2.5rem !important; 
        color: #00FFC8 !important; 
        text-shadow: 0 0 15px rgba(0, 255, 200, 0.4);
    }
    
    /* Tactical Card Effect */
    div[data-testid="stMetric"] {
        background: rgba(16, 20, 24, 0.8);
        border: 1px solid #30363D;
        border-left: 5px solid #00FFC8;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
    }

    /* Modern Table Styling */
    .stTable { 
        border: 1px solid #00FFC8 !important;
        border-radius: 15px !important;
        overflow: hidden;
    }
    
    th { background-color: #101418 !important; color: #00FFC8 !important; font-family: 'Orbitron', sans-serif; }
    td { background-color: #050505 !important; color: #E6EDF3 !important; border-bottom: 0.1px solid #30363D !important; }

    /* Button Neon Effect */
    .stButton>button { 
        background: linear-gradient(45deg, #00FFC8, #0088FF);
        color: #000000; 
        border-radius: 8px; 
        font-family: 'Orbitron', sans-serif;
        font-weight: bold; 
        border: none;
        box-shadow: 0 0 15px rgba(0, 255, 200, 0.3);
        transition: 0.3s;
    }
    .stButton>button:hover { 
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(0, 255, 200, 0.6);
        color: #FFFFFF;
    }

    /* Status Badge Colors */
    .buy-now { color: #00FFC8; font-weight: bold; text-shadow: 0 0 5px #00FFC8; }
    .cheap { color: #FFFF00; font-weight: bold; }
    .hold { color: #888888; }
    </style>
    """, unsafe_allow_html=True)

# 2. ข้อมูลพอร์ต (Persistent Session State)
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
st.markdown("<h1 style='text-align: center;'>⚡ CHAIRMAN NU : NEON OVERDRIVE ⚡</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>SYSTEM VERSION 14.0 | STATUS: ACTIVE</p>", unsafe_allow_html=True)

m_data = get_market_data(list(st.session_state.my_assets.keys()))
total_wealth = sum(info['Val'] * (1 + (m_data.get(t, {}).get("Chg", 0) / 100)) for t, info in st.session_state.my_assets.items())

col_info, col_actions = st.columns([3, 2])

with col_info:
    c1, c2 = st.columns(2)
    c1.metric("💰 TOTAL ASSETS", f"{total_wealth:,.2f} THB", delta=f"{(total_wealth - 298225.25):+,.2f}")
    c2.metric("🔥 AMMO LEFT", f"{st.session_state.cash_balance:,.2f} THB")

with col_actions:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    a1, a2 = st.columns(2)
    with a1.popover("📥 ADD AMMO"):
        topup = st.number_input("Amount", min_value=0.0)
        if st.button("PROCEED TOP-UP"): st.session_state.cash_balance += topup; st.rerun()
    with a2.popover("🎯 EXECUTE FIRE"):
        target = st.selectbox("Select Asset", list(st.session_state.my_assets.keys()))
        spent = st.number_input("Budget (THB)", min_value=0.0)
        if st.button("CONFIRM EXECUTION"):
            if spent <= st.session_state.cash_balance:
                st.session_state.cash_balance -= spent
                st.session_state.my_assets[target]["Val"] += spent
                st.session_state.battle_log.append({"Time": time.strftime("%H:%M"), "Action": f"ช้อน {target}", "Amt": f"{spent:,.0f}"})
                st.balloons(); st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- SECTION 1: ASSETS TABLE ---
st.subheader("📊 TACTICAL PORTFOLIO DATA")
p_display = []
for t, info in st.session_state.my_assets.items():
    chg = m_data.get(t, {}).get("Chg", 0)
    rsi = m_data.get(t, {}).get("RSI", 0)
    mood = "🔥 BUY NOW" if rsi < 35 else "📉 CHEAP" if rsi < 45 else "⚖️ HOLD"
    p_display.append({
        "SYMBOL": t,
        "VALUE (THB)": f"{info['Val'] * (1 + (chg / 100)):,.2f}",
        "TOTAL P/L": f"{(info['PL'] + chg):+.2f}%",
        "PRICE ($)": f"{m_data.get(t, {}).get('Price', 0):.2f}",
        "24H CHG": f"{chg:+.2f}%",
        "RSI": f"{rsi:.1f}",
        "STRATEGY": mood
    })

st.table(pd.DataFrame(p_display))

# --- SECTION 2: BATTLE LOG ---
if st.session_state.battle_log:
    with st.expander("📝 RECENT TRANSACTIONS"):
        st.table(pd.DataFrame(st.session_state.battle_log).iloc[::-1])

st.markdown("<hr style='border: 1px solid #30363D;'>", unsafe_allow_html=True)
st.caption("NEON OVERDRIVE INTERFACE | DEPLOYED BY JARVIS v14.0")
