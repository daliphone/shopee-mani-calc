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
    div[data-testid="stNumberInput"] input { font-size: 20px !important; font-weight: 900 !important; color: #E67E22 !important; }
    
    /* 結果卡片樣式 */
    .result-card { 
        border: 1px solid #e6e9ef; padding: 22px; border-radius: 12px; 
        background-color: #ffffff; box-shadow: 0 4px 10px rgba(0,0,0,0.05); min-height: 520px;
    }
    .title-拍 { color: #333333; border-bottom: 2px solid #333333; padding-bottom: 5px; margin-bottom: 5px; }
    .title-商 { color: #EE4D2D; border-bottom: 2px solid #EE4D2D; padding-bottom: 5px; margin-bottom: 5px; }
    .title-直 { color: #2980B9; border-bottom: 2px solid #2980B9; padding-bottom: 5px; margin-bottom: 5px; }
    
    .cat-display { color: #7F8C8D; font-size: 0.9em; margin-bottom: 15px; font-weight: bold; }
    
    /* 數值同列排版 (Flexbox) */
    .data-row {
        display: flex;
        justify-content: flex-start;
        align-items: baseline;
        gap: 12px;
        margin-top: 10px;
    }
    .label-text { font-size: 1.1em; font-weight: bold; color: #555; white-space: nowrap; }
    .val-15 { font-size: 1.5em; font-weight: 900; line-height: 1; }
    .payout-color { color: #2c3e50; }
    .profit-color { color: #27AE60; }
    
    .expense-tag { color: #E74C3C; font-size: 0.95em; margin: 3px 0; }
    .total-fee-tag { color: #C0392B; font-weight: bold; font-size: 1.05em; margin: 8px 0; padding: 5px; background: #FDEDEC; border-radius: 5px; }
    
    hr { border: 0; border-top: 1px solid #eee; margin: 10px 0; }
    
    .table-header-custom {
        color: #2980B9; font-weight: bold; font-size: 20px;
        background-color: #F8F9F9; padding: 12px; border-radius: 8px;
        border-left: 5px solid #2980B9; margin-bottom: 15px;
    }
    .stDataFrame [data-testid="styled-table-cell"] { font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 側邊欄
with st.sidebar:
    st.header("⚙️ 系統資訊")
    st.markdown('<div style="font-size:11px; color:#95a5a6;">馬尼專用蝦皮計算機<br>版本：V15.7 (精確計算版)<br>© 2025 Mani Shopee Calc</div>', unsafe_allow_html=True)

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
    # 預設值調整為 0
    p = st.number_input("成交單價 ($)", min_value=0, value=0, key="p")
    c = st.number_input("商品成本 ($)", min_value=0, value=0, key="c")
    pay_r = st.number_input("金流費率 (%)", value=2.5, step=0.1, key="pr")
    ev = st.number_input("活動日費用 ($)", value=60, key="ef")
    st.markdown("---")
    m_cat = st.selectbox("品類大類", list(FEE_DB.keys()))
    
    # 選項顯示 % 數
    s_cat_list = list(FEE_DB[m_cat].items())
    s_cat_item = st.selectbox("細項分類", s_cat_list, format_func=lambda x: f"{x[0]} [拍:{x[1][0]}% / 商:{x[1][1]}%]")
    s_cat_name = s_cat_item[0]
    p_rate, s_rate = s_cat_item[1]
    
    direct_type = st.selectbox("直送類型", ["手機/平板 (5%+2%)", "耳機-品牌 (10%+2%)", "耳機-其他 (12%+2%)"])

# 核心計算邏輯 (強制整數)
shared_fee = int(p * (pay_r / 100) + ev)

# A. 蝦拍
tf1, cf1 = int(p * (p_rate / 100)), int(p * 0.03)
total_fee1 = tf1 + cf1 + shared_fee
payout1 = p - total_fee1

# B. 蝦商
tf2, cf2 = int(p * (s_rate / 100)), int(p * 0.015)
total_fee2 = tf2 + cf2 + shared_fee
payout2 = p - total_fee2

# C. 蝦皮直送
f_m = 5.0 if "手機" in direct_type else (10.0 if "品牌" in direct_type and "其他" not in direct_type else 12.0)
tf3, tb3 = int(p * (f_m / 100)), int(p * 0.02)
total_fee3 = tf3 + tb3
payout3 = p - total_fee3

# --- 上方卡片渲染 ---
with col_拍:
    st.markdown(f"""<div class="result-card"><h3 class="title-拍">蝦拍(10倍券3%)</h3>
        <div class="cat-display">當前品類: {s_cat_name} ({p_rate}%)</div>
        <p class="expense-tag">成交手續: -${tf1:,.0f}</p>
        <p class="expense-tag">10倍券回饋: -${cf1:,.0f}</p>
        <p class="expense-tag">金流/活動費: -${shared_fee:,.0f}</p>
        <div class="total-fee-tag">手續費總計: -${total_fee1:,.0f}</div>
        <hr>
        <div class="data-row"><span class="label-text">實拿金額:</span><span class="val-15 payout-color">${payout1:,.0f}</span></div>
        <div class="data-row"><span class="label-text">預估毛利:</span><span class="val-15 profit-color">${payout1-c:,.0f}</span></div>
    </div>""", unsafe_allow_html=True)

with col_商:
    st.markdown(f"""<div class="result-card"><h3 class="title-商">蝦商(5倍券1.5%)</h3>
        <div class="cat-display">當前品類: {s_cat_name} ({s_rate}%)</div>
        <p class="expense-tag">成交手續: -${tf2:,.0f}</p>
        <p class="expense-tag">5倍券回饋: -${cf2:,.0f}</p>
        <p class="expense-tag">金流/活動費: -${shared_fee:,.0f}</p>
        <div class="total-fee-tag">手續費總計: -${total_fee2:,.0f}</div>
        <hr>
        <div class="data-row"><span class="label-text">實拿金額:</span><span class="val-15 payout-color">${payout2:,.0f}</span></div>
        <div class="data-row"><span class="label-text">預估毛利:</span><span class="val-15 profit-color">${payout2-c:,.0f}</span></div>
    </div>""", unsafe_allow_html=True)

with col_直:
    st.markdown(f"""<div class="result-card"><h3 class="title-直">蝦皮直送</h3>
        <div class="cat-display">類型: {direct_type.split(' (')[0]} ({f_m}+2%)</div>
        <p class="expense-tag">前毛手續: -${tf3:,.0f}</p>
        <p class="expense-tag">後毛手續: -${tb3:,.0f}</p>
        <div class="total-fee-tag">手續費總計: -${total_fee3:,.0f}</div>
        <p style="color:#95a5a6; font-size:0.85em; margin: 15px 0;">(不計金流/活動/券)</p>
        <hr>
        <div class="data-row"><span class="label-text">實拿金額:</span><span class="val-15 payout-color">${payout3:,.0f}</span></div>
        <div class="data-row"><span class="label-text">預估毛利:</span><span class="val-15 profit-color">${payout3-c:,.0f}</span></div>
    </div>""", unsafe_allow_html=True)

# --- 6. 橫向比較表 (確認算式無小數點) ---
st.markdown("---")
st.markdown(f'<div class="table-header-custom">📊 各細項分類毛利分析表 (單價: ${p:,.0f} / 成本: ${c:,.0f})</div>', unsafe_allow_html=True)

rows = []
for cat, subs in FEE_DB.items():
    for sub_name, rates in subs.items():
        pr, sr = rates
        # 算式同步卡片邏輯，確保無小數點誤差
        p_profit = p - (int(p*(pr/100)) + int(p*0.03) + shared_fee) - c
        s_profit = p - (int(p*(sr/100)) + int(p*0.015) + shared_fee) - c
        dfm_val = 5.0 if "手機" in sub_name or "平板" in sub_name else 12.0
        d_profit = p - (int(p*(dfm_val/100)) + int(p*0.02)) - c
        
        rows.append({"分類細項": sub_name, "蝦拍利潤": int(p_profit), "蝦商利潤": int(s_profit), "直送利潤": int(d_profit)})

df_compare = pd.DataFrame(rows)
st.dataframe(
    df_compare.style.highlight_max(axis=0, color='#2ECC71', subset=["蝦拍利潤", "蝦商利潤", "直送利潤"])
    .format({"蝦拍利潤": "${:,.0f}", "蝦商利潤": "${:,.0f}", "直送利潤": "${:,.0f}"}),
    use_container_width=True
)
