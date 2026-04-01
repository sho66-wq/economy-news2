import streamlit as st
import yfinance as yf
import pandas as pd

# 1. ページ全体の設定
st.set_page_config(layout="wide", page_title="リアルタイム指標ダッシュボード")

# 2. 画像のデザインを再現するためのカスタムCSS
st.markdown("""
<style>
    /* テーブル全体のデザイン（白背景ベース） */
    .metric-table {
        width: 100%;
        border-collapse: collapse;
        font-family: sans-serif;
        background-color: #ffffff;
        color: #333333;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .metric-table th, .metric-table td {
        border: 1px solid #dcdcdc;
        padding: 10px 8px;
        text-align: right;
        vertical-align: middle;
    }
    .metric-table th {
        background-color: #fcefb4;
        text-align: center;
        font-size: 14px;
        font-weight: bold;
    }
    /* 銘柄名カラム（左寄せ、濃いグレー背景） */
    .name-col {
        text-align: left !important;
        font-weight: bold;
        background-color: #4a4a4a;
        color: #ffffff;
        padding-left: 12px !important;
        font-size: 16px;
    }
    /* 数値のフォントサイズ */
    .val-col { font-size: 20px; font-weight: bold; }
    /* 上昇（緑）と下落（赤）のデザイン */
    .up { color: #008000; font-weight: bold; background-color: #eafaea; }
    .down { color: #ff0000; font-weight: bold; background-color: #faeaea; }
    .flat { color: #333; font-weight: bold; }
    /* 高値・安値の小さな文字 */
    .hl-col { font-size: 12px; color: #888; text-align: right; line-height: 1.2; }
</style>
""", unsafe_allow_html=True)

st.title("📊 リアルタイム 経済指標一覧")

# 3. 取得するティッカーシンボルと表示名の定義
tickers_info = {
    "^N225": ("日経平均株価", "🇯🇵"),
    "1306.T": ("TOPIX (※ETF連動)", "🇯🇵"),
    "1591.T": ("JPX日経400 (※ETF連動)", "🇯🇵"),
    "2516.T": ("グロース250 (※ETF連動)", "🇯🇵"),
    "JPY=X": ("為替 ドル円", "🇺🇸"),
    "EURJPY=X": ("為替 ユーロ円", "🇪🇺"),
    "NIY=F": ("先物 日経平均", "🇯🇵"),
    "^JN09": ("日本国債10年利回り", "🇯🇵"),
    "^JNIV": ("日経VI (恐怖指数)", "💀"),
    "1343.T": ("東証REIT (※ETF連動)", "🇯🇵")
}

# 4. データ取得関数（60秒間キャッシュして制限エラーを防ぐ）
@st.cache_data(ttl=60)
def fetch_data():
    data = []
    for ticker, (name, flag) in tickers_info.items():
        try:
            tkr = yf.Ticker(ticker)
            hist = tkr.history(period="5d")
            if len(hist) >= 2:
                curr = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                high = hist['High'].iloc[-1]
                low = hist['Low'].iloc[-1]
                
                diff = curr - prev
                pct = (diff / prev) * 100
                data.append({
                    "ticker": ticker, "name": name, "flag": flag,
                    "curr": curr, "diff": diff, "pct": pct, "high": high, "low": low
                })
        except:
            pass
    return data

market_data = fetch_data()

# 5. NT倍率とドル建て日経平均の自動計算
n225 = next((item for item in market_data if item["ticker"] == "^N225"), None)
topix = next((item for item in market_data if item["ticker"] == "1306.T"), None)
usdjpy = next((item for item in market_data if item["ticker"] == "JPY=X"), None)

if n225 and topix:
    nt_ratio = n225["curr"] / topix["curr"]
    prev_nt = (n225["curr"] - n225["diff"]) / (topix["curr"] - topix["diff"])
    diff_nt = nt_ratio - prev_nt
    pct_nt = (diff_nt / prev_nt) * 100
    market_data.append({"ticker": "NT", "name": "NT倍率 (ETF基準)", "flag": "🇯🇵", "curr": nt_ratio, "diff": diff_nt, "pct": pct_nt, "high": nt_ratio, "low": nt_ratio})

if n225 and usdjpy:
    dol_nikkei = n225["curr"] / usdjpy["curr"]
    prev_dol = (n225["curr"] - n225["diff"]) / (usdjpy["curr"] - usdjpy["diff"])
    diff_dol = dol_nikkei - prev_dol
    pct_dol = (diff_dol / prev_dol) * 100
    market_data.append({"ticker": "USD_N225", "name": "ドル建て日経平均", "flag": "🇯🇵", "curr": dol_nikkei, "diff": diff_dol, "pct": pct_dol, "high": dol_nikkei, "low": dol_nikkei})

# 6. HTMLテーブルの生成
html = '<table class="metric-table">'
html += '<tr><th>銘柄</th><th>現在値</th><th>前日比</th><th>前日比%</th><th>高値 / 安値</th></tr>'

for item in market_data:
    name_str = f"{item['flag']} {item['name']}"
    
    # 為替や利回りは小数点以下3桁、それ以外は2桁に調整
    is_fx_or_yield = "為替" in item["name"] or "利回り" in item["name"] or "倍率" in item["name"]
    decimals = 3 if is_fx_or_yield else 2
    
    curr_str = f"{item['curr']:,.{decimals}f}"
    diff_str = f"{item['diff']:+,.{decimals}f}"
    pct_str = f"{item['pct']:+,.2f}%"
    high_str = f"H: {item['high']:,.{decimals}f}"
    low_str = f"L: {item['low']:,.{decimals}f}"
    
    # プラスマイナスで色と矢印を分岐
    css_class = "up" if item['diff'] > 0 else "down" if item['diff'] < 0 else "flat"
    sign_arrow = "▲" if item['diff'] > 0 else "▼" if item['diff'] < 0 else ""
    
    # 【修正点】改行をなくして1行に繋げました
    html += f'<tr><td class="name-col">{name_str}</td><td class="val-col">{curr_str}</td><td class="{css_class}">{diff_str}</td><td class="{css_class}">{sign_arrow}{pct_str}</td><td class="hl-col">{high_str}<br>{low_str}</td></tr>'

html += '</table>'

# 【修正点】st.write から st.markdown に変更し、確実にHTMLとしてレンダリングさせます
st.markdown(html, unsafe_allow_html=True)
