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
        background-color: #ffffff; box-shadow: 0 4px 10px rgba(0,0,0,0.05); min-height: 580px;
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
    st.markdown('<div style="font-size:11px; color:#95a5a6;">馬尼專用蝦皮計算機<br>版本：V17.0 (家用電器+券配置版)<br>© 2025 Mani Shopee Calc</div>', unsafe_allow_html=True)

# 4. 擴充資料庫 (加入家用電器)
FEE_DB = {
    "手機平板與周邊": {"手機": [5.5, 3.8], "平板電腦": [5.5, 4.0], "穿戴裝置": [5.5, 4.5]},
    "影音/相機": {"耳機/麥克風": [5.5, 6.5], "音響/喇叭": [6.0, 7.5]},
    "電腦與周邊": {"筆記型電腦": [5.0, 4.0], "桌上型電腦": [5.5, 5.0]},
    "家用電器": {
        "大型家電 (冰箱/洗衣機)": [5.3, 5.8],
        "生活/廚房家電": [5.5, 6.0],
        "投影機與周邊": [7.5, 8.5],
        "居安零件/遙控器": [6.0, 8.0]
    }
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

    # --- 全局參數設定 (券配置功能) ---
    with st.expander("⚙️ 全局參數與公式設定", expanded=False):
        custom_p_rate = st.number_input(f"【{s_cat_name}】蝦拍成交率 (%)", value=s_cat_item[1][0], step=0.1)
        custom_s_rate = st.number_input(f"【{s_cat_name}】蝦商成交率 (%)", value=s_cat_item[1][1], step=0.1)
        st.markdown("---")
        
        # 券 1 配置
        col_v1_1, col_v1_2 = st.columns([2, 1])
        v1_rate = col_v1_1.number_input("10倍蝦拍券回饋 (%)", value=3.0, step=0.1)
        v1_target = col_v1_2.selectbox("配置到", ["蝦拍", "蝦商"], key="v1_t")
        
        # 券 2 配置
        col_v2_1, col_v2_2 = st.columns([2, 1])
        v2_rate = col_v2_1.number_input("5倍蝦拍券回饋 (%)", value=1.5, step=0.1)
        v2_target = col_v2_2.selectbox("配置到", ["蝦拍", "蝦商"], index=1, key="v2_t")
        
        st.markdown("---")
        cfg_直_後毛 = st.number_input("直送後毛費率 (%)", value=2.0, step=0.1)
        cfg_直_前毛_手機 = st.number_input("直送前毛(手機/平板) (%)", value=5.0, step=0.1)
        cfg_直_前毛_其他 = st.number_input("直送前毛(其他) (%)", value=12.0, step=0.1)

# 計算邏輯 (動態券位)
shared_fee = round(p * (pay_r / 100)) + ev

# 判定哪個券在蝦拍，哪個在蝦商
p_v_rate = v1_rate if v1_target == "蝦拍" else (v2_rate if v2_target == "蝦拍" else 0)
p_v_name = "10倍券" if v1_target == "蝦拍" else ("5倍券" if v2_target == "蝦拍" else "自訂券")

s_v_rate = v1_rate if v1_target == "蝦商" else (v2_rate if v2_target == "蝦商" else 0)
s_v_name = "10倍券" if v1_target == "蝦商" else ("5倍券" if v2_target == "蝦商" else "自訂券")

# 蝦拍
tf1 = round(p * (custom_p_rate / 100))
cf1 = round(p * (p_v_rate / 100))
total_fee1 = tf1 + cf1 + shared_fee
payout1 = p - total_fee1

# 蝦商
tf2 = round(p * (custom_s_rate / 100))
cf2 = round(p * (s_v_rate / 100))
total_fee2 = tf2 + cf2 + shared_fee
payout2 = p - total_fee2

# 直送
f_m_val = cfg_直_前毛_手機 if ("手機" in s_cat_name or "平板" in s_cat_name) else cfg_直_前毛_其他
tf3 = round(p * (f_m_val / 100))
tb3 = round(p * (cfg_直_後毛 / 100))
total_fee3 = tf3 + tb3
payout3 = p - total_fee3

# --- 畫面渲染 ---
with col_拍:
    st.markdown(f"""<div class="result-card"><h3 class="title-拍">蝦拍({p_v_name}{p_v_rate}%)</h3>
        <p style="color:gray; font-size:0.9em;">品項: {s_cat_name}</p><hr>
        <p class="formula-text">公式: {p} × {custom_p_rate}%</p>
        <p class="expense-tag">成交手續費: -${tf1:,.0f}</p>
        <p class="formula-text">公式: {p} × {p_v_rate}%</p>
        <p class="expense-tag">{p_v_name}費: -${cf1:,.0f}</p>
        <p class="formula-text">公式: ({p} × {pay_r}%) + {ev}</p>
        <p class="expense-tag">金流/活動費: -${shared_fee:,.0f}</p>
        <div class="total-fee-tag">手續費總計: -${total_fee1:,.0f}</div>
        <hr>
        <div class="data-row"><span class="label-text">實拿金額:</span><span class="val-15 payout-color">${payout1:,.0f}</span></div>
        <div class="data-row"><span class="label-text">預估毛利:</span><span class="val-15 profit-color">${payout1-c:,.0f}</span></div>
    </div>""", unsafe_allow_html=True)

with col_商:
    st.markdown(f"""<div class="result-card"><h3 class="title-商">蝦商({s_v_name}{s_v_rate}%)</h3>
        <p style="color:gray; font-size:0.9em;">品項: {s_cat_name}</p><hr>
        <p class="formula-text">公式: {p} × {custom_s_rate}%</p>
        <p class="expense-tag">成交手續費: -${tf2:,.0f}</p>
        <p class="formula-text">公式: {p} × {s_v_rate}%</p>
        <p class="expense-tag">{s_v_name}費: -${cf2:,.0f}</p>
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

# --- 6. 橫向比較表 ---
st.markdown("---")
st.markdown(f'<div style="color:#2980B9; font-weight:bold; font-size:20px; background:#F8F9F9; padding:12px; border-left:5px solid #2980B9;">📊 全品項分類毛利對照 (單價: ${p:,.0f} / 成本: ${c:,.0f})</div>', unsafe_allow_html=True)

rows = []
for cat, subs in FEE_DB.items():
    for sub_name, rates in subs.items():
        pr_row = custom_p_rate if sub_name == s_cat_name else rates[0]
        sr_row = custom_s_rate if sub_name == s_cat_name else rates[1]
        p_p = p - (round(p*(pr_row/100)) + round(p*(p_v_rate/100)) + shared_fee) - c
        s_p = p - (round(p*(sr_row/100)) + round(p*(s_v_rate/100)) + shared_fee) - c
        dfm_val_row = cfg_直_前毛_手機 if ("手機" in sub_name or "平板" in sub_name) else cfg_直_前毛_其他
        d_p = p - (round(p*(dfm_val_row/100)) + round(p*(cfg_直_後毛/100))) - c
        rows.append({"分類細項": sub_name, "蝦拍利潤": int(p_p), "蝦商利潤": int(s_p), "直送利潤": int(d_p)})

df_compare = pd.DataFrame(rows)
st.dataframe(
    df_compare.style.highlight_max(axis=0, color='#2ECC71', subset=["蝦拍利潤", "蝦商利潤", "直送利潤"])
    .format({"蝦拍利潤": "${:,.0f}", "蝦商利潤": "${:,.0f}", "直送利潤": "${:,.0f}"}),
    use_container_width=True
)
