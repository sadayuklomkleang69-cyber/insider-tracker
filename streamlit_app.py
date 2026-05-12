import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Chairman Nu Command Center V4.2", layout="wide")

# รหัสของท่านประธาน (จาร์วิสล็อกไว้ให้แล้ว)
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
                # แก้ไขราคา 0.00 ให้เป็นราคาตลาดปัจจุบัน
                df['DisplayPrice'] = df['Price'].apply(lambda x: live_p if x == 0 or pd.isna(x) else x)
                
                all_buys.append(df[df['Text'].str.contains('Purchase', case=False, na=False)])
                all_sells.append(df[df['Text'].str.contains('Sale', case=False, na=False)])
        except: continue
    return pd.concat(all_buys) if all_buys else pd.DataFrame(), pd.concat(all_sells) if all_sells else pd.DataFrame(), prices

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("👨‍✈️ Command Center")
    menu = st.radio("เลือกโหมดการทำงาน:", ["🐳 ระบบจับตาปลาวาฬ", "🧮 ตารางคำนวณอัจฉริยะ", "📡 ระบบเชื่อมต่อ LINE"])
    st.markdown("---")
    st.info(f"อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')}")

# Load Data
try:
    buys_df, sells_df, current_prices = fetch_all_data()

    # --- 4. PAGE: WHALE TRACKER ---
    if menu == "🐳 ระบบจับตาปลาวาฬ":
        st.header("🐳 รายงานปลาวาฬขยับตัว (โหมดโชว์รายละเอียด)")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🟢 ฝั่งซื้อ (Insiders Buying)")
            if not buys_df.empty:
                for _, row in buys_df.sort_values('Date', ascending=False).head(12).iterrows():
                    st.success(f"""
                    **หุ้น: {row['Symbol']}** | {row['Date'].strftime('%d/%m/%y')}
                    * **ผู้ซื้อ:** {row['Insider']}
                    * **ตำแหน่ง:** {row.get('Position', 'N/A')}
                    * **จำนวน:** {int(row['Shares']):,} หุ้น @ **${row['DisplayPrice']:.2f}**
                    """)
            else: st.write("ไม่พบข้อมูลการซื้อ")
        
        with col2:
            st.subheader("🔴 ฝั่งขาย (Insiders Selling)")
            if not sells_df.empty:
                for _, row in sells_df.sort_values('Date', ascending=False).head(12).iterrows():
                    st.error(f"""
                    **หุ้น: {row['Symbol']}** | {row['Date'].strftime('%d/%m/%y')}
                    * **ผู้ขาย:** {row['Insider']}
                    * **ตำแหน่ง:** {row.get('Position', 'N/A')}
                    * **จำนวน:** {int(row['Shares']):,} หุ้น @ **${row['DisplayPrice']:.2f}**
                    """)
            else: st.write("ไม่พบข้อมูลการขาย")

    # --- 5. PAGE: CALCULATOR ---
    elif menu == "🧮 ตารางคำนวณอัจฉริยะ":
        st.header("🧮 ตารางคำนวณอัจฉริยะ (Sync Dime)")
        selected = st.selectbox("เลือกหุ้น:", watchlist, index=watchlist.index('UPST'))
        live_p = current_prices.get(selected, 0)
        c1, c2 = st.columns(2)
        with c1:
            dime_shares = st.number_input("จำนวนหุ้นใน Dime", value=0.0)
            dime_avg = st.number_input("ต้นทุนเดิม (USD)", value=live_p)
            top_up = st.number_input("เงินที่ลงทุนเพิ่ม (USD)", value=1000.0)
            new_sh = top_up / live_p if live_p > 0 else 0
            final_avg = ((dime_shares * dime_avg) + top_up) / (dime_shares + new_sh) if (dime_shares + new_sh) > 0 else 0
            st.metric("ราคาเฉลี่ยใหม่", f"${final_avg:.2f}", f"{final_avg - dime_avg:.2f}")

    # --- 6. PAGE: LINE SYSTEM ---
    elif menu == "📡 ระบบเชื่อมต่อ LINE":
        st.header("📡 ศูนย์ควบคุมระบบส่งข้อความ")
        st.write(f"**สถานะ:** เชื่อมต่อกับ User ID: `{USER_ID}`")
        test_msg = st.text_input("พิมพ์ข้อความทดสอบ:", "จาร์วิสรายงานตัวครับท่านประธานนุ!")
        if st.button("🚀 ส่งข้อความทดสอบเข้า LINE"):
            res = send_line_message(test_msg)
            if res and res.status_code == 200:
                st.success("ส่งเรียบร้อย! ลองเช็คในมือถือท่านประธานดูครับ")
                st.balloons()
            else: st.error("ส่งไม่สำเร็จ ตรวจสอบสถานะอีกครั้งครับ")

except Exception as e:
    st.error(f"ระบบขัดข้อง: {e}")
