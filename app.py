import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V9.5", layout="wide")
st_autorefresh(interval=60000, key="datarefresh")

# 2. Initializing Systems
if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 4000.0
if 'battle_log' not in st.session_state:
    st.session_state.battle_log = []
if 'my_portfolio' not in st.session_state:
    st.session_state.my_portfolio = {} # {Ticker: {Total_Spent: 0, Total_Qty: 0, Avg_Price: 0}}

# 3. Target Data
target_prices = {
    "NBIS": 170.0, "MU": 730.0, "NVDA": 210.0, "TSM": 380.0, "ASML": 1450.0, 
    "PLTR": 130.0, "GOOGL": 380.0, "AVGO": 400.0, "MSFT": 400.0, 
    "AMZN": 260.0, "ARM": 200.0, "AMD": 430.0, "RKLB": 110.0, "SPY": 530.0
}
tickers = list(target_prices.keys())

# 4. Functions
@st.cache_data(ttl=60)
def get_stock_data(ticker_list):
    stock_data = {}
    for symbol in ticker_list:
        try:
            ticker_obj = yf.Ticker(symbol)
            df = ticker_obj.history(period="5d", interval="15m")
            if df.empty: continue
            
            # RSI Calculation
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            current_rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            
            current_p = float(df['Close'].iloc[-1])
            prev_close = ticker_obj.fast_info['previousClose']
            change = ((current_p - prev_close) / prev_close) * 100
            
            stock_data[symbol] = {
                "Price": current_p,
                "Change %": change,
                "RSI": current_rsi,
                "Mood": "🔥 น่าช้อน" if current_rsi < 35 else "📉 เริ่มถูก" if current_rsi < 45 else "⚖️ ปกติ"
            }
        except: continue
    return stock_data

# --- TOP HUD ---
st.title("🎯 Chairman Nu Command Center V9.5")
col_status, col_ammo, col_fill, col_fire = st.columns([1, 2, 1, 1])

with col_status:
    st.write("📡 **LIVE SIGNAL**")
    st.caption(f"Last sync: {time.strftime('%H:%M:%S')}")

with col_ammo:
    st.metric("🔥 กระสุนคงเหลือ", f"{st.session_state.cash_balance:,.2f} THB")

with col_fill:
    with st.popover("📥 เติมเงิน"):
        amt = st.number_input("จำนวนเงินที่เติม", min_value=0.0, step=500.0)
        if st.button("ยืนยัน"):
            st.session_state.cash_balance += amt
            st.rerun()

with col_fire:
    with st.popover("🎯 ยิงกระสุน"):
        sel = st.selectbox("เป้าหมาย", tickers)
        p_usd = st.number_input("ราคาหุ้นที่ซื้อ ($)", min_value=0.01)
        spent_thb = st.number_input("ใช้กระสุน (THB)", min_value=0.0)
        if st.button("Execute Order"):
            if spent_thb <= st.session_state.cash_balance and spent_thb > 0:
                # บันทึก Battle Log
                st.session_state.cash_balance -= spent_thb
                st.session_state.battle_log.append({"Time": time.strftime("%H:%M"), "Ticker": sel, "Spent": spent_thb, "Price": p_usd})
                
                # อัปเดตพอร์ต (Simplified Calculation)
                if sel not in st.session_state.my_portfolio:
                    st.session_state.my_portfolio[sel] = {"Total_Spent": 0.0}
                st.session_state.my_portfolio[sel]["Total_Spent"] += spent_thb
                
                st.balloons(); st.rerun()
            else: st.error("ข้อมูลไม่ถูกต้อง หรือกระสุนไม่พอ!")

st.markdown("---")

# ดึงข้อมูลตลาด
market_data = get_stock_data(tickers)

# --- ส่วนที่ 1: รายละเอียดพอร์ตของประธาน (The Vault) ---
st.subheader("📁 My Strategic Assets (พอร์ตของฉัน)")
if st.session_state.my_portfolio:
    p_cols = st.columns(len(st.session_state.my_portfolio) if len(st.session_state.my_portfolio) < 5 else 4)
    for idx, (t, p_info) in enumerate(st.session_state.my_portfolio.items()):
        with p_cols[idx % 4]:
            current_mkt_price = market_data.get(t, {}).get("Price", 0)
            st.info(f"**{t}**\n\nทุนสะสม: {p_info['Total_Spent']:,.2f} THB\n\nราคาตลาด: ${current_mkt_price}")
else:
    st.write("ยังไม่มีหุ้นในครอบครอง กดยิงกระสุนเพื่อเริ่มสะสม")

st.markdown("---")

# ส่วนที่ 2: ตารางหุ้น
if market_data:
    st.subheader("🚀 Market Live Pulse")
    display_df = pd.DataFrame.from_dict(market_data, orient='index').reset_index()
    display_df.columns = ["Ticker", "Price", "Change %", "RSI", "Market Mood"]
    st.dataframe(display_df.sort_values("RSI"), use_container_width=True)

st.markdown("---")

# ส่วนที่ 3: Battle Log
st.subheader("📜 Battle Log")
if st.session_state.battle_log:
    st.table(pd.DataFrame(st.session_state.battle_log).iloc[::-1])

st.caption("© 2026 Chairman Nu Intelligence System • Portfolio Mode Active")
