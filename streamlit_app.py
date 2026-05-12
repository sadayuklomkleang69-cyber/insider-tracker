import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Chairman Nu Insider", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #121212; color: white; }
    h1, h2, h3 { color: #4FA3FF !important; font-family: 'Kanit', sans-serif; }
    .buy-card { background-color: #1E1E1E; padding: 20px; border-radius: 12px; border-left: 6px solid #2ECC71; margin-bottom: 10px; }
    .sell-card { background-color: #1E1E1E; padding: 20px; border-radius: 12px; border-left: 6px solid #E74C3C; margin-bottom: 10px; }
    .ticker-name { color: #F1C40F; font-size: 22px; font-weight: bold; }
    .date-text { color: #888888; font-size: 15px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA FETCHING ---
watchlist = ['NVDA', 'TSM', 'MSFT', 'PLTR', 'UPST', 'SOFI', 'GOOGL', 'AMD', 'TSLA', 'ARM', 'MU']

@st.cache_data(ttl=600)
def get_insider_data():
    all_buys, all_sells = [], []
    prices = {}
    for ticker in watchlist:
        try:
            t = yf.Ticker(ticker)
            current_p = t.info.get('regularMarketPrice') or t.info.get('currentPrice') or 0
            prices[ticker] = current_p
            df = t.insider_transactions
            if df is not None and not df.empty:
                df['Transaction_Date'] = pd.to_datetime(df['Start Date'] if 'Start Date' in df.columns else df.index)
                df['Symbol'] = ticker
                df['Current_Price'] = current_p
                buys = df[df['Text'].str.contains('Purchase', case=False, na=False)]
                sells = df[df['Text'].str.contains('Sale', case=False, na=False)]
                all_buys.append(buys); all_sells.append(sells)
        except: continue
    return pd.concat(all_buys), pd.concat(all_sells), prices

# --- 3. MAIN INTERFACE ---
try:
    buys_df, sells_df, current_prices = get_insider_data()
    
    st.title('🎯 ระบบจับตาปลาวาฬ: ซื้อ & ขาย')
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("🟢 รายการซื้อ (สะสมของ)")
        for _, row in buys_df.sort_values('Transaction_Date', ascending=False).head(10).iterrows():
            st.markdown(f'<div class="buy-card"><span class="ticker-name">{row["Symbol"]}</span> | 📅 {row["Transaction_Date"].strftime("%d/%m/%Y")}<br>{int(row["Shares"]):,} หุ้น @ ${row.get("Price", 0):.2f}<br><b>{row["Insider"]}</b></div>', unsafe_allow_html=True)
            
    with col_r:
        st.subheader("🔴 รายการขาย (ระวังตัว)")
        for _, row in sells_df.sort_values('Transaction_Date', ascending=False).head(10).iterrows():
            st.markdown(f'<div class="sell-card"><span class="ticker-name">{row["Symbol"]}</span> | 📅 {row["Transaction_Date"].strftime("%d/%m/%Y")}<br>{int(row["Shares"]):,} หุ้น @ ${row.get("Price", 0):.2f}<br><b>{row["Insider"]}</b></div>', unsafe_allow_html=True)

    # --- 4. DYNAMIC CALCULATOR (NEW!) ---
    st.markdown("---")
    st.header("🧮 ตารางคำนวณอัจฉริยะ (เลือกหุ้นได้)")
    
    selected_stock = st.selectbox("เลือกหุ้นที่ท่านต้องการวางแผน:", watchlist)
    live_price = current_prices.get(selected_stock, 0)
    
    col_c1, col_c2 = st.columns([1, 2])
    with col_c1:
        st.subheader(f"คำนวณถัวเฉลี่ย: {selected_stock}")
        st.write(f"ราคาตลาดปัจจุบัน: **${live_price:.2f}**")
        cur_sh = st.number_input("หุ้นที่มีปัจจุบัน", value=100.0)
        cur_avg = st.number_input("ต้นทุนเดิม (USD)", value=live_price)
        add_inv = st.number_input("เงินที่จะลงเพิ่ม (USD)", value=1000.0)
        
        new_sh = add_inv / live_price
        total_sh = cur_sh + new_sh
        new_avg_cost = ((cur_sh * cur_avg) + add_inv) / total_sh
        st.metric("ราคาเฉลี่ยใหม่ถ้าซื้อตอนนี้", f"${new_avg_cost:.2f}", f"{new_avg_cost - cur_avg:.2f}")

    with col_c2:
        st.subheader("เป้าหมายกำไรตามแนวต้าน")
        # คำนวณแนวรับ-ต้านจำลองจากราคาปัจจุบัน (หรือปรับแต่งเองได้)
        res = [live_price * 1.1, live_price * 1.25, live_price * 1.5]
        sup = [live_price * 0.9, live_price * 0.8, live_price * 0.7]
        
        matrix = []
        for s in sup:
            row = {"แนวรับที่รอช้อน": f"${s:.2f}"}
            for i, r in enumerate(res):
                upside = ((r - s) / s) * 100
                row[f"เป้า R{i+1} (${r:.2f})"] = f"+{upside:.2f}%"
            matrix.append(row)
        st.table(pd.DataFrame(matrix))

except Exception as e:
    st.error(f"กำลังดึงข้อมูล: {e}")
