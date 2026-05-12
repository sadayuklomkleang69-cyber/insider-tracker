import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Chairman Nu Command Center V6.8", layout="wide")

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
    .metric-box { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border: 1px solid #00AAFF; }
    /* สไตล์สำหรับไฟกระพริบ */
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
    st.title("🎛️ Command Center V6.8")
    menu = st.radio("เลือกโหมด:", ["📊 Whale Sentiment Score", "🐳 Insider Live Feed", "🧮 ตารางคำนวณ Dime", "📝 บันทึกการลงทุน", "📡 ระบบ LINE"])
    st.markdown("---")
    # ไฟกระพริบกลับมาแล้วครับ
    st.markdown(f"สถานะระบบ: <span class='status-live'>● LIVE</span>", unsafe_allow_html=True)
    st.info(f"อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')}")

try:
    full_df, current_prices = fetch_all_data()

    if menu == "📊 Whale Sentiment Score":
        st.title("📊 Whale Confidence Score")
        scores = []
        for ticker in watchlist:
            f_score, status = 0, "💤 นิ่ง"
            if not full_df.empty:
                ticker_data = full_df[full_df['Symbol'] == ticker]
                buys = ticker_data[ticker_data['Text'].str.contains('Purchase|Exercise|Acquisition', case=False, na=False)]
                if not buys.empty:
                    base = 2
                    vol = min(4, int(buys['Shares'].sum() / 100))
                    role = 4 if any(r in str(buys['Position']).upper() for r in ['CEO', 'DIRECTOR', 'OFFICER']) else 0
                    f_score = min(10, base + vol + role)
                    status = "🔥 แรงมาก" if f_score >= 7 else "✅ เริ่มขยับ"
            scores.append({"หุ้น": ticker, "คะแนน (1-10)": f_score, "สถานะ": status})
        st.dataframe(pd.DataFrame(scores).sort_values("คะแนน (1-10)", ascending=False), use_container_width=True)

    elif menu == "🐳 Insider Live Feed":
        st.title("🐳 Insider Transaction Feed")
        if not full_df.empty:
            latest = full_df.sort_values('Date', ascending=False)
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🟢 รายการช้อนซื้อ")
                buys = latest[latest['Text'].str.contains('Purchase|Exercise|Acquisition', case=False, na=False)].head(20)
                for _, row in buys.iterrows():
                    st.markdown(f'<div class="whale-card"><h3>{row["Symbol"]} | ${current_prices.get(row["Symbol"], 0):.2f}</h3><p><b>คนซื้อ:</b> {row["Insider"]} ({row["Position"]})</p><p><b>จำนวน:</b> {int(row["Shares"]):,} หุ้น | {row["Date"].strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)
            with c2:
                st.subheader("🔴 รายการขาย")
                sells = latest[latest['Text'].str.contains('Sale', case=False, na=False)].head(20)
                for _, row in sells.iterrows():
                    st.markdown(f'<div class="whale-card sell-card"><h3>{row["Symbol"]} | ${current_prices.get(row["Symbol"], 0):.2f}</h3><p><b>คนขาย:</b> {row["Insider"]}</p><p><b>จำนวน:</b> {int(row["Shares"]):,} หุ้น | {row["Date"].strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)

    elif menu == "🧮 ตารางคำนวณ Dime":
        st.title("🧮 Smart Calculator (Sync Dime)")
        selected = st.selectbox("เลือกหุ้น:", watchlist, index=watchlist.index('UPST') if 'UPST' in watchlist else 0)
        live_p = current_prices.get(selected, 1.0)
        c1, c2 = st.columns([1, 1.2])
        with c1:
            st.markdown(f'<div class="metric-box">ราคาปัจจุบัน: <b>${live_p:.2f}</b></div>', unsafe_allow_html=True)
            d_sh = st.number_input("หุ้นใน Dime", value=0.0)
            d_avg = st.number_input("ต้นทุนเดิม ($)", value=float(live_p))
            top_up = st.number_input("เงินช้อนเพิ่ม ($)", value=1000.0)
            new_sh = top_up / live_p if live_p > 0 else 0
            total_sh = d_sh + new_sh
            final_avg = ((d_sh * d_avg) + top_up) / total_sh if total_sh > 0 else 0
            st.metric("ราคาเฉลี่ยใหม่", f"${final_avg:.2f}", f"{final_avg - d_avg:.2f}")
        with c2:
            st.subheader("🎯 จุดเข้า & เป้าหมาย")
            targets = [live_p * 1.2, live_p * 1.5, live_p * 2.0]
            supports = [live_p * 0.95, live_p * 0.90, live_p * 0.85]
            res_data = [{"จุดช้อน ($)": f"{s:.2f}", "เป้า 1 (+20%)": f"${live_p*1.2:.2f}", "เป้า 2 (+50%)": f"${live_p*1.5:.2f}"} for s in supports]
            st.table(pd.DataFrame(res_data))

    elif menu == "📝 บันทึกการลงทุน":
        st.title("📝 Investment Journal")
        st.text_area("บันทึกแผนการเทรด:", placeholder="พิมพ์แผนของท่านประธานที่นี่...")
        st.button("💾 บันทึก")

    elif menu == "📡 ระบบ LINE":
        st.header("📡 LINE System")
        if st.button("🚀 ทดสอบสัญญาณ"): st.balloons()

except Exception as e:
    st.error(f"ระบบขัดข้อง: {e}")
