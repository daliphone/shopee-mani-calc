import streamlit as st
import pandas as pd

# 1. 頁面配置
st.set_page_config(page_title="馬尼專用蝦皮計算機", layout="wide", initial_sidebar_state="expanded")

# 2. 側邊欄：縮小系統資訊字體
with st.sidebar:
    st.markdown("""
        <style>
        .small-font {
            font-size: 11px !important;
            color: #7f8c8d;
            line-height: 1.2;
        }
        </style>
        <div class="small-font">
            <b>🛠️ 系統資訊</b><br>
            版本號：V11.0 Final<br>
            <hr style="margin: 8px 0;">
            © 2025 馬尼蝦皮計算機<br>
            All Rights Reserved.
        </div>
    """, unsafe_allow_html=True)

# 3. PDF 精確資料庫
FEE_DB = {
    "手機平板與周邊": {"手機": [5.5, 3.8], "平板電腦": [5.5, 4.0], "穿戴裝置": [5.5, 4.5]},
    "影音/相機": {"耳機/麥克風": [5.5, 6.5], "音響/喇叭": [6.0, 7.5], "相機": [5.0, 5.0]},
    "電腦與周邊": {"筆記型電腦": [5.0, 4.0], "桌上型電腦": [5.5, 5.0]}
}

# 4. CSS 美化樣式 (維持四欄位佈局不動)
st.markdown("""
    <style>
    html, body, [class*="st-"] { font-family: 'Microsoft JhengHei', sans-serif; }
    
    .result-card { 
        border: 1px solid #e6e9ef; 
        padding: 20px; 
        border-radius: 15px; 
        background-color: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        min-height: 500px;
        transition: transform 0.2s;
    }
    
    .title-拍 { color: #333333; border-bottom: 3px solid #333333; padding-bottom: 5px; }
    .title-商 { color: #EE4D2D; border-bottom: 3px solid #EE4D2D; padding-bottom: 5px; }
    .title-直 { color: #2980B9; border-bottom: 3px solid #2980B9; padding-bottom: 5px; }
    
    .price-tag { color: #3498DB; font-weight: 700; }
    .expense-tag { color: #E74C3C; font-size: 0.95em; margin: 3px 0; }
    .profit-tag { color: #27AE60; font-size: 1.8em; font-weight: 900; }
    
    hr { border: 0; border-top: 1px solid #eee; margin: 15px 0; }
    </style>
    """, unsafe_allow_html=True)

# 5. 四等分布局 (維持比例 1:1:1:1)
col_in, col_拍, col_商, col_直 = st.columns([1, 1, 1, 1])

# --- 欄位 1: 馬尼輸入區 ---
with col_in:
    st.header("📋 馬尼輸入")
    p = st.number_input("成交單價 (TWD)", min_value=0, value=1000, step=100)
    c = st.number_input("商品成本 (TWD)", min_value=0, value=500, step=100)
    
    st.markdown("---")
    with st.expander("一般賣家進階設定", expanded=True):
        pay_r = st.number_input("金流費率 (%)", value=2.5, step=0.1)
        ev = st.number_input("活動日費用 (元)", value=60)
        m_cat = st.selectbox("品類大類", list(FEE_DB.keys()))
        s_cat = st.selectbox("細項分類", list(FEE_DB[m_cat].items()), format_func=lambda x: f"{x[0]} [{x[1][0]}%/{x[1][1]}%]")
    
    st.markdown("---")
    direct_type = st.selectbox("直送類型 (僅影響直送)", 
                               ["手機/平板 (5%+2%)", "耳機-手機品牌 (10%+2%)", "耳機-其他品牌 (12%+2%)"])

# --- 核心計算邏輯 ---
p_rate, s_rate = s_cat[1]

# 1. 蝦拍
tf1, pf1, cf1 = p*(p_rate/100), p*(pay_r/100), p*0.025
payout1 = p - tf1 - pf1 - cf1 - ev
profit1 = payout1 - c

# 2. 蝦商
tf2, pf2, cf2 = p*(s_rate/100), p*(pay_r/100), p*0.015
payout2 = p - tf2 - pf2 - cf2 - ev
profit2 = payout2 - c

# 3. 蝦皮直送 (獨立邏輯)
f_m = 5.0 if "手機" in direct_type else (10.0 if "手機品牌" in direct_type else 12.0)
b_m = 2.0
tf3, tb3 = p*(f_m/100), p*(b_m/100)
payout3 = p - tf3 - tb3
profit3 = payout3 - c

# --- 畫面渲染 (維持四欄對齊) ---
with col_拍:
    st.markdown(f"""<div class="result-card">
        <h3 class="title-拍">蝦拍 (一般)</h3>
        <p>單價: <span class="price-tag">${p:,.0f}</span></p>
        <p>成本: ${c:,.0f}</p>
        <hr>
        <p class="expense-tag">成交手續({p_rate}%): -{tf1:,.0f}</p>
        <p class="expense-tag">蝦幣回饋(2.5%): -{cf1:,.0f}</p>
        <p class="expense-tag">金流/活動費: -{(pf1+ev):,.0f}</p>
        <hr>
        <p style="margin:0;">實拿撥款: <b>${payout1:,.0f}</b></p>
        <p style="margin-top:10px; font-size:0.9em;">預估純利:</p>
        <p class="profit-tag">${profit1:,.0f}</p>
    </div>""", unsafe_allow_html=True)

with col_商:
    st.markdown(f"""<div class="result-card">
        <h3 class="title-商">蝦商 (商城)</h3>
        <p>單價: <span class="price-text">${p:,.0f}</span></p>
        <p>成本: ${c:,.0f}</p>
        <hr>
        <p class="expense-tag">成交手續({s_rate}%): -{tf2:,.0f}</p>
        <p class="expense-tag">蝦幣回饋(1.5%): -{cf2:,.0f}</p>
        <p class="expense-tag">金流/活動費: -{(pf2+ev):,.0f}</p>
        <hr>
        <p style="margin:0;">實拿撥款: <b>${payout2:,.0f}</b></p>
        <p style="margin-top:10px; font-size:0.9em;">預估純利:</p>
        <p class="profit-tag">${profit2:,.0f}</p>
    </div>""", unsafe_allow_html=True)

with col_直:
    st.markdown(f"""<div class="result-card">
        <h3 class="title-直">蝦皮直送</h3>
        <p>單價: <span class="price-text">${p:,.0f}</span></p>
        <p>成本: ${c:,.0f}</p>
        <hr>
        <p class="expense-tag">前毛手續({f_m}%): -{tf3:,.0f}</p>
        <p class="expense-tag">後毛手續({b_m}%): -{tb3:,.0f}</p>
        <p style="color:#95a5a6; font-size:0.85em; margin-top:10px;">(直送不計金流/活動費)</p>
        <hr>
        <p style="margin:0;">實拿撥款: <b>${payout3:,.0f}</b></p>
        <p style="margin-top:10px; font-size:0.9em;">預估純利:</p>
        <p class="profit-tag">${profit3:,.0f}</p>
    </div>""", unsafe_allow_html=True)
