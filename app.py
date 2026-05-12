import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import time

# 1. Setup & Configuration
st.set_page_config(page_title="Chairman Nu Command Center V8.5", layout="wide")
st_autorefresh(interval=300000, key="datarefresh")

# 2. Initializing Systems (Ammo & News)
if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 4000.0
if 'battle_log' not in st.session_state:
    st.session_state.battle_log = []
if 'news_bulletin' not in st.session_state:
    st.session_state.news_bulletin = [
        {"Date": "2026-05-12", "Topic": "Cerebras IPO: 3 จุดตายที่ต้องระวัง", "Impact": "⚠️ High Risk"},
        {"Date": "2026-05-12", "Topic": "ARK (Cathie Wood) เทขาย AMD และ RKLB ต่อเนื่อง", "Impact": "📉 Negative"}
    ]

# 3. Target Data
target_prices = {
    "NBIS": 170.0, "MU": 730.0, "NVDA": 210.0, "TSM": 380.0, "ASML": 1450.0, 
    "PLTR": 130.0, "GOOGL": 380.0, "AVGO": 400.0, "MSFT": 400.0, 
    "AMZN": 260.0, "ARM": 200.0, "AMD": 430.0, "RKLB": 110.0, "SPY": 530.0
}
tickers = list(target_prices.keys())

# 4. Technical Functions
def calculate_rsi_manual(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=600)
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
        except: continue
    return pd.DataFrame(stock_data)

# --- SIDEBAR: COMMANDS ---
st.sidebar.title("🧨 Ammunition Depot")
st.sidebar.metric("กระสุนคงเหลือ (Cash)", f"{st.session_state.cash_balance:,.2f} THB")

with st.sidebar.expander("📥 เติมกระสุน / 🎯 ยิงกระสุน"):
    option = st.radio("เลือกปฏิบัติการ", ["เติมเงิน", "ช้อนซื้อ"])
    if option == "เติมเงิน":
        add_amt = st.number_input("จำนวนเงินที่เติม", min_value=0.0, step=500.0)
        if st.button("ยืนยันการเติมเงิน"):
            st.session_state.cash_balance += add_amt
            st.rerun()
    else:
        selected_stock = st.selectbox("เลือกเป้าหมาย", tickers)
        buy_p = st.number_input("ราคา ($)", min_value=0.0)
        spent = st.number_input("ใช้กระสุน (THB)", min_value=0.0)
        if st.button("Execute Order"):
            if spent <= st.session_state.cash_balance:
                st.session_state.cash_balance -= spent
                st.session_state.battle_log.append({"Time": time.strftime("%H:%M"), "Ticker": selected_stock, "Spent": spent, "Price": buy_p})
                st.balloons()
                st.rerun()

with st.sidebar.expander("📰 เพิ่มข่าววงใน (Intel)"):
    new_topic = st.text_input("หัวข้อข่าว/ประเด็นสำคัญ")
    impact_lv = st.selectbox("ผลกระทบ", ["🔥 Hot News", "⚠️ Warning", "📈 Positive", "📉 Negative", "⚖️ Neutral"])
    if st.button("บันทึกข่าว"):
        st.session_state.news_bulletin.insert(0, {"Date": time.strftime("%Y-%m-%d"), "Topic": new_topic, "Impact": impact_lv})
        st.success("บันทึกข่าวลงค่ายเรียบร้อย!")
        st.rerun()

# --- MAIN CONTENT ---
st.title("🎯 Chairman Nu Command Center V8.5")

# 1. Market Scan
data = get_data(tickers)
if not data.empty:
    st.subheader("🚀 Market Opportunity Scan")
    st.dataframe(data.sort_values("RSI"), use_container_width=True)
    best_deal = data.sort_values("RSI").iloc[0]
    if best_deal['RSI'] < 40:
        st.success(f"💡 **จาร์วิสวิเคราะห์:** หุ้น **{best_deal['Ticker']}** อยู่ในจุดที่น่าสนใจที่สุด (RSI: {best_deal['RSI']})")

st.markdown("---")

# 2. Strategic Intel (โหมดข่าวที่ประธานต้องการ)
st.subheader("📰 Strategic Intel Bulletin")
if st.session_state.news_bulletin:
    for news in st.session_state.news_bulletin[:5]: # โชว์ 5 ข่าวล่าสุด
        st.info(f"**[{news['Date']}]** | **{news['Impact']}** : {news['Topic']}")
else:
    st.write("ยังไม่มีข่าวใหม่เข้าค่าย")

st.markdown("---")

# 3. History & Charts
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("📜 Battle Log")
    if st.session_state.battle_log: st.table(pd.DataFrame(st.session_state.battle_log).iloc[::-1])
with col2:
    st.subheader("📊 Ammo Allocation")
    if st.session_state.battle_log: st.bar_chart(pd.DataFrame(st.session_state.battle_log).groupby("Ticker")["Spent"].sum())

st.caption("© 2026 Chairman Nu Intelligence System • News & Intel Mode Active")
