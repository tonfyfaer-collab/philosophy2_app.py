import io  # 1. io 모듈 추가
import pandas as pd
import requests
import streamlit as st

# 2. 네이버페이 증권 데이터 요청
url = "https://finance.naver.com/sise/sise_quant.naver?sosok=0"
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

res = requests.get(url, headers=headers)
res.encoding = "euc-kr"

# 3. io.StringIO로 감싸서 전달 (FileNotFoundError 해결)
tables = pd.read_html(io.StringIO(res.text))
df = tables[1]

# 4. 결측치 정리 및 상위 종목 추출
df = df.dropna(subset=["종목명"])
top20 = df[
    [
        "N",
        "종목명",
        "현재가",
        "전일비",
        "등락률",
        "거래량",
        "거래대금",
        "매수호가",
        "매도호가",
    ]
].head(20)

st.dataframe(top20, use_container_width=True)import pandas as pd
import requests

# 1. 네이버페이 증권 거래량 상위 20 종목 수집 (KOSPI 기준)
url = "https://finance.naver.com/sise/sise_quant.naver?sosok=0"  # sosok=0: 코스피, sosok=1: 코스닥
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

res = requests.get(url, headers=headers)
res.encoding = "euc-kr"

# 2. HTML 내 테이블 추출
tables = pd.read_html(res.text)
df = tables[1]  # 시세 데이터가 담긴 메인 테이블

# 3. 결측치 제거 및 상위 20개 추출
df = df.dropna(subset=["종목명"])
df = df[
    [
        "N",
        "종목명",
        "현재가",
        "전일비",
        "등락률",
        "거래량",
        "거래대금",
        "매수호가",
        "매도호가",
    ]
]
top20 = df.head(20).reset_index(drop=True)

# 4. 결과 출력
display(top20)
