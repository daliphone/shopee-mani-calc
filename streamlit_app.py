import streamlit as st
import pandas as pd

# 1. 頁面配置
st.set_page_config(page_title="馬尼專用蝦皮計算機", layout="wide", initial_sidebar_state="expanded")

# 2. 強制隱藏系統異常文字與美化 CSS
st.markdown("""
    <style>
    /* 強制隱藏所有 Material Icon 異常顯示的英文字母 */
    span[data-testid="stSidebarCollapseIcon"], 
    .st-emotion-cache-1vt4yxc, 
    .st-emotion-cache-15zrgzn,
    [data-testid="stExpanderToggleIcon"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        font-size: 0 !important;
    }

    /* 修正側邊欄外觀 */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    .small-font {
        font-size: 11px !important;
        color: #95a5a6;
        line-height: 1.2;
    }

    /* 核心卡片樣式優化 */
    .result-card { 
        border: 1px solid #e6e9ef; 
        padding: 20px; 
        border-radius: 12px; 
        background-color: #ffffff;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        min-height: 480px;
    }
    
    .title-拍 { color: #333333; border-bottom: 2px solid #333333; padding-bottom: 5px; margin-bottom: 12px; }
    .title-商 { color: #EE4D2D; border-bottom: 2px solid #EE4D2D; padding-bottom: 5px; margin-bottom: 12px; }
    .title-直 { color: #2980B9; border-bottom: 2px solid #2980B9; padding-bottom: 5px; margin-bottom: 12px; }
    
    .price-tag { color: #3498DB; font-weight: bold; }
    .expense-tag { color: #E74C3C; font-size: 0.9em; margin: 3px 0; }
    .profit-tag { color: #27AE60; font-size: 1.8em; font-weight: 900; }
    
    hr { border: 0; border-top: 1px solid #eee; margin: 12px 0; }
    </style>
    """, unsafe_allow_html=True)

# 3. 側邊欄：極簡系統資訊
with st.sidebar:
    st.header("⚙️ 系統資訊")
    st.markdown('<div class="small-font">馬尼專用蝦皮計算機<br>版本：V11.2 (Stable)<br>© 2025 Mani Shopee Calc</div>', unsafe_allow_html=True)

# 4. 資料庫 (PDF 精確費率)
FEE_DB = {
    "手機平板與周邊": {"手機": [5.5, 3.8], "平板電腦": [5.5, 4.0], "穿戴裝置": [5.5, 4.5]},
    "影音/相機": {"耳機/麥克風": [5.5, 6.5], "音響/喇叭": [6.0, 7.5]},
    "電腦與周邊": {"筆記型電腦": [5.0, 4.0], "桌上型電腦": [5.5, 5.0]}
}

# 5. 四等分布局
col_in, col_拍, col_商, col_直 = st.columns([1, 1, 1, 1])

# --- 欄位 1: 馬尼輸入區 ---
with col_in:
    st.subheader("📋 馬尼輸入")
    p = st.number_input("成交單價", min_value=0, value=1000, step=100)
    c = st.number_input("商品成本", min_value=0, value=500, step=100)
    
    # 使用 container 替代 expander 避免圖示文字問題
    with st.container():
        st.markdown("**一般賣家設定**")
        pay_r = st.number_input("金流費率 (%)", value=2.5, step=0.1)
        ev = st.number_input("活動日費用", value=60)
        m_cat = st.selectbox("品類大類", list(FEE_DB.keys()))
        s_cat_item = st.selectbox("細項分類", list(FEE_DB[m_cat].items()), format_func=lambda x: f"{x[0]} [{x[1][0]}%/{x[1][1]}%]")
    
    st.markdown("---")
    direct_type = st.selectbox("直送類型 (僅影響直送)", ["手機/平板 (5%+2%)", "耳機-品牌 (10%+2%)", "耳機-其他 (12%+2%)"])

# --- 核心計算邏輯 ---
p_rate, s_rate = s_cat_item[1]
# 蝦拍
tf1, pf1, cf1 = p*(p_rate/100), p*(pay_r/100), p*0.025
payout1 = p - tf1 - pf1 - cf1 - ev
profit1 = payout1 - c
# 蝦商
tf2, pf2, cf2 = p*(s_rate/100), p*(pay_r/100), p*0.015
payout2 = p - tf2 - pf2 - cf2 - ev
profit2 = payout2 - c
# 蝦皮直送 (獨立邏輯)
f_m = 5.0 if "手機" in direct_type else (10.0 if "品牌" in direct_type and "其他" not in direct_type else 12.0)
b_m = 2.0
tf3, tb3 = p*(f_m/100), p*(b_m/100)
payout3 = p - tf3 - tb3
profit3 = payout3 - c

# --- 畫面渲染 (維持四欄對齊) ---
with col_拍:
    st.markdown(f"""<div class="result-card">
        <h3 class="title-拍">蝦拍 (一般)</h3>
        <p>單價: <span class="price-tag">${p:,.0f}</span> / 成本: ${c:,.0f}</p>
        <hr>
        <p class="expense-text">成交手續({p_rate}%): -{tf1:,.0f}</p>
        <p class="expense-text">蝦幣回饋(2.5%): -{cf1:,.0f}</p>
        <p class="expense-text">金流/活動: -{(pf1+ev):,.0f}</p>
        <hr>
        <p style="margin:0; font-size:0.9em;">實拿撥款: <b>${payout1:,.0f}</b></p>
        <p style="margin-top:5px; font-size:0.85em;">預估純利:</p>
        <p class="profit-tag">${profit1:,.0f}</p>
    </div>""", unsafe_allow_html=True)

with col_商:
    st.markdown(f"""<div class="result-card">
        <h3 class="title-商">蝦商 (商城)</h3>
        <p>單價: <span class="price-tag">${p:,.0f}</span> / 成本: ${c:,.0f}</p>
        <hr>
        <p class="expense-tag">成交手續({s_rate}%): -{tf2:,.0f}</p>
        <p class="expense-tag">蝦幣回饋(1.5%): -{cf2:,.0f}</p>
        <p class="expense-tag">金流/活動: -{(pf2+ev):,.0f}</p>
        <hr>
        <p style="margin:0; font-size:0.9em;">實拿撥款: <b>${payout2:,.0f}</b></p>
        <p style="margin-top:5px; font-size:0.85em;">預估純利:</p>
        <p class="profit-tag">${profit2:,.0f}</p>
    </div>""", unsafe_allow_html=True)

with col_直:
    st.markdown(f"""<div class="result-card">
        <h3 class="title-直">蝦皮直送</h3>
        <p>單價: <span class="price-tag">${p:,.0f}</span> / 成本: ${c:,.0f}</p>
        <hr>
        <p class="expense-tag">前毛手續({f_m}%): -{tf3:,.0f}</p>
        <p class="expense-tag">後毛手續({b_m}%): -{tb3:,.0f}</p>
        <p style="color:#95a5a6; font-size:0.8em; margin-top:10px;">(直送不計金流/活動費)</p>
        <hr>
        <p style="margin:0; font-size:0.9em;">實拿撥款: <b>${payout3:,.0f}</b></p>
        <p style="margin-top:5px; font-size:0.85em;">預估純利:</p>
        <p class="profit-tag">${profit3:,.0f}</p>
    </div>""", unsafe_allow_html=True)
