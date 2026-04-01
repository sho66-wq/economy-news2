import streamlit as st
import feedparser
import yfinance as yf
import pandas as pd

# ページのタイトル
st.title("📈 経済・投資ダッシュボード")

st.markdown("---")

# 1. 経済ニュースの表示セクション
st.header("📰 最新の経済ニュース")
st.write("Yahoo!ニュース（経済）から最新情報を取得しています。")

# Yahoo!ニュースの経済カテゴリのRSS URL
RSS_URL = "https://news.yahoo.co.jp/rss/topics/business.xml"
feed = feedparser.parse(RSS_URL)

# 最新のニュースを5件表示
for entry in feed.entries[:5]:
    st.markdown(f"- [{entry.title}]({entry.link})")

st.markdown("---")

# 2. 株価チャートの表示セクション
st.header("📊 気になる銘柄の株価チャート")

# ユーザーがティッカーシンボルを入力できるボックス（デフォルトは三菱重工業）
ticker_input = st.text_input("ティッカーシンボルを入力してください（例: トヨタは 7203.T、Appleは AAPL）", "7011.T")

if ticker_input:
    try:
        # yfinanceでデータを取得（過去1ヶ月分）
        stock_data = yf.Ticker(ticker_input)
        hist = stock_data.history(period="1mo")
        
        if not hist.empty:
            st.write(f"**{ticker_input} の直近1ヶ月の終値推移**")
            # Streamlitの標準機能で折れ線グラフを描画
            st.line_chart(hist['Close'])
        else:
            st.warning("データが見つかりませんでした。正しいティッカーシンボルを入力してください。")
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
