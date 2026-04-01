import streamlit as st
import feedparser
import yfinance as yf

# 1. ページ全体の設定（横に広く使う設定）
st.set_page_config(layout="wide", page_title="経済・投資ダッシュボード")

# 2. 参考サイト風のダークモード＆カードデザインを適用（CSS）
st.markdown("""
<style>
    /* 全体の背景を黒っぽく */
    .stApp {
        background-color: #121212;
        color: #ffffff;
    }
    /* 指標を表示するカード（枠）のデザイン */
    div[data-testid="metric-container"] {
        background-color: #1e1e1e;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 世界の主要株価指数・ダッシュボード")
st.markdown("---")

# 3. 経済指標の取得と表示セクション
st.header("🌎 主要指数・為替")

# 取得するティッカーシンボル（yfinance用）
tickers = {
    "日経平均": "^N225",
    "NYダウ": "^DJI",
    "ナスダック": "^IXIC",
    "S&P 500": "^GSPC",
    "米ドル/円": "JPY=X",
    "ユーロ/円": "EURJPY=X",
    "WTI原油": "CL=F",
    "VIX恐怖指数": "^VIX"
}

# データをキャッシュして読み込みを高速化（5分間保持）
@st.cache_data(ttl=300)
def get_market_data():
    data = {}
    for name, ticker in tickers.items():
        try:
            # 休日などを考慮して直近5日分のデータを取得し、最新2日分を比較
            hist = yf.Ticker(ticker).history(period="5d")
            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[-2]
                diff = current - previous
                diff_pct = (diff / previous) * 100
                data[name] = {"current": current, "diff": diff, "diff_pct": diff_pct}
        except Exception:
            pass
    return data

market_data = get_market_data()

# 4列に並べて表示するためのレイアウト作成
cols = st.columns(4)

col_idx = 0
for name, data in market_data.items():
    with cols[col_idx % 4]:
        # delta_color="inverse" を指定することで「プラスが赤、マイナスが緑」の日本式になります
        st.metric(
            label=name, 
            value=f"{data['current']:,.2f}", 
            delta=f"{data['diff']:,.2f} ({data['diff_pct']:,.2f}%)",
            delta_color="inverse" 
        )
    col_idx += 1

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

# 4. 経済ニュースの表示セクション（前回と同様）
st.header("📰 最新の経済ニュース")
st.write("Yahoo!ニュース（経済）から最新情報を取得しています。")

RSS_URL = "https://news.yahoo.co.jp/rss/topics/business.xml"
feed = feedparser.parse(RSS_URL)

for entry in feed.entries[:5]:
    st.markdown(f"- [{entry.title}]({entry.link})")
