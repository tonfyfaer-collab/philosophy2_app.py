import io
import pandas as pd
import requests
import streamlit as st

# 1. 화면 전체 넓게 쓰기 (반드시 최상단 위치)
st.set_page_config(layout="wide")

# 2. 화면 제목 추가
st.subheader("📊 당일 거래대금 상위 20 종목 (코스피+코스닥 주식)")

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# 데이터 수집 자동화 함수
def get_market_data(url):
    res = requests.get(url, headers=headers)
    res.encoding = "euc-kr"
    tables = pd.read_html(io.StringIO(res.text))
    df = tables[1].dropna(subset=["종목명"])
    return df

# 3. 코스피(0)와 코스닥(1) '거래대금 상위' 데이터 각각 수집
df_kospi = get_market_data("https://finance.naver.com/sise/sise_quant_high.naver?sosok=0")
df_kosdaq = get_market_data("https://finance.naver.com/sise/sise_quant_high.naver?sosok=1")

# 4. 두 시장 데이터 병합
df = pd.concat([df_kospi, df_kosdaq])

# 5. ETF/ETN 상품 필터링 (주식만 남기기)
etf_keywords = ['KODEX', 'TIGER', 'KBSTAR', 'ACE', 'SOL', 'HANARO', 'ARIRANG', 'KOSEF', '인버스', '레버리지', 'ETN']
df = df[~df['종목명'].str.contains('|'.join(etf_keywords), na=False)]

# 6. 거래대금 기준으로 내림차순 정렬 후 상위 20개 추출
df["거래대금"] = pd.to_numeric(df["거래대금"], errors='coerce')
df = df.sort_values(by="거래대금", ascending=False).head(20)

# 7. 보기 좋게 표 인덱스(순위) 정리
top20 = df[["종목명", "현재가", "전일비", "등락률", "거래량", "거래대금", "매수호가", "매도호가"]].reset_index(drop=True)
top20.index = top20.index + 1  # 0이 아닌 1위부터 시작하도록 조정

# 8. 화면 출력
st.dataframe(top20, use_container_width=True)
