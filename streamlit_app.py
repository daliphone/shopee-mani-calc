import streamlit as st
import pandas as pd

# 1. 頁面標題與分頁名稱
st.set_page_config(page_title="馬尼專用蝦皮計算機", layout="wide")

# 2. 精確資料庫 (包含一般費率與直送前毛費率)
FEE_DB = {
    "手機平板與周邊": {
        "手機": {"p_s": [5.5, 3.8], "direct_f": 5.0}, 
        "平板電腦": {"p_s": [5.5, 4.0], "direct_f": 5.0}, 
        "穿戴裝置": {"p_s": [5.5, 4.5], "direct_f": 5.0}
    },
    "影音/相機": {
        "耳機(手機品牌)": {"p_s": [5.5, 6.5], "direct_f": 10.0}, 
        "耳機(其他品牌)": {"p_s": [5.5, 6.5], "direct_f": 12.0}, 
        "音響/喇叭/麥克風": {"p_s": [6.0, 7.5], "direct_f": 12.0}
    }
}

if 'c_fees' not in st.session_state: 
    st.session_state.c_fees = []

# 3. 全域 CSS 樣式
st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 16px; font-family: 'Microsoft JhengHei'; }
    .result-box { 
        border: 2px solid #EE4D2D; 
        padding: 20px; 
        border-radius: 15px; 
        background-color: #fdfdfd;
        margin-bottom: 20px;
        box-shadow: 4px 4px 15px rgba(0,0,0,0.1);
    }
    .direct-box { border-color: #2980B9; } /* 直送區塊顏色區分 */
    .price-text { color: #3498DB; font-weight: bold; }
    .expense-text { color: #E74C3C; margin: 3px 0; font-size: 0.9em; }
    .profit-text { color: #27AE60; font-size: 1.5em; font-weight: bold; }
    hr { border: 0; border-top: 1px solid #eee; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# 4. 三欄式佈局
col_in, col_拍商, col_直送 = st.columns([1, 1, 1])

# --- 欄位 1: 馬尼試算輸入 ---
with col_in:
    st.header("馬尼試算輸入")
    price = st.number_input("成交單價", min_value=0, value=1000, step=100)
    cost = st.number_input("商品成本", min_value=0, value=500, step=100)
    pay_r = st.number_input("金流費率(%)", value=2.5, step=0.1)
    ev = st.number_input("活動日費用", value=60)
    
    st.divider()
    m_cat = st.selectbox("商品大類", list(FEE_DB.keys()))
    s_cat = st.selectbox("細項分類", list(FEE_DB[m_cat].keys()))
    
    # 讀取對應費率
    rates = FEE_DB[m_cat][s_cat]
    p_rate, s_rate = rates["p_s"]
    front_margin = rates["direct_f"]
    back_margin = 2.0  # 暫定後毛均為 2%
    
    st.divider()
    st.caption("其他自訂費率(%)")
    n_n = st.text_input("費用名稱")
    n_r = st.number_input("費率", value=0.0)
    if st.button("新增自訂"):
        if n_n: st.session_state.c_fees.append({"name": n_n, "rate": n_r/100})
        st.rerun()
    
    current_cust_rate = sum([f['rate'] for f in st.session_state.c_fees])
    if st.button("🗑️ 清空自訂"):
        st.session_state.c_fees = []
        st.rerun()

# 5. 渲染函數
def draw_card(title, t_rate, coin_r, color, is_direct=False):
    # 計算邏輯
    pf = price * (pay_r / 100)
    cf = price * coin_r
    cst_f = price * current_cust_rate
    
    if is_direct:
        # 蝦皮直送專屬邏輯
        front_f = price * (front_margin / 100)
        back_f = price * (back_margin / 100)
        total = front_f + back_f + pf + ev + cst_f
        fees_html = f"""
            <p class="expense-text">前毛手續({front_margin}%): -{front_f:,.0f}</p>
            <p class="expense-text">後毛手續({back_margin}%): -{back_f:,.0f}</p>
        """
    else:
        # 一般蝦拍/蝦商邏輯
        tf = price * (t_rate / 100)
        total = tf + pf + cf + ev + cst_f
        fees_html = f"""
            <p class="expense-text">成交手續({t_rate}%): -{tf:,.2f}</p>
            <p class="expense-text">蝦幣回饋({coin_r*100}%): -{cf:,.2f}</p>
        """

    payout = price - total
    profit = payout - cost
    box_class = "result-box direct-box" if is_direct else "result-box"
    
    st.markdown(f"""
    <div class="{box_class}">
        <h3 style="color:{color}; margin:0;">{title}</h3>
        <hr>
        <p>單價: <span class="price-text">{price:,.0f}</span> / 成本: {cost:,.0f}</p>
        {fees_html}
        <p class="expense-text">金流/活動/自訂: -{(pf+ev+cst_f):,.0f}</p>
        <hr>
        <p style="font-size:0.9em; margin:0;">實拿: <b>{payout:,.0f}</b></p>
        <p style="margin:0;">預計純利:</p>
        <p class="profit-text">{profit:,.0f} 元</p>
    </div>
    """, unsafe_allow_html=True)

# --- 欄位 2: 蝦拍與蝦商 ---
with col_拍商:
    draw_card("蝦拍 (一般)", p_rate, 0.025, "#333333")
    draw_card("蝦商 (商城)", s_rate, 0.015, "#EE4D2D")

# --- 欄位 3: 蝦皮直送 ---
with col_直送:
    draw_card("蝦皮直送 (專屬)", 0, 0, "#2980B9", is_direct=True)
