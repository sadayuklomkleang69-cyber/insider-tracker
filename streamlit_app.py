import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime

# --- 1. CONFIGURATION & REAL-TIME UI ---
st.set_page_config(page_title="Chairman Nu Command Center V5.8", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0A0A0A; color: #E0E0E0; }
    h1, h2, h3 { color: #00AAFF !important; }
    .whale-card { 
        background: linear-gradient(145deg, #1a1a1a, #252525);
        padding: 20px; border-radius: 15px; 
        border-left: 8px solid #00FF88; margin-bottom: 15px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
    }
    .sell-card { border-left: 8px solid #FF4444; }
    .metric-box { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border: 1px solid #00AAFF; }
    .status-live { color: #00FF88; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LIST หุ้นจาก TRADINGVIEW ---
watchlist = [
    'NVDA', 'TSM', 'ASML', 'PLTR', 'GOOGL', 'AVGO', 'MSFT', 'AMZN', 'ARM', 
    'AMD', 'MU', 'NBIS', 'RKLB', 'JEPQ', 'SPYI', 'SOFI', 'UPST'
]

@st.cache_data(ttl=60)
def fetch_whale_data():
    all_data = []
    prices = {}
    for ticker in watchlist:
        try:
            t = yf.Ticker(ticker)
            prices[ticker] = t.info.get('regularMarketPrice') or t.info.get('currentPrice') or 0
            df = t.insider_transactions
            if df is not None and not df.empty:
                df['Symbol'] = ticker
                df['Date'] = pd.to_datetime(df['Start Date'] if 'Start Date' in df.columns else df.index)
                all_data.append(df)
        except: continue
    return pd.concat(all_data) if all_data else pd.DataFrame(), prices

# --- 3. SIDEBAR NAVIGATION (หมวดหมู่กลับมาแล้วครับ) ---
with st.sidebar:
    st.title("🎛️ Command Center")
    menu = st.radio("เลือกโหมดการทำงาน:", ["🐳 จับตาปลาวาฬ (Live)", "🧮 ตารางคำนวณ Dime"])
    st.markdown("---")
    st.markdown(f"สถานะ: <span class='status-live'>● LIVE</span>", unsafe_allow_html=True)
    st.info(f"อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')}")

try:
    full_df, current_prices = fetch_whale_data()

    if menu == "🐳 จับตาปลาวาฬ (Live)":
        st.title("🐳 Whale Tracker: Deep Scan")
        if not full_df.empty:
            latest_moves = full_df.sort_values('Date', ascending=False).head(50)
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🟢 รายการช้อนซื้อ")
                buys = latest_moves[latest_moves['Text'].str.contains('Purchase', case=False, na=False)]
                for _, row in buys.iterrows():
                    st.markdown(f'<div class="whale-card"><h3>{row["Symbol"]} | ${current_prices.get(row["Symbol"], 0):.2f}</h3><p><b>ใครซื้อ:</b> {row["Insider"]} ({row["Position"]})</p><p><b>จำนวน:</b> {int(row["Shares"]):,} หุ้น | <b>วันที่:</b> {row["Date"].strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)
            with col2:
                st.subheader("🔴 รายการขาย")
                sells = latest_moves[latest_moves['Text'].str.contains('Sale', case=False, na=False)]
                for _, row in sells.iterrows():
                    st.markdown(f'<div class="whale-card sell-card"><h3>{row["Symbol"]} | ${current_prices.get(row["Symbol"], 0):.2f}</h3><p><b>ใครขาย:</b> {row["Insider"]}</p><p><b>จำนวน:</b> {int(row["Shares"]):,} หุ้น | <b>วันที่:</b> {row["Date"].strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)

    elif menu == "🧮 ตารางคำนวณ Dime":
        st.title("🧮 Calculator: Sync Dime & Upside")
        selected = st.selectbox("เลือกหุ้นจากพอร์ต:", watchlist, index=watchlist.index('UPST'))
        live_p = current_prices.get(selected, 1.0)
        
        c1, c2 = st.columns([1, 1.2])
        with c1:
            st.markdown(f'<div class="metric-box">ราคาตลาด {selected}: <b>${live_p:.2f}</b></div><br>', unsafe_allow_html=True)
            d_sh = st.number_input("หุ้นเดิมใน Dime", value=0.0)
            d_avg = st.number_input("ต้นทุนเดิม ($)", value=float(live_p))
            top_up = st.number_input("เงินช้อนเพิ่ม ($)", value=1000.0)
            new_sh = top_up / live_p
            final_avg = ((d_sh * d_avg) + top_up) / (d_sh + new_sh)
            st.metric("ราคาเฉลี่ยใหม่", f"${final_avg:.2f}", f"{final_avg - d_avg:.2f}")

        with c2:
            st.subheader("🎯 วิเคราะห์จุดช้อน & เป้าหมาย")
            targets = [live_p * 1.2, live_p * 1.5, live_p * 2.0]
            supports = [live_p * 0.95, live_p * 0.90, live_p * 0.85]
            res_data = []
            for sup in supports:
                row = {"จุดช้อน ($)": f"{sup:.2f}"}
                for i, t in enumerate(targets):
                    row[f"เป้า {i+1} (${t:.2f})"] = f"+{((t-sup)/sup)*100:.1f}%"
                res_data.append(row)
            st.table(pd.DataFrame(res_data))

except Exception as e:
    st.error(f"ระบบขัดข้อง: {e}")
