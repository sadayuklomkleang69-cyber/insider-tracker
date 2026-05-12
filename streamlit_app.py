import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Chairman Nu Insider", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #121212; color: white; }
    h1, h2, h3 { color: #4FA3FF !important; font-family: 'Kanit', sans-serif; }
    .buy-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #2ECC71;
        margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    .ticker-name { color: #F1C40F; font-size: 22px; font-weight: bold; }
    .price-text { color: #4FA3FF; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER ---
st.title('🎯 ระบบจับตา "คนใน" (ไม่ต้องใช้คีย์)')
st.write(f"ดึงข้อมูลตรงจาก Yahoo Finance | อัปเดตล่าสุด: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# --- 3. WATCHLIST (หุ้นปลาวาฬของท่านประธาน) ---
watchlist = ['NVDA', 'TSM', 'MSFT', 'PLTR', 'UPST', 'SOFI', 'GOOGL', 'AMD', 'TSLA']

@st.cache_data(ttl=600)
def get_yfinance_insider():
    all_data = []
    for ticker in watchlist:
        try:
            t = yf.Ticker(ticker)
            df = t.insider_transactions
            if df is not None and not df.empty:
                # กรองเฉพาะรายการซื้อ (Purchase)
                buys = df[df['Text'].str.contains('Purchase', case=False, na=False)].copy()
                if not buys.empty:
                    buys['Symbol'] = ticker
                    all_data.append(buys)
        except:
            continue
    return pd.concat(all_data) if all_data else pd.DataFrame()

# --- 4. EXECUTION & DISPLAY ---
try:
    with st.spinner('จาร์วิสกำลังสแกนหาปลาวาฬในตลาด...'):
        final_df = get_yfinance_insider()

    if not final_df.empty:
        col_left, col_right = st.columns([1, 2])
        
        with col_left:
            st.subheader("📊 สัดส่วนการเก็บหุ้น")
            fig = px.pie(final_df, values='Shares', names='Symbol', hole=0.7,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_traces(textfont=dict(color='black', size=14), textinfo='percent+label')
            fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.subheader("💎 รายการซื้อที่น่าสนใจ")
            # เรียงตามวันที่ล่าสุด
            final_df = final_df.sort_values(by='Date', ascending=False).head(10)
            
            for _, row in final_df.iterrows():
                st.markdown(f"""
                <div class="buy-card">
                    <table style="width:100%;">
                        <tr>
                            <td style="width:20%;"><span class="ticker-name">{row['Symbol']}</span><br><small>{row['Date'].strftime('%Y-%m-%d')}</small></td>
                            <td style="width:30%; text-align:center;">จำนวน: {int(row['Shares']):,} หุ้น</td>
                            <td style="width:20%; text-align:center;"><span class="price-text">${row['Price']:.2f}</span></td>
                            <td style="width:30%; text-align:right;"><b>{row['Insider']}</b><br><small>{row['Position']}</small></td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("💡 ช่วงนี้เหล่าปลาวาฬใน Watchlist ยังเฝ้าดูสถานการณ์อยู่ครับ (ยังไม่มีรายการซื้อเพิ่ม)")
        st.write("**หุ้นที่จาร์วิสกำลังจับตาให้:** " + ", ".join(watchlist))

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดทางเทคนิค: {e}")

if st.button('🔄 รีเฟรชข้อมูล'):
    st.rerun()
