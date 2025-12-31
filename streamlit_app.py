import streamlit as st
import pandas as pd

# 1. 頁面配置
st.set_page_config(page_title="馬尼專用蝦皮計算機", layout="wide", initial_sidebar_state="expanded")

# 2. CSS 全局美化
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif !important; }
    div[data-testid="stNumberInput"] label { font-size: 16px !important; font-weight: bold !important; color: #2C3E50 !important; }
    div[data-testid="stNumberInput"] input { font-size: 18px !important; font-weight: 900 !important; color: #E67E22 !important; }
    
    .result-card { 
        border: 1px solid #e6e9ef; padding: 20px; border-radius: 12px; 
        background-color: #ffffff; box-shadow: 0 4px 10px rgba(0,0,0,0.05); min-height: 550px;
    }
    .title-拍 { color: #333333; border-bottom: 2px solid #333333; padding-bottom: 5px; }
    .title-商 { color: #EE4D2D; border-bottom: 2px solid #EE4D2D; padding-bottom: 5px; }
    .title-直 { color: #2980B9; border-bottom: 2px solid #2980B9; padding-bottom: 5px; }
    
    .formula-text { color: #95a5a6; font-size: 0.8em; font-style: italic; margin-bottom: 2px; }
    .data-row { display: flex; justify-content: flex-start; align-items: baseline; gap: 10px; margin-top: 8px; }
    .val-15 { font-size: 1.5em; font-weight: 900; line-height: 1; }
    .payout-color { color: #2c3e50; }
    .profit-color { color: #27AE60; }
    
    .expense-tag { color: #E74C3C; font-size: 0.9em; margin: 2px 0; font-weight: bold; }
    .total-fee-tag { color: #C0392B; font-weight: bold; font-size: 1em; margin: 8px 0; padding: 5px; background: #FDEDEC; border-radius: 5px; }
    
    hr { border: 0; border-top: 1px solid #eee; margin: 8px 0; }
    </style>
    """, unsafe_allow_html=True)

# 3. 側邊欄
with st.sidebar:
    st.header("⚙️ 系統資訊")
    st.markdown('<div style="font-size:11px; color:#95a5a6;">馬尼專用蝦皮計算機<br>版本：V16.2 (穩定版)<br>© 2025 Mani Shopee Calc</div>', unsafe_allow_html=True)

# 4. 資料庫
FEE_DB = {
    "手機平板與周邊": {"手機": [5.5, 3.8], "平板電腦": [5.5, 4.0], "穿戴裝置": [5.5, 4.5]},
    "影音/相機": {"耳機/麥克風": [5.5, 6.5], "音響/喇叭": [6.0, 7.5]},
    "電腦與周邊": {"筆記型電腦": [5.0, 4.0], "桌上型電腦": [5.5, 5.0]}
}

# 5. 四等分布局
col_in, col_拍, col_商, col_直 = st.columns([1, 1, 1, 1])

with col_in:
    st.subheader("📋 馬尼輸入")
    p = st.number_input("成交單價 ($)", min_value=0, value=0, key="p")
    c = st.number_input("商品成本 ($)", min_value=0, value=0, key="c")
    pay_r = st.number_input("金流費率 (%)", value=2.5, step=0.1, key="pr")
    ev = st.number_input("活動日費用 ($)", value=60, key="ef")
    
    st.markdown("---")
    m_cat = st.selectbox("品類大類", list(FEE_DB.keys()))
    s_cat_list = list(FEE_DB[m_cat].items())
    s_cat_item = st.selectbox("細項分類", s_cat_list, format_func=lambda x: f"{x[0]} [拍:{x[1][0]}% / 商:{x[1][1]}%]")
    s_cat_name = s_cat_item[0]

    # --- 第二層：全局參數設定 ---
    with st.expander("⚙️ 全局參數與公式設定", expanded=True):
        st.caption("以下費率可手動調整，調整後會同步至所有計算結果")
        
        custom_p_rate = st.number_input(f"【{s_cat_name}】蝦拍費率 (%)", value=s_cat_item[1][0], step=0.1)
        custom_s_rate = st.number_input(f"【{s_cat_name}】蝦商費率 (%)", value=s_cat_item[1][1], step=0.1)
        
        st.markdown("---")
        cfg_拍_券 = st.number_input("蝦拍券回饋 (%)", value=3.0, step=0.1)
        cfg_商_券 = st.number_input("蝦商券回饋 (%)", value=1.5, step=0.1)
        cfg_直_後毛 = st.number_input("直送後毛費率 (%)", value=2.0, step=0.1)
        cfg_直_前毛_手機 = st.number_input("直送前毛(手機/平板) (%)", value=5.0, step=0.1)
        cfg_直_前毛_其他 = st.number_input("直送前毛(其他) (%)", value=12.0, step=0.1)

# 核心計算邏輯 (全局四捨五入)
shared_fee = round(p * (pay_r / 100)) + ev

tf1 = round(p * (custom_p_rate / 100))
cf1 = round(p * (cfg_拍_券 / 100))
total_fee1 = tf1 + cf1 + shared_fee
payout1 = p - total_fee1

tf2 = round(p * (custom_s_rate / 100))
cf2 = round(p * (cfg_商_券 / 100))
total_fee2 = tf2 + cf2 + shared_fee
payout2 = p - total_fee2

f_m_val = cfg_直_前毛_手機 if ("手機" in s_cat_name or "平板" in s_cat_name) else cfg_直_前毛_其他
tf3 = round(p * (f_m_val / 100))
tb3 = round(p * (cfg_直_後毛 / 100))
total_fee3 = tf3 + tb3
payout3 = p - total_fee3

# --- 畫面渲染 ---
with col_拍:
    st.markdown(f"""<div class="result-card"><h3 class="title-拍">蝦拍(一般)</h3>
        <p style="color:gray; font-size:0.9em;">品項: {s_cat_name}</p><hr>
        <p class="formula-text">公式: {p} × {custom_p_rate}%</p>
        <p class="expense-tag">成交手續費: -${tf1:,.0f}</p>
        <p class="formula-text">公式: {p} × {cfg_拍_券}%</p>
        <p class="expense-tag">券回饋費: -${cf1:,.0f}</p>
        <p class="formula-text">公式: ({p} × {pay_r}%) + {ev}</p>
        <p class="expense-tag">金流/活動費: -${shared_fee:,.0f}</p>
        <div class="total-fee-tag">手續費總計: -${total_fee1:,.0f}</div>
        <hr>
        <div class="data-row"><span class="label-text">實拿金額:</span><span class="val-15 payout-color">${payout1:,.0f}</span></div>
        <div class="data-row"><span class="label-text">預估毛利:</span><span class="val-15 profit-color">${payout1-c:,.0f}</span></div>
    </div>""", unsafe_allow_html=True)

with col_商:
    st.markdown(f"""<div class="result-card"><h3 class="title-商">蝦商(商城)</h3>
        <p style="color:gray; font-size:0.9em;">品項: {s_cat_name}</p><hr>
        <p class="formula-text">公式: {p} × {custom_s_rate}%</p>
        <p class="expense-tag">成交手續費: -${tf2:,.0f}</p>
        <p class="formula-text">公式: {p} × {cfg_商_券}%</p>
        <p class="expense-tag">券回饋費: -${cf2:,.0f}</p>
        <p class="formula-text">公式: ({p} × {pay_r}%) + {ev}</p>
        <p class="expense-tag">金流/活動費: -${shared_fee:,.0f}</p>
        <div class="total-fee-tag">手續費總計: -${total_fee2:,.0f}</div>
        <hr>
        <div class="data-row"><span class="label-text">實拿金額:</span><span class="val-15 payout-color">${payout2:,.0f}</span></div>
        <div class="data-row"><span class="label-text">預估毛利:</span><span class="val-15 profit-color">${payout2-c:,.0f}</span></div>
    </div>""", unsafe_allow_html=True)

with col_直:
    st.markdown(f"""<div class="result-card"><h3 class="title-直">蝦皮直送</h3>
        <p style="color:gray; font-size:0.9em;">類別: {"手機/平板" if f_m_val == cfg_直_前毛_手機 else "其他"}</p><hr>
        <p class="formula-text">公式: {p} × {
