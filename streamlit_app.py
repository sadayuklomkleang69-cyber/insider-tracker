import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Chairman Nu Command Center V5.4", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #121212; color: white; }
    h1, h2, h3 { color: #4FA3FF !important; }
    .buy-card { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 5px solid #2ECC71; margin-bottom: 10px; }
    .sell-card { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 5px solid #E74C3C; margin-bottom: 10px; }
    .metric-box { background-color: #262730; padding: 15px; border-radius: 10px; border: 1px solid #4FA3FF; }
    </style>
    """, unsafe_allow_html=True)

LINE_ACCESS_TOKEN = "Tt4FXXuT6v9qP2m9p9p9p9p9p9p9p9p9" 
USER_ID = "U60411800f135b37699709f1938507c31"

def send_line_message(message):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'}
    data = {'to': USER_ID, 'messages': [{'type': 'text', 'text': message}]}
    try: return requests.post(url, headers=headers, json=data)
    except: return None

# --- 2. TRADINGVIEW SYNC WATCHLIST (หุ้นที่ท่านเฝ้าติดตาม) ---
watchlist = [
    'NVDA', 'TSM', 'ASML', 'PLTR', 'GOOGL', 'AVGO', 'MSFT', 'AMZN', 'ARM', 
    'AMD', 'MU', 'NBIS', 'RKLB', 'JEPQ', 'SPYI', 'SOFI', 'UPST'
]

@st.cache_data(ttl=600)
def fetch_all_data():
    all_buys, all_sells = [], []
    prices = {}
    for ticker in watchlist:
        try:
            t = yf.Ticker(ticker)
            live_p = t.info.get('regularMarketPrice') or t.info.get('currentPrice') or 0
            prices[ticker] = live_p
            df = t.insider_transactions
            if df is not None and not df.empty:
                df['Date'] = pd.to_datetime(df['Start Date'] if 'Start Date' in df.columns else df.index)
                df['Symbol'] = ticker
                df['DisplayPrice'] = df['Price'].apply(lambda x: live_p if x == 0 or pd.isna(x) else x)
                
                buys = df[df['Text'].str.contains('Purchase', case=False, na=False)]
                sells = df[df['Text'].str.contains('Sale', case=False, na=False)]
                
                if not buys.empty: all_buys.append(buys)
                if not sells.empty: all_sells.append(sells)
        except: continue
    
    final_buys = pd.concat(all_buys) if all_buys else pd.DataFrame()
    final_sells = pd.concat(all_sells) if all_sells else pd.DataFrame()
    return final_buys, final_sells, prices

# --- 3. UI & NAVIGATION ---
with st.sidebar:
    st.title("👨‍✈️ Command Center")
    menu = st.radio("เลือกโหมด:", ["🐳 ระบบจับตาปลาวาฬ", "🧮 ตารางคำนวณอัจฉริยะ", "📡 ระบบ LINE"])
    st.info(f"อัปเดต: {datetime.now().strftime('%H:%M:%S')}")

try:
    buys_df, sells_df, current_prices = fetch_all_data()

    if menu == "🐳 ระบบจับตาปลาวาฬ":
        st.header("🐳 รายงานความเคลื่อนไหว (Sync TradingView)")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🟢 รายการซื้อ (Insiders Buying)")
            if not buys_df.empty:
                for _, row in buys_df.sort_values('Date', ascending=False).head(20).iterrows():
                    st.markdown(f'<div class="buy-card"><b>{row["Symbol"]}</b> | {row["Date"].strftime("%d/%m/%y")}<br>ผู้ซื้อ: {row["Insider"]} ({row.get("Position", "N/A")})<br>จำนวน: {int(row["Shares"]):,} หุ้น @ <b>${row["DisplayPrice"]:.2f}</b></div>', unsafe_allow_html=True)
            else: st.warning("ไม่พบรายการซื้อในหุ้นกลุ่มที่ท่านเลือก")
            
        with c2:
            st.subheader("🔴 รายการขาย (Insiders Selling)")
            if not sells_df.empty:
                for _, row in sells_df.sort_values('Date', ascending=False).head(20).iterrows():
                    st.markdown(f'<div class="sell-card"><b>{row["Symbol"]}</b> | {row["Date"].strftime("%d/%m/%y")}<br>ผู้ขาย: {row["Insider"]} ({row.get("Position", "N/A")})<br>จำนวน: {int(row["Shares"]):,} หุ้น @ <b>${row["DisplayPrice"]:.2f}</b></div>', unsafe_allow_html=True)
            else: st.warning("ไม่พบรายการขายในหุ้นกลุ่มที่ท่านเลือก")

    elif menu == "🧮 ตารางคำนวณอัจฉริยะ":
        st.header("🧮 ตารางคำนวณอัจฉริยะ (Sync Dime)")
        selected = st.selectbox("เลือกหุ้นจาก TradingView List:", watchlist)
        live_p = current_prices.get(selected, 0)
        
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.markdown(f'<div class="metric-box">ราคาปัจจุบัน {selected}: <b>${live_p:.2f}</b></div><br>', unsafe_allow_html=True)
            d_shares = st.number_input("หุ้นใน Dime", value=0.0)
            d_avg = st.number_input("ต้นทุนเดิม (USD)", value=live_p)
            top_up = st.number_input("เงินลงทุนเพิ่ม (USD)", value=1000.0)
            
            new_sh = top_up / live_p if live_p > 0 else 0
            final_avg = ((d_shares * d_avg) + top_up) / (d_shares + new_sh) if (d_shares + new_sh) > 0 else 0
            st.metric("ราคาเฉลี่ยใหม่", f"${final_avg:.2f}", f"{final_avg - d_avg:.2f}")

        with col2:
            st.subheader("🎯 วิเคราะห์จุดช้อน & เป้าหมายกำไร")
            if live_p > 0:
                targets = [live_p * 1.2, live_p * 1.5, live_p * 2.0]
                supports = [live_p * 0.95, live_p * 0.90, live_p * 0.85]
                res_data = []
                for sup in supports:
                    row = {"จุดช้อน ($)": f"{sup:.2f}"}
                    for i, t in enumerate(targets):
                        row[f"เป้า {i+1} (${t:.2f})"] = f"+{((t-sup)/sup)*100:.1f}%"
                    res_data.append(row)
                st.table(pd.DataFrame(res_data))

    elif menu == "📡 ระบบ LINE":
        st.header("📡 ศูนย์ควบคุม LINE")
        if st.button("🚀 ส่งข้อความทดสอบ"):
            res = send_line_message("จาร์วิสรายงานตัว! เชื่อมต่อหุ้นจาก TradingView ครบถ้วนแล้วครับท่านประธาน!")
            if res and res.status_code == 200: st.success("ส่งเรียบร้อย!"); st.balloons()
            else: st.error("ส่งไม่สำเร็จ")

except Exception as e:
    st.error(f"ระบบขัดข้อง: {e}")
