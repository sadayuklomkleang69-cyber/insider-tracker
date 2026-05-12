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
    .buy-card {
        background-color: #1E1E1E; padding: 20px; border-radius: 12px;
        border-left: 6px solid #2ECC71; margin-bottom: 10px;
    }
    .sell-card {
        background-color: #1E1E1E; padding: 20px; border-radius: 12px;
        border-left: 6px solid #E74C3C; margin-bottom: 10px;
    }
    .ticker-name { color: #F1C40F; font-size: 22px; font-weight: bold; }
    .date-text { color: #888888; font-size: 15px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER ---
st.title('🎯 ระบบจับตาปลาวาฬ: ซื้อ & ขาย')
st.write(f"ข้อมูลสดจาก Yahoo Finance | อัปเดต: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# --- 3. WATCHLIST ---
watchlist = ['NVDA', 'TSM', 'MSFT', 'PLTR', 'UPST', 'SOFI', 'GOOGL', 'AMD', 'TSLA', 'ARM', 'MU']

@st.cache_data(ttl=600)
def get_insider_combined():
    all_buys = []
    all_sells = []
    for ticker in watchlist:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            current_p = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose') or 0
            
            df = t.insider_transactions
            if df is not None and not df.empty:
                # ตรวจสอบว่ามีคอลัมน์วันที่หรือไม่ ถ้าไม่มีใช้ Index
                if 'Start Date' in df.columns:
                    df['Transaction_Date'] = pd.to_datetime(df['Start Date'])
                elif 'Date' in df.columns:
                    df['Transaction_Date'] = pd.to_datetime(df['Date'])
                else:
                    df['Transaction_Date'] = pd.to_datetime(df.index)
                
                df['Symbol'] = ticker
                df['Backup_Price'] = current_p
                
                # กรองซื้อ/ขาย
                buys = df[df['Text'].str.contains('Purchase', case=False, na=False)].copy()
                sells = df[df['Text'].str.contains('Sale', case=False, na=False)].copy()
                
                if not buys.empty: all_buys.append(buys)
                if not sells.empty: all_sells.append(sells)
        except: continue
    return (pd.concat(all_buys) if all_buys else pd.DataFrame(), 
            pd.concat(all_sells) if all_sells else pd.DataFrame())

# --- 4. EXECUTION ---
try:
    with st.spinner('จาร์วิสกำลังตรวจสอบปฏิทินปลาวาฬ...'):
        buys_df, sells_df = get_insider_combined()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🟢 รายการซื้อ (สะสมของ)")
        if not buys_df.empty:
            buys_df = buys_df.sort_values(by='Transaction_Date', ascending=False).head(15)
            for _, row in buys_df.iterrows():
                p = row.get('Price', 0)
                if p == 0 or pd.isna(p): p = row.get('Backup_Price', 0)
                
                d_str = row['Transaction_Date'].strftime('%d/%m/%Y')

                st.markdown(f"""
                <div class="buy-card">
                    <span class="ticker-name">{row['Symbol']}</span> | <span style="color:#2ECC71">BUY</span><br>
                    <span class="date-text">📅 วันที่: {d_str}</span><br>
                    {int(row['Shares']):,} หุ้น @ <b>${p:.2f}</b><br>
                    <b>{row['Insider']}</b> ({row['Position']})
                </div>
                """, unsafe_allow_html=True)
        else: st.info("ยังไม่มีรายการซื้อใหม่")

    with col_right:
        st.subheader("🔴 รายการขาย (ระวังตัว)")
        if not sells_df.empty:
            sells_df = sells_df.sort_values(by='Transaction_Date', ascending=False).head(15)
            for _, row in sells_df.iterrows():
                p = row.get('Price', 0)
                if p == 0 or pd.isna(p): p = row.get('Backup_Price', 0)

                d_str = row['Transaction_Date'].strftime('%d/%m/%Y')

                st.markdown(f"""
                <div class="sell-card">
                    <span class="ticker-name">{row['Symbol']}</span> | <span style="color:#E74C3C">SELL</span><br>
                    <span class="date-text">📅 วันที่: {d_str}</span><br>
                    {int(row['Shares']):,} หุ้น @ <b>${p:.2f}</b><br>
                    <b>{row['Insider']}</b> ({row['Position']})
                </div>
                """, unsafe_allow_html=True)
        else: st.success("ปลอดภัย! ยังไม่มีปลาวาฬเทขายในกลุ่มนี้ครับ")

except Exception as e:
    st.error(f"ระบบกำลังปรับปรุง: {e}")

if st.button('🔄 อัปเดตข้อมูล'):
    st.rerun()
import streamlit as st
import pandas as pd

# --- ส่วนคำนวณแนวรับ-แนวต้าน แบบในรูป image_fdb1db.png ---
st.markdown("---")
st.header("🧮 ตารางคำนวณ แนวรับ-แนวต้าน")

col_calc1, col_calc2 = st.columns([1, 2])

with col_calc1:
    st.subheader("คำนวณค่าเฉลี่ยล่วงหน้า")
    current_shares = st.number_input("จำนวนหุ้นที่มีปัจจุบัน", value=76.447)
    avg_price = st.number_input("ราคาเฉลี่ยปัจจุบัน (USD)", value=11.77)
    invest_more = st.number_input("ใส่เงินลงทุนเพิ่ม (USD)", value=1000)
    
    # คำนวณค่าเฉลี่ยใหม่เมื่อซื้อเพิ่มที่ราคาปัจจุบัน
    # สมมติใช้ราคาปัจจุบัน (Market Price) จากหุ้นที่เลือก
    market_price = 12.82 # ตัวอย่างราคาจากรูป
    new_shares = invest_more / market_price
    total_shares = current_shares + new_shares
    new_avg = ((current_shares * avg_price) + invest_more) / total_shares
    
    st.metric("ราคาเฉลี่ยใหม่", f"${new_avg:.2f}", delta=f"{new_avg - avg_price:.2f}")

with col_calc2:
    st.subheader("ตารางเปรียบเทียบเป้าหมาย (R1-R3)")
    # ดึงข้อมูลแนวรับแนวต้าน (ในที่นี้คือค่าคงที่จากรูปเป็นตัวอย่าง)
    resistance = [11.83, 13.83, 14.77]
    supports = [10.04, 8.67, 6.51]
    
    # สร้างตาราง Matrix
    matrix_data = []
    for s in supports:
        row = {"แนวรับ (Buy at)": f"${s}"}
        for i, r in enumerate(resistance):
            profit = ((r - s) / s) * 100
            row[f"เป้าหมาย R{i+1} (${r})"] = f"+{profit:.2f}%"
        matrix_data.append(row)
    
    st.table(pd.DataFrame(matrix_data))

# --- ส่วนของกราฟ (Technical Chart) ---
st.markdown("### 📈 กราฟเทคนิคัล (Heikin Ashi / Candle)")
st.info("ท่านสามารถใช้เครื่องมือวาดเส้นแนวรับแนวต้านได้เหมือนใน TradingView ครับ")
# ใน Streamlit เราสามารถฝัง TradingView Widget ได้โดยตรงเพื่อให้ได้ UI เหมือนรูปเป๊ะๆ
from streamlit_tradingview_widget import streamlit_tradingview_widget

streamlit_tradingview_widget(
    symbol="NASDAQ:NVDA", # เปลี่ยนตามหุ้นที่เลือก
    widget_type="chart",
    height=500,
    interval="D",
    theme="dark"
)
