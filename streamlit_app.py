import streamlit as st
import pandas as pd

# 1. 頁面基礎設定
st.set_page_config(page_title="馬尼專用蝦皮計算機", layout="wide")

# 2. PDF 精確資料庫
FEE_DB = {
    "手機平板與周邊": {"手機": [5.5, 3.8], "平板電腦": [5.5, 4.0], "穿戴裝置": [5.5, 4.5], "對講機": [6.5, 9.5]},
    "家用電器": {"大型家電": [5.3, 5.8], "生活/廚房家電": [5.5, 6.0], "投影機": [7.5, 8.5]},
    "電腦與周邊配件": {"筆記型電腦": [5.0, 4.0], "桌上型電腦": [5.5, 5.0], "螢幕裝置": [5.5, 5.5], "電腦零組件": [6.0, 6.5]},
    "影音/相機": {"耳機/藍牙耳機": [5.5, 6.5], "音響/喇叭": [6.0, 7.5], "相機": [5.0, 5.0]}
}

if 'c_fees' not in st.session_state: st.session_state.c_fees = []

# 3. 自訂 CSS 樣式優化
f_sz = st.sidebar.slider("字體縮放", 12, 24, 16)
st.markdown(f"""
    <style>
    html, body, [class*="st-"] {{ font-size: {f_sz}px; font-family: 'Microsoft JhengHei'; }}
    .result-box {{ 
        border: 2px solid #EE4D2D; 
        padding: 20px; 
        border-radius: 12px; 
        background-color: #ffffff;
        margin-bottom: 15px;
    }}
    .price-text {{ color: #3498DB; font-weight: bold; }}
    .expense-text {{ color: #E74C3C; }}
    .profit-text {{ color: #27AE60; font-size: 1.4em; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# 4. 三欄式佈局
col_in, col_拍, col_商 = st.columns([1, 1, 1])

# --- 欄位 1: 馬尼試算輸入 ---
with col_in:
    st.header("馬尼試算輸入")
    price = st.number_input("成交單價", min_value=0, value=1000, step=100)
    cost = st.number_input("商品成本", min_value=0, value=500, step=100)
    pay_r = st.number_input("金流費率(%)", value=2.5, step=0.1)
    ev = st.number_input("活動日費用", value=60)
    
    m_cat = st.selectbox("商品大類", list(FEE_DB.keys()))
    s_cat = st.selectbox("細項分類", list(FEE_DB[m_cat].keys()))
    
    st.divider()
    n_n = st.text_input("自訂名稱")
    n_r = st.number_input("自訂費率(%)", value=0.0, step=0.1)
    if st.button("新增自訂"):
        if n_n: st.session_state.c_fees.append({"name": n_n, "rate": n_r/100, "active": True})
    
    st.divider()
    export_df = pd.DataFrame({"項目": ["單價", "成本", "活動費"], "數值": [price, cost, ev]})
    st.download_button("💾 匯出試算表 (CSV)", export_df.to_csv(index=False).encode('utf-8-sig'), "馬尼報告.csv")

# 5. 計算核心邏輯
cust_r_total = sum([f['rate'] for f in st.session_state.c_fees if f['active']])
p_rate_pdf, s_rate_pdf = FEE_DB[m_cat][s_cat]

def render_report(title, t_rate, coin_r, color):
    tf = price * (t_rate / 100)
    pf = price * (pay_r / 100)
    cf = price * coin_r
    cust_f = price * cust_r_total
    total_deduct = tf + pf + cf + ev + cust_f
    payout = price - total_deduct
    profit = payout - cost
    
    st.markdown(f"""
    <div class="result-box">
        <h3 style="color:{color};">{title}</h3>
        <p>單價: <span class="price-text">{price:,.0f} 元</span></p>
        <p>成本: {cost:,.0f} 元</p>
        <hr>
        <p class="expense-text">成交手續費: -{tf:,.2f} 元</p>
        <p class="expense-text">金流服務費: -{pf:,.2f} 元</p>
        <p class="expense-text">蝦幣回饋費: -{cf:,.2f} 元</p>
        <p class="expense-text">活動方案費: -{ev:,.0f} 元</p>
        <hr>
        <p>實拿金額: <b>{payout:,.2f} 元</b></p>
        <p>預計純利: <span class="profit-text">{profit:,.2f} 元</span></p>
    </div>
    """, unsafe_allow_html=True)

# --- 欄位 2: 蝦拍 (10% 2.5%) ---
with col_拍:
    render_report("蝦拍 (10% 2.5%)", p_rate_pdf, 0.025, "#333333")

# --- 欄位 3: 蝦商 (5% 1.5%) ---
with col_商:
    render_report("蝦商 (5% 1.5%)", s_rate_pdf, 0.015, "#EE4D2D")