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
    .result-card { border: 1px solid #e6e9ef; padding: 20px; border-radius: 12px; background-color: #ffffff; box-shadow: 0 4px 10px rgba(0,0,0,0.05); min-height: 550px; }
    .title-拍 { color: #333333; border-bottom: 2px solid #333333; padding-bottom: 5px; }
    .title-商 { color: #EE4D2D; border-bottom: 2px solid #EE4D2D; padding-bottom: 5px; }
    .title-直 { color: #2980B9; border-bottom: 2px solid #2980B9; padding-bottom: 5px; }
    .formula-text { color: #95a5a6; font-size: 0.85em; font-style: italic; margin-bottom: 2px; font-weight: bold; }
    .data-row { display: flex; justify-content: flex-start; align-items: baseline; gap: 10px; margin-top: 8px; }
    .label-text { font-size: 1.1em; font-weight: bold; color: #555; white-space: nowrap; }
    .val-15 { font-size: 1.5em; font-weight: 900; line-height: 1; }
    .payout-color { color: #2c3e50; }
    .profit-color { color: #27AE60; }
    .expense-tag { color: #E74C3C; font-size: 0.95em; margin: 2px 0; font-weight: bold; }
    .total-fee-tag { color: #C0392B; font-weight: bold; font-size: 1em; margin: 8px 0; padding: 8px; background: #FDEDEC; border-radius: 5px; border-left: 4px solid #C0392B; }
    hr { border: 0; border-top: 1px solid #eee; margin: 8px 0; }
    </style>
    """, unsafe_allow_html=True)

# 3. 側邊欄
with st.sidebar:
    st.header("⚙️ 系統資訊")
    st.markdown('<div style="font-size:11px; color:#95a5a6;">馬尼專用蝦皮計算機<br>版本：V22.0 (資料庫清空版)<br>© 2025 Mani Shopee Calc</div>', unsafe_allow_html=True)

# 4. 【資料庫已移除 - 改為手動輸入】
DB_FINAL = {
    "自定義分類": {
        "手動輸入費率項目": { "自定義品項": [0.0, 0.0] }
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
    # 下拉選單保留結構，但僅供占位，主要由下方全局設定控制
    l1 = st.selectbox("1. 首頁分類", list(DB_FINAL.keys()))
    l2 = st.selectbox("2. 第二層分類", list(DB_FINAL[l1].keys()))
    l3_item = st.selectbox("3. 第三層分類", list(DB_FINAL[l1][l2].keys()))
    
    rates_init = DB_FINAL[l1][l2][l3_item]

    with st.expander("⚙️ 全局參數與公式設定", expanded=True):
        st.info("請於下方手動輸入此商品的成交費率：")
        custom_p_rate = st.number_input(f"蝦拍成交費率 (%)", value=rates_init[0], step=0.1)
        custom_s_rate = st.number_input(f"蝦商成交費率 (%)", value=rates_init[1], step=0.1)
        st.markdown("---")
        v1_rate = st.number_input("10倍蝦拍券回饋 (%)", value=3.0, step=0.1)
        v1_target = st.selectbox("配置到", ["蝦拍", "蝦商"], key="v1_t")
        v2_rate = st.number_input("5倍蝦拍券回饋 (%)", value=1.5, step=0.1)
        v2_target = st.selectbox("配置到", ["蝦拍", "蝦商"], index=1, key="v2_t")
        st.markdown("---")
        cfg_直_後毛 = st.number_input("直送後毛率 (%)", value=2.0, step=0.1)
        cfg_直_前毛_手機 = st.number_input("直送前毛(手機/平板) (%)", value=5.0, step=0.1)
        cfg_直_前毛_其他 = st.number_input("直送前毛(其他) (%)", value=12.0, step=0.1)

# 計算邏輯
shared_fee = round(p * (pay_r / 100)) + ev
p_v_rate = v1_rate if v1_target == "蝦拍" else (v2_rate if v2_target == "蝦拍" else 0)
s_v_rate = v1_rate if v1_target == "蝦商" else (v2_rate if v2_target == "蝦商" else 0)
p_v_n = "10倍券" if v1_target == "蝦拍" else "5倍券"
s_v_n = "10倍券" if v1_target == "蝦商" else "5倍券"

tf1 = round(p*(custom_p_rate/100)); cf1 = round(p*(p_v_rate/100)); tot1 = tf1+cf1+shared_fee
tf2 = round(p*(custom_s_rate/100)); cf2 = round(p*(s_v_rate/100)); tot2 = tf2+cf2+shared_fee
# 直送判斷逻辑簡化為依據全局參數
f_m = cfg_直_前毛_手機 if p > 0 else cfg_直_前毛_其他 
tf3 = round(p*(f_m/100)); tb3 = round(p*(cfg_直_後毛/100)); tot3 = tf3+tb3

# --- 渲染卡片 ---
with col_拍:
    st.markdown(f"""<div class="result-card"><h3 class="title-拍">蝦拍({p_v_n}{p_v_rate}%)</h3>
        <p style="color:gray; font-size:0.85em;">手動定義項目</p><hr>
        <p class="formula-text">公式: {p} × {custom_p_rate}%</p><p class="expense-tag">成交手續費: -${tf1:,.0f}</p>
        <p class="formula-text">公式: {p} × {p_v_rate}%</p><p class="expense-tag">{p_v_n}費: -${cf1:,.0f}</p>
        <p class="formula-text">公式: ({p} × {pay_r}%) + {ev}</p><p class="expense-tag">金流/活動費: -${shared_fee:,.0f}</p>
        <div class="total-fee-tag">手續費總計: -${tot1:,.0f}</div><hr>
        <div class="data-row"><span class="label-text">實拿金額:</span><span class="val-15 payout-color">${p-tot1:,.0f}</span></div>
        <div class="data-row"><span class="label-text">預估毛利:</span><span class="val-15 profit-color">${p-tot1-c:,.0f}</span></div>
    </div>""", unsafe_allow_html=True)

with col_商:
    st.markdown(f"""<div class="result-card"><h3 class="title-商">蝦商({s_v_n}{s_v_rate}%)</h3>
        <p style="color:gray; font-size:0.85em;">手動定義項目</p><hr>
        <p class="formula-text">公式: {p} × {custom_s_rate}%</p><p class="expense-tag">成交手續費: -${tf2:,.0f}</p>
        <p class="formula-text">公式: {p} × {s_v_rate}%</p><p class="expense-tag">{s_v_n}費: -${cf2:,.0f}</p>
        <p class="formula-text">公式: ({p} × {pay_r}%) + {ev}</p><p class="expense-tag">金流/活動費: -${shared_fee:,.0f}</p>
        <div class="total-fee-tag">手續費總計: -${tot2:,.0f}</div><hr>
        <div class="data-row"><span class="label-text">實拿金額:</span><span class="val-15 payout-color">${p-tot2:,.0f}</span></div>
        <div class="data-row"><span class="label-text">預估毛利:</span><span class="val-15 profit-color">${p-tot2-c:,.0f}</span></div>
    </div>""", unsafe_allow_html=True)

with col_直:
    st.markdown(f"""<div class="result-card"><h3 class="title-直">蝦皮直送</h3>
        <p style="color:gray; font-size:0.85em;">依據全局前毛設定</p><hr>
        <p class="formula-text">公式: {p} × {f_m}%</p><p class="expense-tag">前毛手續費: -${tf3:,.0f}</p>
        <p class="formula-text">公式: {p} × {cfg_直_後毛}%</p><p class="expense-tag">後毛手續費: -${tb3:,.0f}</p>
        <div class="total-fee-tag">手續費總計: -${tot3:,.0f}</div><hr>
        <div class="data-row"><span class="label-text">實拿金額:</span><span class="val-15 payout-color">${p-tot3:,.0f}</span></div>
        <div class="data-row"><span class="label-text">預估毛利:</span><span class="val-15 profit-color">${p-tot3-c:,.0f}</span></div>
    </div>""", unsafe_allow_html=True)

# --- 6. 橫向比較表 (僅顯示當前手動輸入結果) ---
st.markdown("---")
st.subheader(f"📊 當前自定義毛利對照 (單價: ${p:,.0f} / 成本: ${c:,.0f})")
rows = [{"項目": "手動設定品項", "蝦拍利潤": int(p-tot1-c), "蝦商利潤": int(p-tot2-c), "直送利潤": int(p-tot3-c)}]
df_compare = pd.DataFrame(rows)
st.table(df_compare)
