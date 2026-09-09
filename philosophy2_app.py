import io
import pandas as pd
import requests
import streamlit as st

# 화면 전체 넓게 쓰기
st.set_page_config(layout="wide")
st.subheader("📊 당일 실시간 시장 수급 동향")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
}

def get_market_data(url):
    res = requests.get(url, headers=headers)
    res.encoding = "euc-kr"
    tables = pd.read_html(io.StringIO(res.text))
    df = tables[1].dropna(subset=["종목명"])
    return df

# 코스피(0), 코스닥(1) 거래량 상위 데이터 수집
df_kospi = get_market_data("https://finance.naver.com/sise/sise_quant.naver?sosok=0")
df_kosdaq = get_market_data("https://finance.naver.com/sise/sise_quant.naver?sosok=1")
df = pd.concat([df_kospi, df_kosdaq])

# ETF/ETN 상품 필터링
etf_keywords = ['KODEX', 'TIGER', 'KBSTAR', 'ACE', 'SOL', 'HANARO', 'ARIRANG', 'KOSEF', '인버스', '레버리지', 'ETN']
df = df[~df['종목명'].str.contains('|'.join(etf_keywords), na=False)]

# 불필요한 열 삭제 및 숫자형 변환 (가로 스크롤 잘림 방지)
df = df[["종목명", "현재가", "등락률", "거래량", "거래대금"]]
for col in ["현재가", "거래량", "거래대금"]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 1. 거래량 기준 상위 20종목 정렬
df_vol = df.sort_values(by="거래량", ascending=False).head(20).reset_index(drop=True)
df_vol.index = df_vol.index + 1

# 2. 거래대금 기준 상위 20종목 정렬 (수집된 거래량 100위 명단 내에서 추출)
df_val = df.sort_values(by="거래대금", ascending=False).head(20).reset_index(drop=True)
df_val.index = df_val.index + 1

# 가독성을 위한 콤마(,) 포맷팅 세팅
format_dict = {"현재가": "{:,.0f}", "거래량": "{:,.0f}", "거래대금": "{:,.0f}"}

# 화면을 좌우 2개로 분할하여 출력
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔥 거래량 상위 20")
    st.dataframe(df_vol.style.format(format_dict), use_container_width=True)

with col2:
    st.markdown("### 💰 거래대금 상위 20 (거래량 Top100 기준)")
    st.dataframe(df_val.style.format(format_dict), use_container_width=True)
