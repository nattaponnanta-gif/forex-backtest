import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.title("📉 Forex Manual Backtest & Bar Replay App")

# 1. โหลดข้อมูลราคาย้อนหลัง
@st.cache_data
def load_data():
    df = yf.download("EURUSD=X", start="2025-01-01", end="2026-01-01")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

data = load_data()

# 2. ตั้งค่าระบบ Session State สำหรับควบคุมการ Replay กราฟ
if 'index' not in st.session_state:
    st.session_state.index = 50  # เริ่มต้นแสดง 50 แท่งแรก
if 'balance' not in st.session_state:
    st.session_state.balance = 10000.0
if 'position' not in st.session_state:
    st.session_state.position = None  # สถานะ: None, 'BUY', 'SELL'
    st.session_state.entry_price = 0.0

# 3. แผงควบคุมการ Replay ด้านข้าง (Sidebar)
st.sidebar.header("🕹️ ควบคุม Bar Replay")
col_b1, col_b2 = st.sidebar.columns(2)

if col_b1.button("▶️ Next Bar (+1)"):
    if st.session_state.index < len(data):
        st.session_state.index += 1

if col_b2.button("⏩ Fast Forward (+10)"):
    if st.session_state.index + 10 < len(data):
        st.session_state.index += 10

if st.sidebar.button("🔄 รีเซ็ตการจำลอง"):
    st.session_state.index = 50
    st.session_state.balance = 10000.0
    st.session_state.position = None

# ตัดข้อมูลตามแท่งเทียนปัจจุบันที่จำลอง
current_data = data.iloc[:st.session_state.index]
current_price = float(current_data['Close'].iloc[-1])

# 4. แสดงผลกราฟและราคาปัจจุบัน
st.subheader(f"คู่เงิน: EURUSD | ราคาปัจจุบัน: {current_price:.5f}")
st.line_chart(current_data['Close'])

# 5. ส่วนจำลองการกดเทรด (Trading Panel)
col1, col2, col3 = st.columns(3)

col1.metric("ทุน / พอร์ตปัจจุบัน", f"${st.session_state.balance:,.2f}")

with col2:
    if st.session_state.position is None:
        if st.button("🟢 BUY (Long)", use_container_width=True):
            st.session_state.position = 'BUY'
            st.session_state.entry_price = current_price
            st.rerun()
        if st.button("🔴 SELL (Short)", use_container_width=True):
            st.session_state.position = 'SELL'
            st.session_state.entry_price = current_price
            st.rerun()
    else:
        if st.button("❌ Close Position", use_container_width=True):
            # คำนวณกำไรขาดทุนเบื้องต้น
            if st.session_state.position == 'BUY':
                profit = (current_price - st.session_state.entry_price) * 10000
            else:
                profit = (st.session_state.entry_price - current_price) * 10000
            
            st.session_state.balance += profit
            st.session_state.position = None
            st.rerun()

with col3:
    if st.session_state.position is not None:
        st.info(f"สถานะ: เปิด {st.session_state.position}\nราคาเข้า: {st.session_state.entry_price:.5f}")
    else:
        st.write("สถานะ: ไม่มีออร์เดอร์ (Flat)")

st.write(f"กำลังจำลองแท่งเทียนที่: {st.session_state.index} จากทั้งหมด {len(data)} แท่ง")
