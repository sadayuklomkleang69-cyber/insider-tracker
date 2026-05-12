import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Chairman Nu Command Center V3", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; background-color: #0E1117; color: white; }
    .stSidebar { background-color: #161B22 !important; }
    h1, h2, h3 { color: #FFD700 !important; }
    .card { background-color: #1C2128; padding: 20px; border-radius: 15px; border: 1px solid #30363D; margin-bottom: 15px; }
    .sentiment-pos { color: #23D18B; font-weight: bold; }
    .sentiment-neg { color: #F85149; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
watchlist = ['NVDA', 'TSM', 'MSFT', 'PLTR', 'UPST', 'SOFI', 'GOOGL', 'AMD', 'TSLA', 'ARM', 'MU']

def send_line_notify(token, message):
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {token}'}
    data = {'message': message}
    return requests.post(url, headers=headers, data=data)

@st.cache_data(ttl=600)
def fetch_whale_and_sentiment():
    all_buys, all_sells = [], []
    prices = {}
    for ticker in watchlist:
        try:
            t = yf.Ticker(ticker)
            prices[ticker] = t.info.get('currentPrice') or 0
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
    st.title("🎛️ Command Center")
    menu = st.radio("เลือกโหมดการทำงาน:", [
        "🐳 ระบบจับตาปลาวาฬ", 
        "💬 วิเคราะห์ความรู้สึก AI", 
        "🧮 ตารางคำนวณอัจฉริยะ", 
        "🔔 ตั้งค่าแจ้งเตือน LINE"
    ])
    st.markdown("---")
    st.caption(f"Status: Online | {datetime.now().strftime('%H:%M:%S')}")

# Load Initial Data
buys_df, sells_df, current_prices = fetch_whale_and_sentiment()

# --- 4. PAGE LOGIC ---

if menu == "🐳 ระบบจับตาปลาวาฬ":
    st.header("🐳 รายการขยับตัวล่าสุดของปลาวาฬ")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🟢 ฝั่งซื้อ (Insiders Buying)")
        for _, row in buys_df.sort_values('Date', ascending=False).head(10).iterrows():
            with st.container():
                st.markdown(f"""<div class="card">
                <b style="font-size:20px; color:#FFD700;">{row['Symbol']}</b> | 📅 {row['Date'].strftime('%d/%m/%Y')}<br>
                ซื้อ {int(row['Shares']):,} หุ้น @ <b>${row.get('Price', 0):.2f}</b><br>
                โดย: {row['Insider']} ({row['Position']})</div>""", unsafe_allow_html=True)

    with col2:
        st.subheader("🔴 ฝั่งขาย (Insiders Selling)")
        for _, row in sells_df.sort_values('Date', ascending=False).head(10).iterrows():
            st.markdown(f"""<div class="card">
                <b style="font-size:20px; color:#F85149;">{row['Symbol']}</b> | 📅 {row['Date'].strftime('%d/%m/%Y')}<br>
                ขาย {int(row['Shares']):,} หุ้น @ <b>${row.get('Price', 0):.2f}</b><br>
                โดย: {row['Insider']}</div>""", unsafe_allow_html=True)

elif menu == "💬 วิเคราะห์ความรู้สึก AI":
    st.header("💬 AI News Sentiment Analysis")
    target = st.selectbox("เลือกหุ้นเพื่อวิเคราะห์ข่าวล่าสุด:", watchlist)
    t_obj = yf.Ticker(target)
    news = t_obj.news
    
    st.subheader(f"วิเคราะห์ข่าวล่าสุดของ {target}")
    if news:
        pos_count = 0
        for item in news[:5]:
            title = item['title']
            # Simple AI Simulation (Logic keyword based)
            score = "Neutral"
            if any(word in title.lower() for word in ['bull', 'buy', 'growth', 'strong', 'up', 'beat', 'win']):
                score = "Bullish 🚀"
                pos_count += 1
            elif any(word in title.lower() for word in ['sell', 'fall', 'risk', 'miss', 'down', 'weak', 'loss']):
                score = "Bearish 📉"
            
            st.markdown(f"""<div class="card">
                <b>{title}</b><br>
                AI Pulse: <span class="{'sentiment-pos' if 'Bullish' in score else 'sentiment-neg' if 'Bearish' in score else ''}">{score}</span><br>
                <a href="{item['link']}" target="_blank">อ่านข่าวเต็ม</a></div>""", unsafe_allow_html=True)
        
        st.metric("AI Confidence Score", f"{(pos_count/5)*100}%", "Bullish Trend" if pos_count > 2 else "Wait and See")
    else: st.info("ไม่พบข่าวล่าสุดสำหรับหุ้นตัวนี้")

elif menu == "🧮 ตารางคำนวณอัจฉริยะ":
    st.header("🧮 คำนวณต้นทุนจากแอป Dime")
    # ... (Keep existing calculator logic here)
    st.write("ใช้ข้อมูลจากแอป Dime มาวางแผนการช้อนซื้อ")
    selected = st.selectbox("เลือกหุ้น:", watchlist)
    live_p = current_prices.get(selected, 0)
    d_shares = st.number_input("หุ้นที่มีใน Dime", value=0.0)
    d_avg = st.number_input("ต้นทุนเดิม (Avg)", value=live_p)
    topup = st.number_input("เงินที่จะซื้อเพิ่ม (USD)", value=1000.0)
    new_avg = ((d_shares * d_avg) + topup) / (d_shares + (topup/live_p)) if (d_shares + topup) > 0 else 0
    st.metric("ต้นทุนเฉลี่ยใหม่", f"${new_avg:.2f}", f"{new_avg - d_avg:.2f}")

elif menu == "🔔 ตั้งค่าแจ้งเตือน LINE":
    st.header("🔔 ระบบแจ้งเตือน LINE Notify")
    st.write("รับการแจ้งเตือนทันทีเมื่อตรวจพบ 'ปลาวาฬ' ขยับตัว")
    token = st.text_input("กรอก LINE Notify Token ของท่าน:", type="password")
    if st.button("🚀 ทดสอบการเชื่อมต่อ"):
        if token:
            res = send_line_notify(token, f"✅ จาร์วิสรายงานตัว! ระบบแจ้งเตือนของท่านประธานนุพร้อมทำงานแล้วครับ | {datetime.now()}")
            if res.status_code == 200: st.success("ส่งข้อความทดสอบสำเร็จ! โปรดตรวจสอบในแอป LINE ของท่าน")
            else: st.error("Token ไม่ถูกต้อง โปรดตรวจสอบอีกครั้ง")
        else: st.warning("โปรดใส่ Token ก่อนกดทดสอบ")
    st.markdown("""--- 
    ### 💡 วิธีขอ Token:
    1. เข้าไปที่ [LINE Notify](https://notify-bot.line.me/) แล้ว Login
    2. กด 'My Page' และเลือก 'Generate Token'
    3. เลือกกลุ่มที่ต้องการให้แจ้งเตือน แล้วคัดลอกรหัสมาวางที่นี่ครับ""")
