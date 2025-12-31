import streamlit as st
import pandas as pd

# 1. 頁面配置
st.set_page_config(page_title="馬尼專用蝦皮計算機", layout="wide", initial_sidebar_state="expanded")

# 2. 強制隱藏系統異常文字與美化 CSS
st.markdown("""
    <style>
    /* 強制隱藏所有圖示異常文字 */
    span[data-testid="stSidebarCollapseIcon"], 
    [data-testid="stExpanderToggleIcon"] { display: none !important; }

    .small-font { font-size: 11px !important; color: #95a5a6; line-height: 1.2; }

    /* 核心卡片樣式 */
    .result-card { 
        border: 1px solid #e6e9ef; 
        padding: 20px; 
        border-radius: 12px; 
        background-color: #ffffff;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        min-height: 420px;
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

# 3. 側邊欄
with st.sidebar:
    st.header("⚙️ 系統資訊")
    st.markdown('<div class="small-font">馬尼專用蝦皮計算機<br>版本：V12.0 (補全費率版)<br>© 2025 Mani Shopee Calc</div>', unsafe_allow_html=True)

# 4. 資料庫
FEE_DB = {
    "手機平板與周邊": {"手機": [5.5, 3.8], "平板電腦": [5.5, 4.0], "穿戴裝置": [5.5, 4.5]},
    "影音/相機": {"耳機/麥克風": [5.5, 6.5], "音響/喇叭": [6.0, 7.5]},
    "電腦與周邊": {"筆記型電腦": [5.0, 4.0], "桌上型電腦": [5.5, 5.0]}
}

# 5. 四等分布局 (上排)
col_in, col_拍, col_商, col_直 = st.columns([1, 1, 1, 1])

# --- 欄位 1: 馬尼輸入區 ---
with col_in:
    st.subheader("📋 馬尼輸入")
    p = st.number_input("成交單價", min_value=0, value=1000)
    c = st.number_input("商品成本", min_value=0, value=500)
    
    st.markdown("**一般賣家設定**")
    pay_r = st.number_input("金流費率 (%)", value=2.5, step=0.1)
    ev = st.number_input("活動日費用", value=60)
    m_cat = st.selectbox("品類大類", list(FEE_DB.keys()))
    s_cat_item = st.selectbox("細項分類", list(FEE_DB[m_cat].items()), format_func=lambda x: f"{x[0]} [{x[1][0]}%/{x[1][1]}%]")
    
    st.markdown("---")
    direct_type = st.selectbox("直送類型", ["手機/平板 (5%+2%)", "耳機-品牌 (10%+2%)", "耳機-其他 (12%+2%)"])

# --- 核心計算邏輯 ---
p_rate, s_rate = s_cat_item[1]

# A. 蝦拍 (10倍券 3%)
tf1, pf1, cf1 = p*(p_rate/100), p*(pay_r/100), p*0.03
payout1 = p - tf1 - pf1 - cf1 - ev
profit1 = payout1 - c

# B. 蝦商 (5倍券 1.5%)
tf2, pf2, cf2 = p*(s_rate/100), p*(pay_r/100), p*0.015
payout2 = p - tf2 - pf2 - cf2 - ev
profit2 = payout2 - c

# C. 蝦皮直送 (前毛+後毛)
f_m = 5.0 if "手機" in direct_type else (10.0 if "品牌" in direct_type and "其他" not in direct_type else 12.0)
b_m = 2.0
tf3, tb3 = p*(f_m/100), p*(b_m/100)
payout3 = p - tf3 - tb3
profit3 = payout3 - c

# --- 畫面渲染 (三卡片區) ---
with col_拍:
    st.markdown(f"""<div class="result-card">
        <h3 class="title-拍">蝦拍 (一般)</h3>
        <p>單價: <span class="price-tag">${p:,.0f}</span> / 成本: ${c:,.0f}</p>
        <hr>
        <p class="expense-tag">成交手續({p_rate}%): -{tf1:,.0f}</p>
        <p class="expense-tag">10倍券回饋(3%): -{cf1:,.0f}</p>
        <p class="expense-tag">金流/活動: -{(pf1+ev):,.0f}</p>
        <hr>
        <p style="margin:0; font-size:0.9em;">實拿撥款: <b>${payout1:,.0f}</b></p>
        <p class="profit-tag">${profit1:,.0f}</p>
    </div>""", unsafe_allow_html=True)

with col_商:
    st.markdown(f"""<div class="result-card">
        <h3 class="title-商">蝦商 (商城)</h3>
        <p>單價: <span class="price-tag">${p:,.0f}</span> / 成本: ${c:,.0f}</p>
        <hr>
        <p class="expense-tag">成交手續({s_rate}%): -{tf2:,.0f}</p>
        <p class="expense-tag">5倍券回饋(1.5%): -{cf2:,.0f}</p>
        <p class="expense-tag">金流/活動: -{(pf2+ev):,.0f}</p>
        <hr>
        <p style="margin:0; font-size:0.9em;">實拿撥款: <b>${payout2:,.0f}</b></p>
        <p class="profit-tag">${profit2:,.0f}</p>
    </div>""", unsafe_allow_html=True)

with col_直:
    st.markdown(f"""<div class="result-card">
        <h3 class="title-直">蝦皮直送</h3>
        <p>單價: <span class="price-tag">${p:,.0f}</span> / 成本: ${c:,.0f}</p>
        <hr>
        <p class="expense-tag">前毛手續({f_m}%): -{tf3:,.0f}</p>
        <p class="expense-tag">後毛手續({b_m}%): -{tb3:,.0f}</p>
        <p style="color:#95a5a6; font-size:0.8em; margin-top:10px;">(不計金流/活動/券)</p>
        <hr>
        <p style="margin:0; font-size:0.9em;">實拿撥款: <b>${payout3:,.0f}</b></p>
        <p class="profit-tag">${profit3:,.0f}</p>
    </div>""", unsafe_allow_html=True)

# --- 6. 新增：橫向彙整區塊 ---
st.markdown("---")
st.subheader("📊 方案橫向比較表")
summary_data = {
    "方案名稱": ["蝦拍 (10倍券)", "蝦商 (5倍券)", "蝦皮直送"],
    "成交單價": [f"${p:,.0f}", f"${p:,.0f}", f"${p:,.0f}"],
    "總扣除費用": [f"${(p-payout1):,.0f}", f"${(p-payout2):,.0f}", f"${(p-payout3):,.0f}"],
    "實拿金額": [f"${payout1:,.0f}", f"${payout2:,.0f}", f"${payout3:,.0f}"],
    "預計純利": [f"${profit1:,.0f}", f"${profit2:,.0f}", f"${profit3:,.0f}"]
}
df_sum = pd.DataFrame(summary_data)
st.table(df_sum) # 使用表格呈現，方便橫向閱讀
