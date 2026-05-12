import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Chairman Nu Command Center V6.1", layout="wide")

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
    </style>
    """, unsafe_allow_html=True)

# --- 2. TRADINGVIEW WATCHLIST ---
watchlist = ['NVDA', 'TSM', 'ASML', 'PLTR', 'GOOGL', 'AVGO', 'MSFT', 'AMZN', 'ARM', 'AMD', 'MU', 'NBIS', 'RKLB', 'JEPQ', 'SPYI', 'SOFI', 'UPST']

@st.cache_data(ttl=60)
def fetch_all_data():
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

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🎛️ Command Center V6.1")
    menu = st.radio("เลือกโหมด:", ["🐳 จับตาปลาวาฬ & Sentiment", "🧮 ตารางคำนวณ Dime", "📝 บันทึกการลงทุน", "📡 ระบบ LINE"])
    st.markdown("---")
    st.info(f"อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')}")

try:
    full_df, current_prices = fetch_all_data()

    if menu == "🐳 จับตาปลาวาฬ & Sentiment":
        st.title("🐳 Insider Intelligence Scan")
        
        # --- ปรับสูตรคะแนนใหม่ (New Logic) ---
        st.subheader("📊 Whale Confidence Score (ปรับปรุงใหม่)")
        scores = []
        for ticker in watchlist:
            ticker_data = full_df[full_df['Symbol'] == ticker]
            buys = ticker_data[ticker_data['Text'].str.contains('Purchase', case=False, na=False)]
            
            if not buys.empty:
                # สูตรใหม่: เริ่มที่ 1 คะแนนทันทีที่มีคนซื้อ + โบนัสตามจำนวนหุ้น
                base_score = 1
                volume_bonus = min(5, int(buys['Shares'].sum() / 1000)) 
                role_bonus = 4 if any(role in str(buys['Position']).upper() for role in ['CEO', 'DIRECTOR', 'OFFICER']) else 0
                final_score = min(10, base_score + volume_bonus + role_bonus)
                
                status = "🔥 แรงมาก" if final_score >= 7 else "✅ เริ่มขยับ"
                scores.append({"หุ้น": ticker, "คะแนน (1-10)": final_score, "สถานะ": status})
            else:
                scores.append({"หุ้น": ticker, "คะแนน (1-10)": 0, "สถานะ": "💤 นิ่ง"})
        
        st.dataframe(pd.DataFrame(scores).sort_values("คะแนน (1-10)", ascending=False), use_container_width=True)

        col1, col2 = st.columns(2)
        latest_moves = full_df.sort_values('Date', ascending=False).head(40)
        with col1:
            st.subheader("🟢 รายการช้อนซื้อ")
            if not latest_moves[latest_moves['Text'].str.contains('Purchase', case=False, na=False)].empty:
                for _, row in latest_moves[latest_moves['Text'].str.contains('Purchase', case=False, na=False)].iterrows():
                    st.markdown(f'<div class="whale-card"><h3>{row["Symbol"]} | ${current_prices.get(row["Symbol"], 0):.2f}</h3><p><b>คนซื้อ:</b> {row["Insider"]} ({row["Position"]})</p><p><b>จำนวน:</b> {int(row["Shares"]):,} หุ้น | {row["Date"].strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)
            else: st.write("ยังไม่มีรายงานซื้อใหม่")

        with col2:
            st.subheader("🔴 รายการขาย")
            for _, row in latest_moves[latest_moves['Text'].str.contains('Sale', case=False, na=False)].iterrows():
                st.markdown(f'<div class="whale-card sell-card"><h3>{row["Symbol"]} | ${current_prices.get(row["Symbol"], 0):.2f}</h3><p><b>คนขาย:</b> {row["Insider"]}</p><p><b>จำนวน:</b> {int(row["Shares"]):,} หุ้น | {row["Date"].strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)

    # --- ส่วนอื่นๆ คงเดิม ---
    elif menu == "🧮 ตารางคำนวณ Dime":
        st.title("🧮 Smart Calculator")
        selected = st.selectbox("เลือกหุ้น:", watchlist, index=watchlist.index('UPST'))
        live_p = current_prices.get(selected, 1.0)
        c1, c2 = st.columns([1, 1.2])
        with c1:
            d_sh = st.number_input("หุ้นใน Dime", value=0.0)
            d_avg = st.number_input("ต้นทุนเดิม ($)", value=float(live_p))
            top_up = st.number_input("เงินช้อนเพิ่ม ($)", value=1000.0)
            new_sh = top_up / live_p
            final_avg = ((d_sh * d_avg) + top_up) / (d_sh + new_sh)
            st.metric("ราคาเฉลี่ยใหม่", f"${final_avg:.2f}", f"{final_avg - d_avg:.2f}")
        with c2:
            st.table(pd.DataFrame([{"จุดช้อน ($)": f"{live_p*s:.2f}", "เป้า 1": f"${live_p*1.2:.2f}"} for s in [0.95, 0.9, 0.85]]))

except Exception as e:
    st.error(f"ระบบขัดข้อง: {e}")
