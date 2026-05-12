import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Chairman Nu Command Center", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    .main { background-color: #0E1117; color: white; }
    .stSidebar { background-color: #1A1C24 !important; }
    h1, h2, h3 { color: #F1C40F !important; }
    .buy-card { background-color: #1E293B; padding: 20px; border-radius: 15px; border-left: 8px solid #10B981; margin-bottom: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.3); }
    .sell-card { background-color: #1E293B; padding: 20px; border-radius: 15px; border-left: 8px solid #EF4444; margin-bottom: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.3); }
    .ticker-name { color: #F1C40F; font-size: 24px; font-weight: bold; }
    .metric-box { background-color: #262730; padding: 15px; border-radius: 10px; border: 1px solid #4FA3FF; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SHARED DATA LOGIC ---
watchlist = ['NVDA', 'TSM', 'MSFT', 'PLTR', 'UPST', 'SOFI', 'GOOGL', 'AMD', 'TSLA', 'ARM', 'MU']

@st.cache_data(ttl=600)
def fetch_all_data():
    all_buys, all_sells = [], []
    prices = {}
    for ticker in watchlist:
        try:
            t = yf.Ticker(ticker)
            prices[ticker] = t.info.get('regularMarketPrice') or t.info.get('currentPrice') or 0
            df = t.insider_transactions
            if df is not None and not df.empty:
                df['Date'] = pd.to_datetime(df['Start Date'] if 'Start Date' in df.columns else df.index)
                df['Symbol'] = ticker
                all_buys.append(df[df['Text'].str.contains('Purchase', case=False, na=False)])
                all_sells.append(df[df['Text'].str.contains('Sale', case=False, na=False)])
        except: continue
    return pd.concat(all_buys), pd.concat(all_sells), prices

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/608/608153.png", width=100)
    st.title("Command Center")
    menu = st.radio(
        "เลือกโหมดการทำงาน:",
        ["🐳 ระบบจับตาปลาวาฬ", "🧮 ตารางคำนวณอัจฉริยะ", "🚀 ฟีเจอร์ในอนาคต"]
    )
    st.markdown("---")
    st.info(f"อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')}")

# Load Data
try:
    buys_df, sells_df, current_prices = fetch_all_data()

    # --- 4. PAGE: WHALE TRACKER ---
    if menu == "🐳 ระบบจับตาปลาวาฬ":
        st.header("🐳 ระบบจับตาปลาวาฬ: ซื้อ & ขาย")
        st.write("ติดตามการขยับตัวของเจ้าของบริษัท (Real-time SEC Data)")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🟢 รายการซื้อ (สะสมของ)")
            for _, row in buys_df.sort_values('Date', ascending=False).head(15).iterrows():
                st.markdown(f"""
                <div class="buy-card">
                    <span class="ticker-name">{row['Symbol']}</span> | 📅 {row['Date'].strftime('%d/%m/%Y')}<br>
                    <span style="font-size:18px;">{int(row['Shares']):,} หุ้น @ <b>${row.get('Price', 0):.2f}</b></span><br>
                    <b>{row['Insider']}</b> ({row['Position']})
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.subheader("🔴 รายการขาย (ระวังตัว)")
            for _, row in sells_df.sort_values('Date', ascending=False).head(15).iterrows():
                st.markdown(f"""
                <div class="sell-card">
                    <span class="ticker-name">{row['Symbol']}</span> | 📅 {row['Date'].strftime('%d/%m/%Y')}<br>
                    <span style="font-size:18px;">{int(row['Shares']):,} หุ้น @ <b>${row.get('Price', 0):.2f}</b></span><br>
                    <b>{row['Insider']}</b> ({row['Position']})
                </div>
                """, unsafe_allow_html=True)

    # --- 5. PAGE: CALCULATOR ---
    elif menu == "🧮 ตารางคำนวณอัจฉริยะ":
        st.header("🧮 ตารางคำนวณอัจฉริยะ (Sync แอป Dime)")
        selected = st.selectbox("เลือกหุ้นที่ท่านถือในแอป Dime:", watchlist, index=watchlist.index('UPST'))
        
        live_p = current_prices.get(selected, 0)
        
        c1, c2 = st.columns([1, 1.5])
        with c1:
            st.markdown(f'<div class="metric-box"><h3>แผนการเทรด: {selected}</h3><p>ราคาตลาด: <b>${live_p:.2f}</b></p></div>', unsafe_allow_html=True)
            dime_shares = st.number_input("จำนวนหุ้นในแอป Dime", value=0.0, step=0.1)
            dime_avg = st.number_input("ต้นทุนเฉลี่ยใน Dime (USD)", value=live_p)
            top_up = st.number_input("เงินที่จะช้อนเพิ่มคืนนี้ (USD)", value=1000.0)
            
            new_shares = top_up / live_p
            total_s = dime_shares + new_shares
            final_avg = ((dime_shares * dime_avg) + top_up) / total_s if total_s > 0 else 0
            
            st.markdown("---")
            st.metric("ต้นทุนเฉลี่ยใหม่", f"${final_avg:.2f}", f"{final_avg - dime_avg:.2f}")

        with c2:
            st.subheader("ตารางวิเคราะห์ Upside (เป้าหมายกำไร)")
            targets = [live_p * 1.2, live_p * 1.5, live_p * 2.0]
            supports = [live_p * 0.95, live_p * 0.90, live_p * 0.85]
            
            res_data = []
            for sup in supports:
                row = {"จุดช้อนรอดีด ($)": f"{sup:.2f}"}
                for i, t in enumerate(targets):
                    row[f"เป้า {i+1} (${t:.2f})"] = f"+{((t-sup)/sup)*100:.1f}%"
                res_data.append(row)
            st.table(pd.DataFrame(res_data))

    # --- 6. PAGE: FUTURE ---
    elif menu == "🚀 ฟีเจอร์ในอนาคต":
        st.header("🚀 ฟีเจอร์ที่จาร์วิสกำลังพัฒนา")
        st.write("ท่านประธานสามารถสั่งงานเพิ่มได้ที่นี่ครับ:")
        st.checkbox("ระบบแจ้งเตือนผ่าน LINE เมื่อปลาวาฬซื้อไม้ใหญ่", value=True)
        st.checkbox("ระบบ AI วิเคราะห์ความเสี่ยงจากข่าวลือ (Sentiment Analysis)")
        st.checkbox("ตารางสรุปปันผลรายปีจากพอร์ต Dime")
        st.info("ส่งคำสั่งใหม่ให้จาร์วิสได้ตลอดเวลาครับ!")

except Exception as e:
    st.error(f"ระบบกำลังเตรียมข้อมูล: {e}")
