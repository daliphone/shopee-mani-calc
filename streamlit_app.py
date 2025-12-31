import streamlit as st
import pandas as pd

# 1. 頁面配置
st.set_page_config(page_title="馬尼專用蝦皮計算機", layout="wide", initial_sidebar_state="expanded")

# 2. CSS 全局美化
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif !important; }
    
    /* 馬尼輸入區字級與數字強化 */
    div[data-testid="stNumberInput"] label { font-size: 18px !important; font-weight: bold !important; color: #2C3E50 !important; }
    div[data-testid="stNumberInput"] input { font-size: 22px !important; font-weight: 900 !important; color: #E67E22 !important; }
    
    /* 結果卡片樣式 */
    .result-card { 
        border: 1px solid #e6e9ef; padding: 25px; border-radius: 12px; 
        background-color: #ffffff; box-shadow: 0 4px 10px rgba(0,0,0,0.05); min-height: 480px;
    }
    .title-拍 { color: #333333; border-bottom: 2px solid #333333; padding-bottom: 5px; margin-bottom: 15px; }
    .title-商 { color: #EE4D2D; border-bottom: 2px solid #EE4D2D; padding-bottom: 5px; margin-bottom: 15px; }
    .title-直 { color: #2980B9; border-bottom: 2px solid #2980B9; padding-bottom: 5px; margin-bottom: 15px; }
    
    /* 卡片數值統一為 2.5em 並加粗 */
    .payout-val { font-size: 2.5em; font-weight: 900; color: #2c3e50; margin: 10px 0; line-height: 1.2; }
    .profit-val-card { font-size: 2.5em; font-weight: 900; color: #27AE60; line-height: 1.2; }
    .label-text { font-size: 1.2em; font-weight: bold; color: #555; }
    
    /* 分析表標題 */
    .table-header-custom {
        color: #2980B9;
        font-weight: bold;
        font-size: 20px;
        background-color: #F8F9F9;
        padding: 12px;
        border-radius: 8px;
        border-left: 5px solid #2980B9;
        margin-bottom: 15px;
    }

    /* 表格字體加粗 */
    .stDataFrame [data-testid="styled-table-cell"] {
        font-weight: bold !important;
        font-size: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 側邊欄
with st.sidebar:
    st.header("⚙️ 系統資訊")
    st.markdown('<div style="font-size:11px; color:#95a5a6;">馬尼專用蝦皮計算機<br>版本：V15.3 (欄位標記版)<br>© 2025 Mani Shopee Calc</div>', unsafe_allow_html=True)

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
    p = st.number_input("成交單價 ($)", min_value=0, value=2850, key="p")
    c = st.number_input("商品成本 ($)", min_value=0, value=500, key="c")
    pay_r = st.number_input("金流費率 (%)", value=2.5, step=0.1, key="pr")
    ev = st.number_input("活動日費用 ($)", value=60, key="ef")
    
    st.markdown("---")
    m_cat = st.selectbox("品類大類", list(FEE_DB.keys()))
    s_cat_name = st.selectbox("細項分類", list(FEE_DB[m_cat].keys()))
    direct_type = st.selectbox("直送類型", ["手機/平板 (5%+2%)", "耳機-品牌 (10%+2%)", "耳機-其他 (12%+2%)"])

# 核心計算
p_rate, s_rate = FEE_DB[m_cat][s_cat_name]
res_拍 = p - (p*(p_rate/100)) - (p*(pay_r/100)) - (p*0.03) - ev
res_商 = p - (p*(s_rate/100)) - (p*(pay_r/100)) - (p*0.015) - ev
f_m = 5.0 if "手機" in direct_type else (10.0 if "品牌" in direct_type and "其他" not in direct_type else 12.0)
res_直 = p - (p*(f_m/100)) - (p*0.02)

# --- 上方卡片渲染 (字體統一 2.5em) ---
with col_拍:
    st.markdown(f"""<div class="result-card"><h3 class="title-拍">蝦拍(10倍券3%)</h3><p>品項: <b>{s_cat_name}</b></p><hr>
        <p class="label-text">實拿金額:</p><div class="payout-val">${res_拍:,.0f}</div>
        <p class="label-text">預估毛利:</p><div class="profit-val-card">${res_拍-c:,.0f}</div>
    </div>""", unsafe_allow_html=True)

with col_商:
    st.markdown(f"""<div class="result-card"><h3 class="title-商">蝦商(5倍券1.5%)</h3><p>品項: <b>{s_cat_name}</b></p><hr>
        <p class="label-text">實拿金額:</p><div class="payout-val">${res_商:,.0f}</div>
        <p class="label-text">預估毛利:</p><div class="profit-val-card">${res_商-c:,.0f}</div>
    </div>""", unsafe_allow_html=True)

with col_直:
    st.markdown(f"""<div class="result-card"><h3 class="title-直">蝦皮直送</h3><p>類型: <b>{direct_type.split(' (')[0]}</b></p><hr>
        <p class="label-text">實拿金額:</p><div class="payout-val">${res_直:,.0f}</div>
        <p class="label-text">預估毛利:</p><div class="profit-val-card">${res_直-c:,.0f}</div>
    </div>""", unsafe_allow_html=True)

# --- 6. 橫向比較表 (V15.3 欄位標記邏輯) ---
st.markdown("---")
st.markdown(f'<div class="table-header-custom">📊 各細項分類毛利分析表 (單價: ${p:,.0f} / 成本: ${c:,.0f})</div>', unsafe_allow_html=True)

rows = []
for cat, subs in FEE_DB.items():
    for sub_name, rates in subs.items():
        pr, sr = rates
        p_p = p - (p*(pr/100)) - (p*(pay_r/100)) - (p*0.03) - ev - c
        s_p = p - (p*(sr/100)) - (p*(pay_r/100)) - (p*0.015) - ev - c
        # 直送費率判定
        dfm = 5.0 if "手機" in sub_name or "平板" in sub_name else 12.0
        d_p = p - (p*(dfm/100)) - (p*0.02) - c
        rows.append({"分類細項": sub_name, "蝦拍利潤": int(p_p), "蝦商利潤": int(s_p), "直送利潤": int(d_p)})

df_compare = pd.DataFrame(rows)

# 修正重點：highlight_max 使用 axis=0 (代表欄 Column) 獨立標記每一欄的最大值
st.dataframe(
    df_compare.style.highlight_max(axis=0, color='#2ECC71', subset=["蝦拍利潤", "蝦商利潤", "直送利潤"])
    .format({"蝦拍利潤": "${:,.0f}", "蝦商利潤": "${:,.0f}", "直送利潤": "${:,.0f}"}),
    use_container_width=True
)
