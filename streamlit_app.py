import streamlit as st
import pandas as pd

# 1. 頁面配置
st.set_page_config(page_title="馬尼專用蝦皮計算機", layout="wide", initial_sidebar_state="expanded")

# 2. CSS 樣式
st.markdown("""
    <style>
    span[data-testid="stSidebarCollapseIcon"], [data-testid="stExpanderToggleIcon"] { display: none !important; }
    .small-font { font-size: 11px !important; color: #95a5a6; line-height: 1.2; }
    .result-card { 
        border: 1px solid #e6e9ef; padding: 20px; border-radius: 12px; 
        background-color: #ffffff; box-shadow: 0 4px 10px rgba(0,0,0,0.05); min-height: 400px;
    }
    .title-拍 { color: #333333; border-bottom: 2px solid #333333; padding-bottom: 5px; margin-bottom: 12px; }
    .title-商 { color: #EE4D2D; border-bottom: 2px solid #EE4D2D; padding-bottom: 5px; margin-bottom: 12px; }
    .title-直 { color: #2980B9; border-bottom: 2px solid #2980B9; padding-bottom: 5px; margin-bottom: 12px; }
    .price-tag { color: #3498DB; font-weight: bold; }
    .expense-tag { color: #E74C3C; font-size: 0.85em; margin: 2px 0; }
    .profit-tag { color: #27AE60; font-size: 1.8em; font-weight: 900; }
    hr { border: 0; border-top: 1px solid #eee; margin: 10px 0; }
    /* 表格字體縮小以容納更多資訊 */
    .stTable { font-size: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 側邊欄
with st.sidebar:
    st.header("⚙️ 系統資訊")
    st.markdown('<div class="small-font">馬尼專用蝦皮計算機<br>版本：V13.0 (全分類對照版)<br>© 2025 Mani Shopee Calc</div>', unsafe_allow_html=True)

# 4. 資料庫 (PDF 精確費率)
FEE_DB = {
    "手機平板與周邊": {
        "手機": [5.5, 3.8], "平板電腦": [5.5, 4.0], "穿戴裝置": [5.5, 4.5]
    },
    "影音/相機": {
        "耳機/麥克風": [5.5, 6.5], "音響/喇叭": [6.0, 7.5]
    },
    "電腦與周邊": {
        "筆記型電腦": [5.0, 4.0], "桌上型電腦": [5.5, 5.0]
    }
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
    s_cat_name = st.selectbox("細項分類", list(FEE_DB[m_cat].keys()))
    
    st.markdown("---")
    direct_type = st.selectbox("直送類型 (僅影響卡片顯示)", ["手機/平板 (5%+2%)", "耳機-品牌 (10%+2%)", "耳機-其他 (12%+2%)"])

# --- 核心計算邏輯 (針對目前選中項) ---
p_rate, s_rate = FEE_DB[m_cat][s_cat_name]
# 蝦拍
tf1, pf1, cf1 = p*(p_rate/100), p*(pay_r/100), p*0.03
payout1 = p - tf1 - pf1 - cf1 - ev
# 蝦商
tf2, pf2, cf2 = p*(s_rate/100), p*(pay_r/100), p*0.015
payout2 = p - tf2 - pf2 - cf2 - ev
# 蝦皮直送
f_m = 5.0 if "手機" in direct_type else (10.0 if "品牌" in direct_type and "其他" not in direct_type else 12.0)
payout3 = p - (p*(f_m/100)) - (p*0.02)

# --- 畫面渲染 (卡片區) ---
with col_拍:
    st.markdown(f"""<div class="result-card">
        <h3 class="title-拍">蝦拍(10倍券3%)</h3>
        <p>品項: {s_cat_name}</p>
        <hr>
        <p class="expense-tag">成交手續({p_rate}%): -{tf1:,.0f}</p>
        <p class="expense-tag">10倍券(3%): -{cf1:,.0f}</p>
        <p class="expense-tag">金流/活動: -{(pf1+ev):,.0f}</p>
        <hr>
        <p style="margin:0; font-size:0.9em;">實拿: <b>${payout1:,.0f}</b></p>
        <p class="profit-tag">${(payout1-c):,.0f}</p>
    </div>""", unsafe_allow_html=True)

with col_商:
    st.markdown(f"""<div class="result-card">
        <h3 class="title-商">蝦商(5倍券1.5%)</h3>
        <p>品項: {s_cat_name}</p>
        <hr>
        <p class="expense-tag">成交手續({s_rate}%): -{tf2:,.0f}</p>
        <p class="expense-tag">5倍券(1.5%): -{cf2:,.0f}</p>
        <p class="expense-tag">金流/活動: -{(pf2+ev):,.0f}</p>
        <hr>
        <p style="margin:0; font-size:0.9em;">實拿: <b>${payout2:,.0f}</b></p>
        <p class="profit-tag">${(payout2-c):,.0f}</p>
    </div>""", unsafe_allow_html=True)

with col_直:
    st.markdown(f"""<div class="result-card">
        <h3 class="title-直">蝦皮直送</h3>
        <p>直送類型: {direct_type.split(' (')[0]}</p>
        <hr>
        <p class="expense-tag">前毛手續({f_m}%): -{p*(f_m/100):,.0f}</p>
        <p class="expense-tag">後毛手續(2%): -{p*0.02:,.0f}</p>
        <p style="color:gray; font-size:0.8em;">(不計金流/活動/券)</p>
        <hr>
        <p style="margin:0; font-size:0.9em;">實拿: <b>${payout3:,.0f}</b></p>
        <p class="profit-tag">${(payout3-c):,.0f}</p>
    </div>""", unsafe_allow_html=True)

# --- 6. 橫向全品項對照表 ---
st.markdown("---")
st.subheader(f"📊 各細項分類個別利潤比較表 (單價:${p:,.0f} / 成本:${c:,.0f})")

rows = []
for cat, subs in FEE_DB.items():
    for sub_name, rates in subs.items():
        pr, sr = rates
        # 蝦拍計算
        p_payout = p - (p*(pr/100)) - (p*(pay_r/100)) - (p*0.03) - ev
        # 蝦商計算
        s_payout = p - (p*(sr/100)) - (p*(pay_r/100)) - (p*0.015) - ev
        # 直送計算 (判斷類別套用前毛)
        dfm = 5.0 if "手機" in sub_name or "平板" in sub_name else 12.0 # 預設非手機類12%
        d_payout = p - (p*(dfm/100)) - (p*0.02)
        
        rows.append({
            "分類": sub_name,
            "蝦拍利潤(10倍券)": f"${(p_payout-c):,.0f}",
            "蝦商利潤(5倍券)": f"${(s_payout-c):,.0f}",
            "直送利潤(估計)": f"${(d_payout-c):,.0f}",
            "最優方案": "蝦拍" if p_payout > s_payout and p_payout > d_payout else ("蝦商" if s_payout > d_payout else "直送")
        })

df_compare = pd.DataFrame(rows)
st.table(df_compare)
