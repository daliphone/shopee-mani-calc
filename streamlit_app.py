import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. 頁面配置
st.set_page_config(page_title="馬尼專用蝦皮計算機", layout="wide", initial_sidebar_state="expanded")

# --- 初始化 Google Sheets 連線 ---
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # 這裡會讀取你在 Streamlit Secrets 中設定的憑證
    try:
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(credentials)
        return client
    except:
        return None

gc = init_connection()
SPREADSHEET_NAME = "馬尼銷售報表" # 請確保你的 Google Sheets 名稱為此或自行修改

# 2. CSS 全局美化
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif !important; }
    div[data-testid="stNumberInput"] label { font-size: 16px !important; font-weight: bold !important; color: #2C3E50 !important; }
    div[data-testid="stNumberInput"] input { font-size: 20px !important; font-weight: 900 !important; color: #E67E22 !important; }
    .result-card { border: 1px solid #e6e9ef; padding: 18px; border-radius: 12px; background-color: #ffffff; box-shadow: 0 4px 10px rgba(0,0,0,0.05); min-height: 650px; }
    .title-拍 { color: #333333; border-bottom: 2px solid #333333; padding-bottom: 5px; }
    .title-商 { color: #EE4D2D; border-bottom: 2px solid #EE4D2D; padding-bottom: 5px; }
    .title-直 { color: #2980B9; border-bottom: 2px solid #2980B9; padding-bottom: 5px; }
    .formula-text { color: #95a5a6; font-size: 0.8em; font-style: italic; margin-bottom: 2px; font-weight: bold; }
    .data-row { display: flex; justify-content: flex-start; align-items: baseline; gap: 8px; margin-top: 6px; }
    .label-text { font-size: 1.05em; font-weight: bold; color: #555; white-space: nowrap; }
    .val-15 { font-size: 1.5em; font-weight: 900; line-height: 1; }
    .val-no-v { font-size: 1.1em; font-weight: bold; color: #7F8C8D; text-decoration: none; }
    .payout-color { color: #2c3e50; }
    .profit-color { color: #27AE60; }
    .expense-tag { color: #E74C3C; font-size: 0.9em; margin: 2px 0; font-weight: bold; }
    .total-fee-tag { color: #C0392B; font-weight: bold; font-size: 0.95em; margin: 6px 0; padding: 6px; background: #FDEDEC; border-radius: 5px; border-left: 4px solid #C0392B; }
    hr { border: 0; border-top: 1px solid #eee; margin: 8px 0; }
    .table-header-green { color: #27AE60 !important; font-weight: bold; font-size: 20px; background-color: #F8F9F9; padding: 12px; border-radius: 8px; border-left: 5px solid #27AE60; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 側邊欄
with st.sidebar:
    st.header("👤 人員登錄")
    staff_name = st.text_input("人員姓名", value="馬尼員工")
    store_name = st.selectbox("所屬門市", ["門市A", "門市B", "門市C"])
    st.markdown("---")
    st.markdown('<div style="font-size:11px; color:#95a5a6;">版本：V25.1 (不含券對比版)</div>', unsafe_allow_html=True)

# 4. 【試算表對齊資料庫】 
DB_FINAL = {
    '手機平板與周邊': {
        '手機 (一般賣家5.5%、商城賣家3.8%)': {'NONE': [5.5, 3.8]},
        '平板電腦 (一般賣家5.5%、商城賣家4.0%)': {'NONE': [5.5, 4.0]},
        '穿戴裝置 (一般賣家5.5%、商城賣家4.5%)': {'NONE': [5.5, 4.5]},
        '對講機 (一般賣家6.5%、商城賣家9.5%)': {'NONE': [6.5, 9.5]},
        '手機周邊配件 (一般賣家7.5%、商城賣家9.5%)': {'NONE': [7.5, 9.5]}
    },
    '影音': {
        '綜合擴大機/混音器 (一般賣家4.0%、商城賣家6.0%)': {'NONE': [4.0, 6.0]},
        '耳機/耳麥/藍牙耳機 (一般賣家5.5%、商城賣家6.5%)': {'NONE': [5.5, 6.5]},
        '音響/喇叭 (一般賣家6.0%、商城賣家7.5%)': {'NONE': [6.0, 7.5]}
    },
    '家用電器': {
        '大型家電 (一般賣家5.3%、商城賣家5.8%)': {'NONE': [5.3, 5.8]},
        '生活家電 (一般賣家5.5%、商城賣家6.0%)': {'NONE': [5.5, 6.0]},
        '電視機與周邊配件 (一般賣家5.5%、商城賣家6.0%)': {'NONE': [5.5, 6.0]}
    },
    '電腦與周邊配件': {
        '筆記型電腦 (一般賣家5.0%、商城賣家4.0%)': {'NONE': [5.0, 4.0]},
        '電腦周邊配件': {
            '網路設備 (一般賣家6.0%、商城賣家7.5%)': [6.0, 7.5],
            '電腦線材 (一般賣家6.0%、商城賣家7.5%)': [6.0, 7.5]
        }
    }
} # (其餘品項省略，實際執行時請保留 V23.1 完整資料庫)

# 5. 輸入與布局
col_in, col_拍, col_商, col_直 = st.columns([1, 1, 1, 1])

with col_in:
    st.subheader("📋 數據輸入")
    p = st.number_input("成交單價 ($)", min_value=0, value=0, key="p")
    c = st.number_input("商品成本 ($)", min_value=0, value=0, key="c")
    pay_r = st.number_input("金流費率 (%)", value=2.5, step=0.1, key="pr")
    ev = st.number_input("活動日費用 ($)", value=60, key="ef")
    st.markdown("---")
    l1_keys = list(DB_FINAL.keys())
    l1 = st.selectbox("1. 首頁分類", l1_keys, index=l1_keys.index('手機平板與周邊'))
    l2 = st.selectbox("2. 第二層分類", list(DB_FINAL[l1].keys()))
    l3_dict = DB_FINAL[l1][l2]
    
    if "NONE" in l3_dict:
        s_cat_display = l2; rates_init = l3_dict["NONE"]
    else:
        l3_list = list(l3_dict.items())
        l3_item = st.selectbox("3. 第三層分類", l3_list, format_func=lambda x: x[0])
        s_cat_display = l3_item[0]; rates_init = l3_item[1]

    with st.expander("⚙️ 全局參數與公式設定", expanded=False):
        custom_p_rate = st.number_input(f"蝦拍費率 (%)", value=float(rates_init[0]), step=0.1)
        custom_s_rate = st.number_input(f"蝦商費率 (%)", value=float(rates_init[1]), step=0.1)
        st.markdown("---")
        v1_rate = st.number_input("10倍券回饋 (%)", value=3.0, step=0.1)
        v1_target = st.selectbox("配置到", ["蝦拍", "蝦商"], key="v1_t")
        v2_rate = st.number_input("5倍券回饋 (%)", value=1.5, step=0.1)
        v2_target = st.selectbox("配置到", ["蝦拍", "蝦商"], index=1, key="v2_t")
        st.markdown("---")
        cfg_直_後毛 = st.number_input("直送後毛率 (%)", value=2.0, step=0.1)
        cfg_直_前毛_手機 = st.number_input("直送前毛(手機/平板) (%)", value=5.0, step=0.1)
        cfg_直_前毛_其他 = st.number_input("直送前毛(其他) (%)", value=12.0, step=0.1)

# --- 核心計算邏輯 (全局四捨五入) ---
shared_fee = round(p * (pay_r / 100)) + ev
p_v_rate = v1_rate if v1_target == "蝦拍" else (v2_rate if v2_target == "蝦拍" else 0)
s_v_rate = v1_rate if v1_target == "蝦商" else (v2_rate if v2_target == "蝦商" else 0)
p_v_n = "10倍券" if v1_target == "蝦拍" else "5倍券"
s_v_n = "10倍券" if v1_target == "蝦商" else "5倍券"

# 蝦拍
tf1 = round(p*(custom_p_rate/100))
cf1 = round(p*(p_v_rate/100))
tot1 = tf1 + cf1 + shared_fee
po1 = p - tot1
# 不含券計算
po1_no_v = p - tf1 - shared_fee

# 蝦商
tf2 = round(p*(custom_s_rate/100))
cf2 = round(p*(s_v_rate/100))
tot2 = tf2 + cf2 + shared_fee
po2 = p - tot2
# 不含券計算
po2_no_v = p - tf2 - shared_fee

# 直送
f_m = cfg_直_前毛_手機 if ("手機" in l1 or "平板" in l1) else cfg_直_前毛_其他
tf3 = round(p*(f_m/100)); tb3 = round(p*(cfg_直_後毛/100)); tot3 = tf3+tb3; po3 = p-tot3

# --- 卡片渲染 ---
with col_拍:
    st.markdown(f"""<div class="result-card"><h3 class="title-拍">蝦拍({p_v_n}{p_v_rate}%)</h3>
        <p style="color:gray; font-size:0.8em;">{l1}<br>品項: {s_cat_display}</p><hr>
        <p class="formula-text">公式: {p} × {custom_p_rate}%</p><p class="expense-tag">成交手續費: -${tf1:,.0f}</p>
        <p class="formula-text">公式: {p} × {p_v_rate}%</p><p class="expense-tag">{p_v_n}費: -${cf1:,.0f}</p>
        <p class="formula-text">公式: ({p} × {pay_r}%) + {ev}</p><p class="expense-tag">金流/活動費: -${shared_fee:,.0f}</p>
        <div class="total-fee-tag">手續費總計: -${tot1:,.0f}</div><hr>
        <div class="data-row"><span class="label-text">實拿金額:</span><span class="val-15 payout-color">${po1:,.0f}</span></div>
        <div class="data-row"><span class="label-text">預估毛利:</span><span class="val-15 profit-color">${po1-c:,.0f}</span></div>
        <hr style="border-top: 1px dashed #ccc;">
        <div class="data-row"><span class="label-text" style="color:gray;">不含{p_v_n}實拿:</span><span class="val-no-v">${po1_no_v:,.0f}</span></div>
        <div class="data-row"><span class="label-text" style="color:gray;">不含{p_v_n}毛利:</span><span class="val-no-v">${po1_no_v-c:,.0f}</span></div>
    </div>""", unsafe_allow_html=True)

with col_商:
    st.markdown(f"""<div class="result-card"><h3 class="title-商">蝦商({s_v_n}{s_v_rate}%)</h3>
        <p style="color:gray; font-size:0.8em;">{l1}<br>品項: {s_cat_display}</p><hr>
        <p class="formula-text">公式: {p} × {custom_s_rate}%</p><p class="expense-tag">成交手續費: -${tf2:,.0f}</p>
        <p class="formula-text">公式: {p} × {s_v_rate}%</p><p class="expense-tag">{s_v_n}費: -${cf2:,.0f}</p>
        <p class="formula-text">公式: ({p} × {pay_r}%) + {ev}</p><p class="expense-tag">金流/活動費: -${shared_fee:,.0f}</p>
        <div class="total-fee-tag">手續費總計: -${tot2:,.0f}</div><hr>
        <div class="data-row"><span class="label-text">實拿金額:</span><span class="val-15 payout-color">${po2:,.0f}</span></div>
        <div class="data-row"><span class="label-text">預估毛利:</span><span class="val-15 profit-color">${po2-c:,.0f}</span></div>
        <hr style="border-top: 1px dashed #ccc;">
        <div class="data-row"><span class="label-text" style="color:gray;">不含{s_v_n}實拿:</span><span class="val-no-v">${po2_no_v:,.0f}</span></div>
        <div class="data-row"><span class="label-text" style="color:gray;">不含{s_v_n}毛利:</span><span class="val-no-v">${po2_no_v-c:,.0f}</span></div>
    </div>""", unsafe_allow_html=True)

with col_直:
    st.markdown(f"""<div class="result-card"><h3 class="title-直">蝦皮直送</h3>
        <p style="color:gray; font-size:0.8em;">直送判斷: {"手機/平板" if f_m == cfg_直_前毛_手機 else "其他"}<br>{s_cat_display}</p><hr>
        <p class="formula-text">公式: {p} × {f_m}%</p><p class="expense-tag">前毛手續費: -${tf3:,.0f}</p>
        <p class="formula-text">公式: {p} × {cfg_直_後毛}%</p><p class="expense-tag">後毛手續費: -${tb3:,.0f}</p>
        <div class="total-fee-tag">手續費總計: -${tot3:,.0f}</div><hr>
        <div class="data-row"><span class="label-text">實拿金額:</span><span class="val-15 payout-color">${po3:,.0f}</span></div>
        <div class="data-row"><span class="label-text">預估毛利:</span><span class="val-15 profit-color">${po3-c:,.0f}</span></div>
    </div>""", unsafe_allow_html=True)

# --- 7. 雲端同步與報表 (維持 V25.0 邏輯) ---
st.markdown("---")
if st.button("🚀 同步當前結果至 Google Sheets"):
    if gc:
        try:
            sh = gc.open(SPREADSHEET_NAME)
            ws = sh.get_worksheet(0)
            ws.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), staff_name, store_name, s_cat_display, p, c, po1-c])
            st.success("✅ 數據已成功同步！")
        except Exception as e:
            st.error(f"同步失敗: {e}")
    else:
        st.warning("⚠️ Google Sheets 未連線，請確認 Secrets 設定。")

st.markdown(f'<div class="table-header-green">📊 全品項分類毛利對照 (單價: ${p:,.0f} / 成本: ${c:,.0f})</div>', unsafe_allow_html=True)
# ... (維持原本的 df_compare 表格生成代碼)
