import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Chairman Nu Command Center V4.4", layout="wide")

LINE_ACCESS_TOKEN = "Tt4FXXuT6v9qP2m9p9p9p9p9p9p9p9p9" 
USER_ID = "U60411800f135b37699709f1938507c31"

def send_line_message(message):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'}
    data = {'to': USER_ID, 'messages': [{'type': 'text', 'text': message}]}
    try: return requests.post(url, headers=headers, json=data)
    except: return None

# --- 2. DATA FETCHING ---
watchlist = ['NVDA', 'TSM', 'MSFT', 'PLTR', 'UPST', 'SOFI', 'GOOGL', 'AMD', 'TSLA', 'ARM', 'MU']

@st.cache_data(ttl=600)
def fetch_all_data():
    all_data = []
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
                all_data.append(df)
        except: continue
    return pd.concat(all_data) if all_data else pd.DataFrame(), prices

# --- 3. MAIN LOGIC ---
with st.sidebar:
    st.title("👨‍✈️ Command Center")
    menu = st.radio("เลือกโหมด:", ["🐳 จับตาปลาวาฬ (ทุกรายการ)", "🧮 ตารางคำนวณ", "📡 ระบบ LINE"])
    st.info(f"อัปเดต: {datetime.now().strftime('%H:%M:%S')}")

try:
    full_df, current_prices = fetch_all_data()

    if menu == "🐳 จับตาปลาวาฬ (ทุกรายการ)":
        st.header("🐳 รายงานความเคลื่อนไหวคนใน (Real-time)")
        if not full_df.empty:
            buys = full_df[~full_df['Text'].str.contains('Sale', case=False, na=False)]
            sells = full_df[full_df['Text'].str.contains('Sale', case=False, na=False)]
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🟢 รายการรับหุ้น/ซื้อเพิ่ม")
                for _, row in buys.sort_values('Date', ascending=False).head(15).iterrows():
                    st.success(f"**{row['Symbol']}** | {row['Date'].strftime('%d/%m/%y')}\n\n**{row['Insider']}** ({row['Position']})\n\n{int(row['Shares']):,} หุ้น | ประเภท: {row['Text']}")
            
            with col2:
                st.subheader("🔴 รายการขาย/โอนออก")
                for _, row in sells.sort_values('Date', ascending=False).head(15).iterrows():
                    st.error(f"**{row['Symbol']}** | {row['Date'].strftime('%d/%m/%y')}\n\n**{row['Insider']}** ({row['Position']})\n\n{int(row['Shares']):,} หุ้น | ประเภท: {row['Text']}")
        else:
            st.warning("กำลังดึงข้อมูล... หากยังไม่ขึ้นกรุณารอสักครู่ครับ")

    elif menu == "🧮 ตารางคำนวณ":
        st.header("🧮 ตารางคำนวณอัจฉริยะ (Sync Dime)")
        selected = st.selectbox("เลือกหุ้น:", watchlist, index=watchlist.index('UPST'))
        live_p = current_prices.get(selected, 0)
        
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"ราคาตลาดปัจจุบัน: **${live_p:.2f}**")
            dime_shares = st.number_input("จำนวนหุ้นใน Dime", value=0.0)
            dime_avg = st.number_input("ต้นทุนเดิม (USD)", value=live_p)
            top_up = st.number_input("เงินที่ลงทุนเพิ่ม (USD)", value=1000.0)
            
            new_sh = top_up / live_p if live_p > 0 else 0
            final_avg = ((dime_shares * dime_avg) + top_up) / (dime_shares + new_sh) if (dime_shares + new_sh) > 0 else 0
            st.metric("ราคาเฉลี่ยใหม่", f"${final_avg:.2f}", f"{final_avg - dime_avg:.2f}")

    elif menu == "📡 ระบบ LINE":
        st.header("📡 ศูนย์ควบคุม LINE")
        st.write(f"**สถานะ:** เชื่อมต่อกับ User ID: `{USER_ID}`")
        test_msg = st.text_input("พิมพ์ข้อความทดสอบ:", "จาร์วิสรายงานตัวครับท่านประธานนุ!")
        if st.button("🚀 ส่งข้อความทดสอบ"):
            res = send_line_message(test_msg)
            if res and res.status_code == 200:
                st.success("ส่งเรียบร้อย! ลองเช็คในมือถือท่านประธานดูครับ")
                st.balloons()
            else:
                st.error("ส่งไม่สำเร็จ ตรวจสอบสถานะอีกครั้งครับ")

except Exception as e:
    st.error(f"ระบบขัดข้อง: {e}")
