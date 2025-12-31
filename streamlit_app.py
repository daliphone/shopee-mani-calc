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
    st.markdown('<div style="font-size:11px; color:#95a5a6;">馬尼專用蝦皮計算機<br>版本：V16.0 (旗艦版)<br>© 2025 Mani Shopee Calc</div>', unsafe_allow_html=True)

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
    p_rate, s_rate = s_cat_item[1]

    # --- 第二層：全局參數設定 ---
    with st.expander("⚙️ 全局參數與公式設定", expanded=False):
        st.caption("調整下方數值將影響全站計算結果")
        cfg_拍_券 = st.number_input("蝦拍券回饋 (%)", value=3.0, step=0.1)
        cfg_商_券 = st.number_input("蝦商券回饋 (%)", value=1.5, step=0.1)
        cfg_直_後毛 = st.number_input("直送後毛費率 (%)", value=2.0, step=0.1)
        cfg_直_前毛_手機 = st.number_input("直送前毛(手機/平板) (%)", value=5.0, step=0.1)
        cfg_直_前毛_其他 = st.number_input("直送前毛(其他) (%)", value=12.0, step=0.1)

# 核心計算邏輯 (全局四捨五入)
# 公式 A: 共通金流活動費 = round(單價 * 金流率) + 活動費
shared_fee = round(p * (pay_r / 100)) + ev

# 蝦拍計算
tf1 = round(p * (p_rate / 100))
cf1 = round(p * (cfg_拍_券 / 100))
total_fee1 = tf1 + cf1 + shared_fee
payout1 = p - total_fee1

# 蝦商計算
tf2 = round(p * (s_rate / 100))
cf2 = round(p * (cfg_商_券 / 100))
total_fee2 = tf2 + cf2 + shared_fee
payout2 = p - total_fee2

# 直送計算 (依據分類自動切換前毛)
f_m_val = cfg_直_前毛_手機 if ("手機" in s_cat_name or "平板" in s_cat_name) else cfg_直_前毛_其他
tf3 = round(p * (f_m_val / 100))
tb3 = round(p * (cfg_直_後毛 / 100))
total_fee3 = tf3 + tb3
payout3 = p - total_fee3

# --- 畫面渲染 ---
with col_拍:
    st.markdown(f"""<div class="result-card"><h3 class="title-拍">蝦拍(一般)</h3>
        <p style="color:gray; font-size:0.9em;">品項: {s_cat_name}</p><hr>
        <p class="formula-text">公式: {p} × {p_rate}%</p>
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
        <p class="formula-text">公式: {p} × {s_rate}%</p>
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
        <p style="color:gray; font-size:0.9em;">判斷類別: {"手機/平板" if f_m_val == cfg_直_前毛_手機 else "其他"}</p><hr>
        <p class="formula-text">公式: {p} × {f_m_val}%</p>
        <p class="expense-tag">前毛手續費: -${tf3:,.0f}</p>
        <p class="formula-text">公式: {p} × {cfg_直_後毛}%</p>
        <p class="expense-tag">後毛手續費: -${tb3:,.0f}</p>
        <div class="total-fee-tag">手續費總計: -${total_fee3:,.0f}</div>
        <p style="color:#95a5a6; font-size:0.85em; margin: 20px 0;">(不計金流/活動/券)</p>
        <hr>
        <div class="data-row"><span class="label-text">實拿金額:</span><span class="val-15 payout-color">${payout3:,.0f}</span></div>
        <div class="data-row"><span class="label-text">預估毛利:</span><span class="val-15 profit-color">${payout3-c:,.0f}</span></div>
    </div>""", unsafe_allow_html=True)

# --- 6. 橫向比較表 (同步後台參數) ---
st.markdown("---")
st.markdown(f'<div style="color:#2980B9; font-weight:bold; font-size:20px; background:#F8F9F9; padding:12px; border-left:5px solid #2980B9;">📊 全品項分類毛利對照 (單價: ${p:,.0f} / 成本: ${c:,.0f})</div>', unsafe_allow_html=True)

rows = []
for cat, subs in FEE_DB.items():
    for sub_name, rates in subs.items():
        pr, sr = rates
        # 套用四捨五入與自訂參數
        p_p = p - (round(p*(pr/100)) + round(p*(cfg_拍_券/100)) + shared_fee) - c
        s_p = p - (round(p*(sr/100)) + round(p*(cfg_商_券/100)) + shared_fee) - c
        dfm_val = cfg_直_前毛_手機 if ("手機" in sub_name or "平板" in sub_name) else cfg_直_前毛_其他
        d_p = p - (round(p*(dfm_val/100)) + round(p*(cfg_直_後毛/100))) - c
        rows.append({"分類細項": sub_name, "蝦拍利潤": int(p_p), "蝦商利潤": int(s_p), "直送利潤": int(d_p)})

df_compare = pd.DataFrame(rows)
st.dataframe(
    df_compare.style.highlight_max(axis=0, color='#2ECC71', subset=["蝦拍利潤", "蝦商利潤", "直送利潤"])
    .format({"蝦拍利潤": "${:,.0f}", "蝦商利潤": "${:,.0f}", "直送利潤": "${:,.0f}"}),
    use_container_width=True
)
