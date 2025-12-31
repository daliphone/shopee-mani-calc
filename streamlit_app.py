import streamlit as st
import pandas as pd

# 1. 頁面配置
st.set_page_config(page_title="馬尼專用蝦皮計算機", layout="wide", initial_sidebar_state="expanded")

# 2. CSS 樣式美化
st.markdown("""
    <style>
    /* 隱藏異常文字 */
    span[data-testid="stSidebarCollapseIcon"], [data-testid="stExpanderToggleIcon"] { display: none !important; }
    
    /* 馬尼輸入區字級加大與粗體 */
    div[data-testid="stNumberInput"] label { font-size: 18px !important; font-weight: bold !important; }
    div[data-testid="stNumberInput"] input { font-size: 20px !important; font-weight: bold !important; color: #34495e !important; }
    
    /* 側邊欄系統資訊 */
    .small-font { font-size: 11px !important; color: #95a5a6; }

    /* 結果卡片樣式 */
    .result-card { 
        border: 1px solid #e6e9ef; padding: 22px; border-radius: 12px; 
        background-color: #ffffff; box-shadow: 0 4px 10px rgba(0,0,0,0.05); min-height: 420px;
    }
    .title-拍 { color: #333333; border-bottom: 2px solid #333333; padding-bottom: 5px; margin-bottom: 12px; }
    .title-商 { color: #EE4D2D; border-bottom: 2px solid #EE4D2D; padding-bottom: 5px; margin-bottom: 12px; }
    .title-直 { color: #2980B9; border-bottom: 2px solid #2980B9; padding-bottom: 5px; margin-bottom: 12px; }
    
    /* 實拿與毛利加大並粗體 */
    .payout-text { font-size: 1.2em; font-weight: 800; color: #2c3e50; }
    .profit-tag { color: #27AE60; font-size: 2.1em; font-weight: 900; }
    .expense-tag { color: #E74C3C; font-size: 0.9em; margin: 3px 0; }
    
    hr { border: 0; border-top: 1px solid #eee; margin: 12px 0; }
    </style>
    """, unsafe_allow_html=True)

# 3. 側邊欄
with st.sidebar:
    st.header("⚙️ 系統資訊")
    st.markdown('<div class="small-font">馬尼專用蝦皮計算機<br>版本：V14.0 (專業美化版)<br>© 2025 Mani Shopee Calc</div>', unsafe_allow_html=True)

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
    # 利用 Streamlit 預設行為與標籤順序，Enter 會依序跳轉
    p = st.number_input("成交單價 ($)", min_value=0, value=1000)
    c = st.number_input("商品成本 ($)", min_value=0, value=500)
    pay_r = st.number_input("金流費率 (%)", value=2.5, step=0.1)
    ev = st.number_input("活動日費用 ($)", value=60)
    
    st.markdown("---")
    m_cat = st.selectbox("品類大類", list(FEE_DB.keys()))
    s_cat_name = st.selectbox("細項分類", list(FEE_DB[m_cat].keys()))
    direct_type = st.selectbox("直送類型", ["手機/平板 (5%+2%)", "耳機-品牌 (10%+2%)", "耳機-其他 (12%+2%)"])

# --- 核心計算邏輯 ---
p_rate, s_rate = FEE_DB[m_cat][s_cat_name]

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
tf3, tb3 = p*(f_m/100), p*0.02
payout3 = p - tf3 - tb3
profit3 = payout3 - c

# --- 畫面渲染 (卡片區) ---
with col_拍:
    st.markdown(f"""<div class="result-card">
        <h3 class="title-拍">蝦拍(10倍券3%)</h3>
        <p>品項: {s_cat_name}</p>
        <hr>
        <p class="expense-text">成交手續({p_rate}%): -${tf1:,.0f}</p>
        <p class="expense-text">10倍券回饋(3%): -${cf1:,.0f}</p>
        <p class="expense-text">金流/活動: -${(pf1+ev):,.0f}</p>
        <hr>
        <p class="payout-text">實拿金額: <b>${payout1:,.0f}</b></p>
        <p style="margin-top:10px; font-weight:bold;">預估毛利:</p>
        <p class="profit-tag">${profit1:,.0f}</p>
    </div>""", unsafe_allow_html=True)

with col_商:
    st.markdown(f"""<div class="result-card">
        <h3 class="title-商">蝦商(5倍券1.5%)</h3>
        <p>品項: {s_cat_name}</p>
        <hr>
        <p class="expense-text">成交手續({s_rate}%): -${tf2:,.0f}</p>
        <p class="expense-text">5倍券回饋(1.5%): -${cf2:,.0f}</p>
        <p class="expense-text">金流/活動: -${(pf2+ev):,.0f}</p>
        <hr>
        <p class="payout-text">實拿金額: <b>${payout2:,.0f}</b></p>
        <p style="margin-top:10px; font-weight:bold;">預估毛利:</p>
        <p class="profit-tag">${profit2:,.0f}</p>
    </div>""", unsafe_allow_html=True)

with col_直:
    st.markdown(f"""<div class="result-card">
        <h3 class="title-直">蝦皮直送</h3>
        <p>直送類型: {direct_type.split(' (')[0]}</p>
        <hr>
        <p class="expense-text">前毛手續({f_m}%): -${tf3:,.0f}</p>
        <p class="expense-tag">後毛手續(2%): -${tb3:,.0f}</p>
        <p style="color:#95a5a6; font-size:0.85em; margin-top:5px;">(直送不計金流/活動/券)</p>
        <hr>
        <p class="payout-text">實拿金額: <b>${payout3:,.0f}</b></p>
        <p style="margin-top:10px; font-weight:bold;">預估毛利:</p>
        <p class="profit-tag">${profit3:,.0f}</p>
    </div>""", unsafe_allow_html=True)

# --- 6. 橫向全品項對照表 (美化版) ---
st.markdown("---")
st.subheader(f"📊 各細項分類毛利分析表 (單價:${p:,.0f} / 成本:${c:,.0f})")

rows = []
for cat, subs in FEE_DB.items():
    for sub_name, rates in subs.items():
        pr, sr = rates
        # 計算
        p_payout = p - (p*(pr/100)) - (p*(pay_r/100)) - (p*0.03) - ev
        s_payout = p - (p*(sr/100)) - (p*(pay_r/100)) - (p*0.015) - ev
        dfm = 5.0 if "手機" in sub_name or "平板" in sub_name else 12.0
        d_payout = p - (p*(dfm/100)) - (p*0.02)
        
        rows.append({
            "分類細項": sub_name,
            "蝦拍利潤 (10倍券)": int(p_payout - c),
            "蝦商利潤 (5倍券)": int(s_payout - c),
            "直送利潤 (估計)": int(d_payout - c)
        })

df_compare = pd.DataFrame(rows)

# 使用 Streamlit Dataframe 進行美化顯示，並高亮最大值
st.dataframe(
    df_compare.style.highlight_max(axis=1, color='#d4edda', subset=["蝦拍利潤 (10倍券)", "蝦商利潤 (5倍券)", "直送利潤 (估計)"])
    .format({"蝦拍利潤 (10倍券)": "${:,.0f}", "蝦商利潤 (5倍券)": "${:,.0f}", "直送利潤 (估計)": "${:,.0f}"}),
    use_container_width=True
)
