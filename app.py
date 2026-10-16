import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.title("📊 Forex Strategy Backtest Web App")

# --- ส่วนตั้งค่าพารามิเตอร์ด้านข้าง (Sidebar) ---
st.sidebar.header("ตั้งค่ากลยุทธ์")
symbol = st.sidebar.selectbox("เลือกคู่เงิน", ["EURUSD=X", "GBPUSD=X", "GC=F"]) # ตัวอย่างคู่เงินและทองคำ
start_date = st.sidebar.date_input("วันที่เริ่มต้น", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("วันที่สิ้นสุด", pd.to_datetime("2026-01-01"))

fast_ma = st.sidebar.number_input("Fast MA Period", value=10)
slow_ma = st.sidebar.number_input("Slow MA Period", value=30)
initial_capital = st.sidebar.number_input("ทุนเริ่มต้น ($)", value=10000)

# --- โหลดข้อมูลราคา ---
@st.cache_data
def load_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    # จัดการโครงสร้างข้อมูลให้เป็นรูปแบบมาตรฐาน
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

data = load_data(symbol, start_date, end_date)

if not data.empty:
    st.subheader(f"กราฟราคาและข้อมูลย้อนหลัง: {symbol}")
    st.line_chart(data['Close'])

    # --- ระบบคำนวณ Backtest (Moving Average Crossover) ---
    data['Fast_MA'] = data['Close'].rolling(window=int(fast_ma)).mean()
    data['Slow_MA'] = data['Close'].rolling(window=int(slow_ma)).mean()

    # สร้างสัญญาณซื้อ/ขาย
    data['Signal'] = 0
    data['Signal'] = np.where(data['Fast_MA'] > data['Slow_MA'], 1, -1)
    data['Market_Returns'] = data['Close'].pct_change()
    data['Strategy_Returns'] = data['Market_Returns'] * data['Signal'].shift(1)

    # คำนวณกำไรสะสม
    data['Cumulative_Strategy'] = (1 + data['Strategy_Returns'].fillna(0)).cumprod() * initial_capital

    st.subheader("ผลลัพธ์การ Backtest")
    final_balance = data['Cumulative_Strategy'].iloc[-1]
    net_profit = final_balance - initial_capital

    col1, col2 = st.columns(2)
    col1.metric("มูลค่าพอร์ตสุดท้าย", f"${final_balance:,.2f}", f"${net_profit:,.2f}")

    # แสดงกราฟเปรียบเทียบผลตอบแทน
    st.line_chart(data[['Cumulative_Strategy']])
else:
    st.warning("ไม่พบข้อมูลในช่วงเวลาดังกล่าว กรุณาเปลี่ยนช่วงวันที่")
