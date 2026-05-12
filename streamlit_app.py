import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Chairman Nu Command Center V7.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0A0A0A; color: #E0E0E0; }
    h1, h2, h3 { color: #00AAFF !important; }
    .whale-card { 
        background: linear-gradient(145deg, #1a1a1a, #252525);
        padding: 20px; border-radius: 15px; 
        border-left: 8px solid #00FF88; margin-bottom: 15px;
    }
    .sell-card { border-left: 8px solid #FF4444; }
    .status-live { color: #00FF88; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. WATCHLIST จาก TRADINGVIEW ---
watchlist = ['NVDA', 'TSM', 'ASML', 'PLTR', 'GOOGL', 'AVGO', 'MSFT', 'AMZN', 'ARM', 'AMD', 'MU', 'NBIS', 'RKLB', 'JEPQ', 'SPYI', 'SOFI', 'UPST']

@st.cache_data(ttl=300)
def fetch_all_data():
    all_data_list = []
    prices = {}
    for ticker in watchlist:
        try:
            t = yf.Ticker(ticker)
            p = t.info.get('regularMarketPrice') or t.info.get('currentPrice') or 0
            prices[ticker] = p
            df = t.insider_transactions
            if df is not None and not df.empty:
                df = df.copy()
                df['Symbol'] = ticker
                df['Date'] = pd.to_datetime(df['Start Date'] if 'Start Date' in df.columns else df.index)
                all_data_list.append(df)
        except: continue
    return (pd.concat(all_data_list) if all_data_list else pd.DataFrame()), prices

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🎛️ Command Center V7.0")
    menu = st.radio("เลือกโหมด:", [
        "📊 Whale Sentiment Score", 
        "🐳 Insider Live Feed", 
        "🎯 กลยุทธ์การช้อน & ขาย", 
        "🧮 ตารางคำนวณ Dime"
    ])
    st.markdown("---")
    st.markdown(f"สถานะ: <span class='status-live'>● LIVE</span>", unsafe_allow_html=True)

try:
    full_df, current_prices = fetch_all_data()

    # --- PAGE 1: SENTIMENT SCORE ---
    if menu == "📊 Whale Sentiment Score":
        st.title("📊 Whale Confidence Score")
        scores = []
        for ticker in watchlist:
            f_score, status = 0, "💤 นิ่ง"
            if not full_df.empty:
                ticker_data = full_df[full_df['Symbol'] == ticker]
                buys = ticker_data[ticker_data['Text'].str.contains('Purchase|Exercise|Acquisition', case=False, na=False)]
                if not buys.empty:
                    f_score = 10
                    status = "🔥 แรงมาก"
            scores.append({"หุ้น": ticker, "คะแนน (1-10)": f_score, "สถานะ": status})
        st.dataframe(pd.DataFrame(scores).sort_values("คะแนน (1-10)", ascending=False), use_container_width=True)

    # --- PAGE 2: LIVE FEED (กู้คืนหมวดปลาวาฬที่หายไป) ---
    elif menu == "🐳 Insider Live Feed":
        st.title("🐳 Insider Transaction Feed (Real-time)")
        if not full_df.empty:
            latest = full_df.sort_values('Date', ascending=False)
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🟢 รายการช้อนซื้อล่าสุด")
                buys_list = latest[latest['Text'].str.contains('Purchase|Exercise|Acquisition', case=False, na=False)].head(20)
                for _, row in buys_list.iterrows():
                    st.markdown(f'<div class="whale-card"><h3>{row["Symbol"]} | ${current_prices.get(row["Symbol"], 0):.2f}</h3><p><b>คนซื้อ:</b> {row["Insider"]} ({row["Position"]})</p><p><b>จำนวน:</b> {int(row["Shares"]):,} หุ้น | {row["Date"].strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)
            with c2:
                st.subheader("🔴 รายการขายล่าสุด")
                sells_list = latest[latest['Text'].str.contains('Sale', case=False, na=False)].head(20)
                for _, row in sells_list.iterrows():
                    st.markdown(f'<div class="whale-card sell-card"><h3>{row["Symbol"]} | ${current_prices.get(row["Symbol"], 0):.2f}</h3><p><b>คนขาย:</b> {row["Insider"]}</p><p><b>จำนวน:</b> {int(row["Shares"]):,} หุ้น | {row["Date"].strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)

    # --- PAGE 3: STRATEGY ---
    elif menu == "🎯 กลยุทธ์การช้อน & ขาย":
        st.title("🎯 กลยุทธ์ไม้ 1-2-3 & จุดขายทำกำไร")
        strategy_data = []
        for ticker in watchlist:
            price = current_prices.get(ticker, 0)
            if price == 0: continue
            risk_level = "🟢 ต่ำ"
            if not full_df.empty:
                ticker_data = full_df[full_df['Symbol'] == ticker]
                sells = ticker_data[ticker_data['Text'].str.contains('Sale', case=False, na=False)]
                if len(sells) > 5: risk_level = "🔴 เสี่ยง (วาฬรินขาย)"
            
            strategy_data.append({
                "หุ้น": ticker, "ราคาปัจจุบัน": f"${price:.2f}",
                "ช้อนไม้ 1 (-5%)": f"${price*0.95:.2f}", "ช้อนไม้ 2 (-10%)": f"${price*0.90:.2f}",
                "ขายไม้ 1 (+10%)": f"${price*1.10:.2f}", "ขายไม้ 2 (+20%)": f"${price*1.20:.2f}",
                "ความเสี่ยง": risk_level
            })
        st.dataframe(pd.DataFrame(strategy_data), use_container_width=True)

    # --- PAGE 4: CALCULATOR ---
    elif menu == "🧮 ตารางคำนวณ Dime":
        st.title("🧮 Smart Calculator (Sync Dime)")
        selected = st.selectbox("เลือกหุ้น:", watchlist, index=watchlist.index('UPST'))
        live_p = current_prices.get(selected, 1.0)
        c1, c2 = st.columns([1, 1.2])
        with c1:
            d_sh = st.number_input("จำนวนหุ้นใน Dime", value=0.0)
            d_avg = st.number_input("ต้นทุนเดิม ($)", value=float(live_p))
            top_up = st.number_input("เงินที่จะซื้อเพิ่ม ($)", value=1000.0)
            new_sh = top_up / live_p
            final_avg = ((d_sh * d_avg) + top_up) / (d_sh + new_sh)
            st.metric("ราคาเฉลี่ยใหม่", f"${final_avg:.2f}", f"{final_avg - d_avg:.2f}")
        with c2:
            st.table(pd.DataFrame([{"จุดช้อน ($)": f"{live_p*s:.2f}", "เป้ากำไร": f"${live_p*1.2:.2f}"} for s in [0.95, 0.9, 0.85]]))

except Exception as e:
    st.error(f"ระบบขัดข้อง: {e}")
