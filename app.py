import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V8.1", layout="wide")
st_autorefresh(interval=300000, key="datarefresh")

# 2. Initializing Ammo System (ระบบกระสุน)
if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 4000.0  # กระสุนเริ่มต้น
if 'battle_log' not in st.session_state:
    st.session_state.battle_log = [] # ประวัติการช้อน

# 3. Target Data
target_prices = {
    "NVDA": 210.0, "TSM": 380.0, "ASML": 1450.0, "PLTR": 130.0, 
    "GOOGL": 380.0, "AVGO": 400.0, "MSFT": 400.0, "AMZN": 260.0, 
    "ARM": 200.0, "AMD": 430.0, "MU": 730.0, "RKLB": 110.0
}
tickers = list(target_prices.keys())

# 4. Technical Functions
def calculate_rsi_manual(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=900)
def get_data(ticker_list):
    stock_data = []
    for symbol in ticker_list:
        try:
            ticker_obj = yf.Ticker(symbol)
            df = ticker_obj.history(period="1mo")
            if df.empty or len(df) < 15: continue
            
            df['RSI'] = calculate_rsi_manual(df['Close'])
            current_p = float(df['Close'].iloc[-1])
            prev_p = float(df['Close'].iloc[-2])
            current_rsi = float(df['RSI'].iloc[-1])
            change = ((current_p - prev_p) / prev_p) * 100
            target = target_prices.get(symbol, 0)
            gap = ((current_p - target) / target) * 100

            if current_rsi < 35: mood = "🔥 น่าช้อน (Extreme Fear)"
            elif current_rsi < 45: mood = "📉 เริ่มถูก (Discount)"
            elif current_rsi > 70: mood = "⚠️ ระวัง (Extreme Greed)"
            else: mood = "⚖️ ปกติ"

            stock_data.append({
                "Ticker": symbol, "Price": round(current_p, 2),
                "Change %": f"{change:+.2f}%", "RSI": round(current_rsi, 2),
                "Market Mood": mood, "Gap to Target %": f"{gap:+.2f}%"
            })
            time.sleep(0.2)
        except: continue
    return pd.DataFrame(stock_data)

# --- SIDEBAR: AMMO MANAGEMENT (โหมดกระสุน) ---
st.sidebar.title("🧨 Ammunition Depot")
st.sidebar.metric("กระสุนคงเหลือ (Cash)", f"{st.session_state.cash_balance:,.2f} THB")

with st.sidebar.expander("📥 เติมกระสุน (Top-up)"):
    add_amt = st.number_input("จำนวนเงินที่เติม", min_value=0.0, step=500.0)
    if st.button("ยืนยันการเติมเงิน"):
        st.session_state.cash_balance += add_amt
        st.success(f"เติมกระสุนเรียบร้อย! +{add_amt}")
        st.rerun()

with st.sidebar.expander("🎯 คำนวณวิถีกระสุน (Buy)"):
    selected_stock = st.selectbox("เลือกเป้าหมาย", tickers)
    buy_price = st.number_input("ราคาที่ช้อน ($)", min_value=0.0)
    spent_amt = st.number_input("ใช้กระสุนไปกี่บาท (THB)", min_value=0.0)
    
    if st.button("ยืนยันการยิง (Execute Order)"):
        if spent_amt <= st.session_state.cash_balance:
            st.session_state.cash_balance -= spent_amt
            st.session_state.battle_log.append({
                "Time": time.strftime("%H:%M:%S"),
                "Ticker": selected_stock,
                "Spent": spent_amt,
                "At Price": buy_price
            })
            st.balloons()
            st.rerun()
        else:
            st.error("กระสุนไม่พอ! กรุณาเติมเงินก่อน")

# --- MAIN CONTENT ---
st.title("🎯 Chairman Nu Command Center V8.1")

data = get_data(tickers)
if not data.empty:
    st.subheader("🚀 Market Opportunity Scan")
    st.dataframe(data.sort_values("RSI"), use_container_width=True)
    
    best_deal = data.sort_values("RSI").iloc[0]
    if best_deal['RSI'] < 40:
        st.success(f"💡 **จาร์วิสวิเคราะห์:** หุ้น **{best_deal['Ticker']}** อยู่ในจุดที่น่าสนใจที่สุด (RSI: {best_deal['RSI']})")

st.markdown("---")

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("📜 Battle Log (ประวัติการช้อน)")
    if st.session_state.battle_log:
        log_df = pd.DataFrame(st.session_state.battle_log)
        st.table(log_df.iloc[::-1])
    else:
        st.info("ยังไม่มีการบันทึกการรบในรอบนี้")

with col2:
    st.subheader("📊 Ammo Allocation")
    if st.session_state.battle_log:
        log_df = pd.DataFrame(st.session_state.battle_log)
        summary = log_df.groupby("Ticker")["Spent"].sum()
        st.bar_chart(summary)
    else:
        st.write("รอข้อมูลการช้อน...")

st.caption("© 2026 Chairman Nu Intelligence System • Ammo System Active")
