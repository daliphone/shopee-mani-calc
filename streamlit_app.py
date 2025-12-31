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
    .result-card { border: 1px solid #e6e9ef; padding: 20px; border-radius: 12px; background-color: #ffffff; box-shadow: 0 4px 10px rgba(0,0,0,0.05); min-height: 580px; }
    .title-拍 { color: #333333; border-bottom: 2px solid #333333; padding-bottom: 5px; }
    .title-商 { color: #EE4D2D; border-bottom: 2px solid #EE4D2D; padding-bottom: 5px; }
    .title-直 { color: #2980B9; border-bottom: 2980B9; border-bottom: 2px solid #2980B9; padding-bottom: 5px; }
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
    st.markdown('<div style="font-size:11px; color:#95a5a6;">馬尼專用蝦皮計算機<br>版本：V18.0 (三層分類版)<br>© 2025 Mani Shopee Calc</div>', unsafe_allow_html=True)

# 4. 【三層架構資料庫】 格式: 首頁分類 > 第二層 > 第三層: [蝦拍%, 蝦商%]
# 依據 PDF 規範精確分類
DB_3L = {
    "手機平板與周邊": {
        "手機與平板電腦": {
            "手機": [5.5, 3.8], "平板電腦": [5.5, 4.0], "穿戴裝置": [5.5, 4.5]
        },
        "手機平板周邊配件": {
            "保護殼/保護貼": [7.5, 9.5], "行動電源/傳輸線": [7.5, 9.5], "對講機": [6.5, 9.5]
        }
    },
    "影音/相機": {
        "電視機與周邊配件": {
            "電視機": [5.5, 5.0], "影音周邊配件": [6.0, 8.0], "電視盒": [6.0, 8.0]
        },
        "相機與空拍機": {
            "數位相機/單眼": [5.0, 5.0], "空拍機/運動攝影機": [5.0, 5.0], "鏡頭": [5.0, 5.0], "相機周邊配件": [6.5, 8.0]
        },
        "音響與耳機": {
            "耳機/耳麥": [5.5, 6.5], "音響/喇叭": [6.0, 7.5], "麥克風": [6.0, 7.5]
        }
    },
    "家用電器": {
        "廚房家電": {
            "氣炸鍋/微波爐": [5.5, 6.0], "電熱水瓶/烤箱": [5.5, 6.0], "淨水設備": [5.5, 6.5]
        },
        "生活家電": {
            "吸塵器/掃地機器人": [5.5, 6.0], "電風扇/空調": [5.5, 6.0], "美容家電 (吹風機)": [5.5, 6.5]
        },
        "大型家電": {
            "冰箱": [5.3, 5.8], "洗衣機": [5.3, 5.8], "乾衣機": [5.3, 5.8]
        }
    },
    "電腦與周邊配件": {
        "電腦主機與螢幕": {
            "筆記型電腦": [5.0, 4.0], "桌上型電腦": [5.5, 5.0], "螢幕裝置": [5.5, 5.5]
        },
        "電腦零組件與儲存": {
            "電腦零組件": [6.0, 6.5], "硬碟/隨身碟": [5.5, 5.5], "顯示卡": [6.0, 6.5]
        },
        "網路設備與周邊": {
            "網路設備": [6.5, 8.0], "鍵盤滑鼠": [6.0, 7.0], "電腦周邊/軟體": [7.5, 9.5]
        }
    },
    "電玩遊戲": {
        "遊戲主機與配件": {
            "遊戲主機": [4.0, 4.0], "遊戲控制器": [5.5, 6.5], "遊戲周邊配件": [5.5, 6.5]
        },
        "遊戲軟體": {
            "遊戲片": [5.5, 6.5], "點數卡": [5.5, 6.5]
        }
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
    # 三層連動選單
    l1 = st.selectbox("首頁分類", list(DB_3L.keys()))
    l2 = st.selectbox("第二層分類", list(DB_3L[l1].keys()))
    l3_list = list(DB_3L[l1][l2].items())
    l3_item = st.selectbox("第三層分類", l3_list, format_func=lambda x: f"{x[0]} [拍:{x[1][0]}% / 商:{x[1][1]}%]")
    
    s_cat_name = l3_item[0]
    p_rate_init, s_rate_init = l3_item[1]

    with st.expander("⚙️ 全局參數與公式設定", expanded=False):
        custom_p_rate = st.number_input(f"【{s_cat_name}】蝦拍率 (%)", value=p_rate_init, step=0.1)
        custom_s_rate = st.number_input(f"【{s_cat_name}】蝦商率 (%)", value=s_rate_init, step=0.1)
        st.markdown("---")
        col_v1_1, col_v1_2 = st.columns([2, 1])
        v1_rate = col_v1_1.number_input("10倍蝦拍券回饋 (%)", value=3.0, step=0.1)
        v1_target = col_v1_2.selectbox("配置到", ["蝦拍", "蝦商"], key="v1_t")
        col_v2_1, col_v2_2 = st.columns([2, 1])
        v2_rate = col_v2_1.number_input("5倍蝦拍券回饋 (%)", value=1.5, step=0.1)
        v2_target = col_v2_2.selectbox("配置到", ["蝦拍", "蝦商"], index=1, key="v2_t")
        st.markdown("---")
        cfg_直_後毛 = st.number_input("直送後毛率 (%)", value=2.0, step=0.1)
        cfg_直_前毛_手機 = st.number_input("直送前毛(手機/平板) (%)", value=5.0, step=0.1)
        cfg_直_前毛_其他 = st.number_input("直送前毛(其他) (%)", value=12.0, step=0.1)

# 計算邏輯 (券位配置與四捨五入)
shared_fee = round(p * (pay_r / 100)) + ev
p_v_rate = v1_rate if v1_target == "蝦拍" else (v2_rate if v2_target == "蝦拍" else 0)
s_v_rate = v1_rate if v1_target == "蝦商" else (v2_rate if v2_target == "蝦商" else 0)
p_v_name = "10倍券" if v1_target == "蝦拍" else "5倍券"
s_v_name = "10倍券" if v1_target == "蝦商" else "5倍券"

# 實拿計算
tf1 = round(p*(custom_p_rate/100)); cf1 = round(p*(p_v_rate/100)); tot1 = tf1+cf1+shared_fee; po1 = p-tot1
tf2 = round(p*(custom_s_rate/100)); cf2 = round(p*(s_v_rate/100)); tot2 = tf2+cf2+shared_fee; po2 = p-tot2
f_m = cfg_直_前毛_手機 if ("手機" in s_cat_name or "平板" in s_cat_name) else cfg_直_前毛_其他
tf3 = round(p*(f_m/100)); tb3 = round(p*(cfg_直_後毛/100)); tot3 = tf3+tb3; po3 = p-tot3

# --- 渲染卡片 ---
with col_拍:
    st.markdown(f"""<div class="result-card"><h3 class="title-拍">蝦拍({p_v_name}{p_v_rate}%)</h3>
        <p style="color:gray; font-size:0.85em;">{l1} > {l2}<br>品項: {s_cat_name}</p><hr>
        <p class="expense-tag">成交手續費: -${tf1:,.0f}</p>
        <p class="expense-tag">{p_v_name}費: -${cf1:,.0f}</p>
        <p class="expense-tag">金流/活動費: -${shared_fee:,.0f}</p>
        <div class="total-fee-tag">手續費總計: -${tot1:,.0f}</div><hr>
        <div class="data-row"><span class="label-text">實拿金額:</span><span class="val-15 payout-color">${po1:,.0f}</span></div>
        <div class="data-row"><span class="label-text">預估毛利:</span><span class="val-15 profit-color">${po1-c:,.0f}</span></div>
    </div>""", unsafe_allow_html=True)

with col_商:
    st.markdown(f"""<div class="result-card"><h3 class="title-商">蝦商({s_v_name}{s_v_rate}%)</h3>
        <p style="color:gray; font-size:0.85em;">{l1} > {l2}<br>品項: {s_cat_name}</p><hr>
        <p class="expense-tag">成交手續費: -${tf2:,.0f}</p>
        <p class="expense-tag">{s_v_name}費: -${cf2:,.0f}</p>
        <p class="expense-tag">金流/活動費: -${shared_fee:,.0f}</p>
        <div class="total-fee-tag">手續費總計: -${tot2:,.0f}</div><hr>
        <div class="data-row"><span class="label-text">實拿金額:</span><span class="val-15 payout-color">${po2:,.0f}</span></div>
        <div class="data-row"><span class="label-text">預估毛利:</span><span class="val-15 profit-color">${po2-c:,.0f}</span></div>
    </div>""", unsafe_allow_html=True)

with col_直:
    st.markdown(f"""<div class="result-card"><h3 class="title-直">蝦皮直送</h3>
        <p style="color:gray; font-size:0.85em;">判斷: {"手機平板" if f_m == cfg_直_前毛_手機 else "其他"}<br>品項: {s_cat_name}</p><hr>
        <p class="expense-tag">前毛手續費: -${tf3:,.0f}</p>
        <p class="expense-tag">後毛手續費: -${tb3:,.0f}</p>
        <div class="total-fee-tag">手續費總計: -${tot3:,.0f}</div>
        <p style="color:#95a5a6; font-size:0.85em; margin: 25px 0;">(不計金流/活動/券)</p><hr>
        <div class="data-row"><span class="label-text">實拿金額:</span><span class="val-15 payout-color">${po3:,.0f}</span></div>
        <div class="data-row"><span class="label-text">預估毛利:</span><span class="val-15 profit-color">${po3-c:,.0f}</span></div>
    </div>""", unsafe_allow_html=True)

# --- 6. 橫向比較表 ---
st.markdown("---")
st.subheader(f"📊 全品項分類毛利對照 (單價: ${p:,.0f} / 成本: ${c:,.0f})")
rows = []
for cat_l1, subs_l2 in DB_3L.items():
    for sub_l2, items_l3 in subs_l2.items():
        for sub_l3, rates in items_l3.items():
            pr = custom_p_rate if sub_l3 == s_cat_name else rates[0]
            sr = custom_s_rate if sub_l3 == s_cat_name else rates[1]
            p_p = p - (round(p*(pr/100)) + round(p*(p_v_rate/100)) + shared_fee) - c
            s_p = p - (round(p*(sr/100)) + round(p*(s_v_rate/100)) + shared_fee) - c
            dfm_v = cfg_直_前毛_手機 if ("手機" in sub_l3 or "平板" in sub_l3) else cfg_直_前毛_其他
            d_p = p - (round(p*(dfm_v/100)) + round(p*(cfg_直_後毛/100))) - c
            rows.append({"三層分類": f"{cat_l1}>{sub_l2}>{sub_l3}", "蝦拍利潤": int(p_p), "蝦商利潤": int(s_p), "直送利潤": int(d_p)})

df_compare = pd.DataFrame(rows)
st.dataframe(df_compare.style.highlight_max(axis=0, color='#2ECC71', subset=["蝦拍利潤", "蝦商利潤", "直送利潤"]).format({"蝦拍利潤": "${:,.0f}", "蝦商利潤": "${:,.0f}", "直送利潤": "${:,.0f}"}), use_container_width=True)
