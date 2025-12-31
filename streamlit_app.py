import streamlit as st
import pandas as pd

# 1. 頁面標題
st.set_page_config(page_title="馬尼專用蝦皮計算機", layout="wide")

# 2. 資料庫 (僅一般賣家使用)
FEE_DB = {
    "手機平板與周邊": {"手機": [5.5, 3.8], "平板電腦": [5.5, 4.0], "穿戴裝置": [5.5, 4.5]},
    "影音/相機": {"耳機/麥克風": [5.5, 6.5], "音響/喇叭": [6.0, 7.5], "相機": [5.0, 5.0]}
}

if 'c_fees' not in st.session_state: 
    st.session_state.c_fees = []

# 3. CSS 樣式美化
st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 15px; font-family: 'Microsoft JhengHei'; }
    .result-box { 
        border: 2px solid #EE4D2D; 
        padding: 15px; 
        border-radius: 12px; 
        background-color: #fdfdfd;
        min-height: 450px;
    }
    .direct-box { border-color: #2980B9; }
    .price-text { color: #3498DB; font-weight: bold; }
    .expense-text { color: #E74C3C; margin: 2px 0; }
    .profit-text { color: #27AE60; font-size: 1.5em; font-weight: bold; }
    hr { border: 0; border-top: 1px solid #eee; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# 4. 四等分布局
col_in, col_拍, col_商, col_直送 = st.columns([1, 1, 1, 1])

# --- 欄位 1: 馬尼試算輸入 ---
with col_in:
    st.subheader("馬尼輸入")
    price = st.number_input("成交單價", min_value=0, value=1000)
    cost = st.number_input("商品成本", min_value=0, value=500)
    
    st.divider()
    st.caption("一般賣家設定 (蝦拍/蝦商)")
    pay_r = st.number_input("金流費率(%)", value=2.5)
    ev = st.number_input("活動日費用", value=60)
    m_cat = st.selectbox("商品大類", list(FEE_DB.keys()))
    s_cat = st.selectbox("細項分類", list(FEE_DB[m_cat].keys()))
    
    st.divider()
    st.caption("直送專屬設定")
    direct_type = st.selectbox("直送品項類型", ["手機/平板 (5%+2%)", "耳機-手機品牌 (10%+2%)", "耳機-其他品牌 (12%+2%)"])

# --- 邏輯計算 ---
# A. 一般賣家 (蝦拍/蝦商)
p_rate, s_rate = FEE_DB[m_cat][s_cat]
# 蝦拍
tf_拍 = price * (p_rate / 100)
pf_拍 = price * (pay_r / 100)
cf_拍 = price * 0.025
payout_拍 = price - tf_拍 - pf_拍 - cf_拍 - ev
profit_拍 = payout_拍 - cost

# 蝦商
tf_商 = price * (s_rate / 100)
pf_商 = price * (pay_r / 100)
cf_商 = price * 0.015
payout_商 = price - tf_商 - pf_商 - cf_商 - ev
profit_商 = payout_商 - cost

# B. 蝦皮直送 (僅使用前毛/後毛)
if "手機/平板" in direct_type:
    f_margin, b_margin = 5.0, 2.0
else:
    f_margin = 10.0 if "手機品牌" in direct_type else 12.0
    b_margin = 2.0

f_fee = price * (f_margin / 100)
b_fee = price * (b_margin / 100)
payout_直 = price - f_fee - b_fee
profit_直 = payout_直 - cost

# --- 畫面顯示 (修復代碼呈現問題) ---
with col_拍:
    st.markdown(f"""<div class="result-box">
    <h3 style="color:#333;">蝦拍 (一般)</h3>
    <p>單價: <span class="price-text">{price:,.0f}</span></p>
    <p>成本: {cost:,.0f}</p>
    <hr>
    <p class="expense-text">成交手續({p_rate}%): -{tf_拍:,.0f}</p>
    <p class="expense-text">蝦幣回饋(2.5%): -{cf_拍:,.0f}</p>
    <p class="expense-text">金流/活動: -{(pf_拍+ev):,.0f}</p>
    <hr>
    <p>實拿: <b>{payout_拍:,.0f}</b></p>
    <p>預計純利:</p>
    <p class="profit-text">{profit_拍:,.0f} 元</p>
    </div>""", unsafe_allow_html=True)

with col_商:
    st.markdown(f"""<div class="result-box">
    <h3 style="color:#EE4D2D;">蝦商 (商城)</h3>
    <p>單價: <span class="price-text">{price:,.0f}</span></p>
    <p>成本: {cost:,.0f}</p>
    <hr>
    <p class="expense-text">成交手續({s_rate}%): -{tf_商:,.0f}</p>
    <p class="expense-text">蝦幣回饋(1.5%): -{cf_商:,.0f}</p>
    <p class="expense-text">金流/活動: -{(pf_商+ev):,.0f}</p>
    <hr>
    <p>實拿: <b>{payout_商:,.0f}</b></p>
    <p>預計純利:</p>
    <p class="profit-text">{profit_商:,.0f} 元</p>
    </div>""", unsafe_allow_html=True)

with col_直送:
    st.markdown(f"""<div class="result-box direct-box">
    <h3 style="color:#2980B9;">蝦皮直送</h3>
    <p>單價: <span class="price-text">{price:,.0f}</span></p>
    <p>成本: {cost:,.0f}</p>
    <hr>
    <p class="expense-text">前毛手續({f_margin}%): -{f_fee:,.0f}</p>
    <p class="expense-text">後毛手續({b_margin}%): -{b_fee:,.0f}</p>
    <p style="color:gray; font-size:0.8em;">(直送不計金流/活動費)</p>
    <hr>
    <p>實拿: <b>{payout_直:,.0f}</b></p>
    <p>預計純利:</p>
    <p class="profit-text">{profit_直:,.0f} 元</p>
    </div>""", unsafe_allow_html=True)
