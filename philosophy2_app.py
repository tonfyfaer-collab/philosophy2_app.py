import io
import pandas as pd
import requests
import streamlit as st

# 화면 전체 너비 활용
st.set_page_config(layout="wide")
st.subheader("📊 당일 실시간 시장 수급 동향")

# 네이버 증권 차단 방지를 위한 브라우저 헤더 보강
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Referer": "https://finance.naver.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}

@st.cache_data(ttl=60)  # 1분 단위 캐시: 반복 호출로 인한 IP 차단 방지
def get_market_data(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.encoding = "euc-kr"
        
        # HTML 테이블 파싱
        tables = pd.read_html(io.StringIO(res.text))
        
        # 테이블 유효성 검사 (보통 1번 인덱스가 메인 시세 테이블)
        for t in tables:
            if "종목명" in t.columns:
                df = t.dropna(subset=["종목명"]).copy()
                return df
        return pd.DataFrame()
    except Exception as e:
        st.warning(f"데이터 수집 중 일시적 지연 발생: {e}")
        return pd.DataFrame()

# 데이터 수집 (코스피: 0, 코스닥: 1)
df_kospi = get_market_data("https://finance.naver.com/sise/sise_quant.naver?sosok=0")
df_kosdaq = get_market_data("https://finance.naver.com/sise/sise_quant.naver?sosok=1")

df = pd.concat([df_kospi, df_kosdaq], ignore_index=True)

if not df.empty and "종목명" in df.columns:
    # 1. ETF / ETN 종목 필터링
    etf_keywords = ['KODEX', 'TIGER', 'KBSTAR', 'ACE', 'SOL', 'HANARO', 'ARIRANG', 'KOSEF', '인버스', '레버리지', 'ETN']
    df = df[~df['종목명'].str.contains('|'.join(etf_keywords), na=False)]

    # 2. 필요한 열 선택 및 숫자 변환
    target_cols = ["종목명", "현재가", "등락률", "거래량", "거래대금"]
    available_cols = [c for c in target_cols if c in df.columns]
    df = df[available_cols]

    for col in ["현재가", "거래량", "거래대금"]:
        if col in df.columns:
            # 쉼표 제거 및 숫자 변환
            df[col] = df[col].astype(str).str.replace(",", "")
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3. 거래량 상위 20
    df_vol = df.sort_values(by="거래량", ascending=False).head(20).reset_index(drop=True)
    df_vol.index = df_vol.index + 1

    # 4. 거래대금 상위 20
    df_val = df.sort_values(by="거래대금", ascending=False).head(20).reset_index(drop=True)
    df_val.index = df_val.index + 1

    # 숫자 포맷팅 (천 단위 콤마)
    format_dict = {}
    for col in ["현재가", "거래량", "거래대금"]:
        if col in df.columns:
            format_dict[col] = "{:,.0f}"

    # 화면 2분할 출력
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔥 거래량 상위 20")
        st.dataframe(df_vol.style.format(format_dict), use_container_width=True)

    with col2:
        st.markdown("### 💰 거래대금 상위 20 (거래량 상위 내)")
        st.dataframe(df_val.style.format(format_dict), use_container_width=True)
else:
    st.info("현재 네이버 증권 데이터를 불러오는 중입니다. 잠시 후 새로고침(R)을 눌러주세요.")
