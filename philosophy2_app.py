import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. 페이지 기본 설정 (프라이빗 모드)
# ==========================================
st.set_page_config(page_title="재화의 프라이빗 사주 관제탑", layout="centered")

# ==========================================
# 🔒 VIP 전용 비밀번호 출입 통제소
# ==========================================
st.title("🔒 철학 관제탑 출입 통제소")

# type="password" 옵션으로 비밀번호가 가려집니다.
pwd_input = st.text_input("접근 권한이 필요합니다. 비밀번호를 입력하세요:", type="password")

# 💡 기본 비밀번호는 1234로 설정되어 있습니다. 원하시는 숫자로 변경 가능합니다.
if pwd_input != "1234":
    st.warning("올바른 비밀번호를 입력해야 분석 엔진이 가동됩니다.")
    st.stop() # 비밀번호가 틀리면 여기서 화면을 완전히 차단합니다.

# ==========================================
# 🔓 프라이빗 사주 분석 메인 화면 (비밀번호 통과 시 등장)
# ==========================================
st.divider()
st.title("☯️ 사주 명식 및 운세 관제탑")
st.subheader("사주 8글자(명식) 추출기")

# 1. 정보 입력창
col1, col2, col3 = st.columns(3)
with col1:
    cal_type = st.selectbox("달력 기준", ["양력", "음력"])
with col2:
    # 달력을 넘기기 편하시도록 기본 시작 연도를 1975년으로 세팅해 두었습니다.
    birth_date = st.date_input("생년월일", value=pd.to_datetime("1975-01-01"), min_value=pd.to_datetime("1970-01-01"), max_value=pd.to_datetime("2070-12-31"))
with col3:
    # 시주를 계산하기 위한 시간 선택창
    time_options = [
        "모름 (시주 제외)", "자시 (23:30~01:29)", "축시 (01:30~03:29)", "인시 (03:30~05:29)",
        "묘시 (05:30~07:29)", "진시 (07:30~09:29)", "사시 (09:30~11:29)", "오시 (11:30~13:29)",
        "미시 (13:30~15:29)", "신시 (15:30~17:29)", "유시 (17:30~19:29)", "술시 (19:30~21:29)", "해시 (21:30~23:29)"
    ]
    birth_time = st.selectbox("태어난 시간", time_options)

# 2. 분석 엔진 가동
if st.button("🔍 사주 명식 뽑기"):
    with st.spinner("만세력 데이터베이스를 검색 중입니다..."):
        try:
            # 💡 [필승 치트키] 복잡한 Connection 라이브러리 대신, 구글 시트의 데이터를 직접 가져옵니다.
            # edit?gid=0 부분을 export?format=csv&gid=0 으로 바꾸면 파이썬이 즉시 읽을 수 있습니다!
            csv_url = "https://docs.google.com/spreadsheets/d/1Fn-s98Yn1aJYRMy0_kbE0id4gDwMqkOD008qNsS3vyk/export?format=csv&gid=0"
            
            # Pandas로 0.1초만에 다이렉트로 읽어오기
            df_saju = pd.read_csv(csv_url)
            
            # 날짜 데이터 문자열 변환 (안전장치)
            df_saju['양력'] = df_saju['양력'].astype(str)
            df_saju['음력'] = df_saju['음력'].astype(str)
            
            # 날짜 포맷 맞추기
            target_date_str = birth_date.strftime("%Y-%m-%d")
            
            # 달력 기준에 따라 구글 시트에서 검색
            if cal_type == "양력":
                result = df_saju[df_saju['양력'] == target_date_str]
            else:
                result = df_saju[df_saju['음력'].str.startswith(target_date_str)]
            
            if not result.empty:
                saju_row = result.iloc[0]
                year_pillar = saju_row['연주']
                month_pillar = saju_row['월주']
                day_pillar = saju_row['일주']
                
                # 3. 시간으로 '시주' 자동 계산 로직 (시두법 적용)
                time_pillar = "모름"
                if birth_time != "모름 (시주 제외)":
                    CHEONGAN = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
                    JIJI = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
                    
                    day_stem = day_pillar[0]
                    try:
                        day_stem_idx = CHEONGAN.index(day_stem)
                        time_jiji_char = birth_time[0]
                        time_jiji_idx = JIJI.index(time_jiji_char)
                        
                        stem_start_idx = (day_stem_idx % 5) * 2
                        time_stem_idx = (stem_start_idx + time_jiji_idx) % 10
                        
                        time_pillar = CHEONGAN[time_stem_idx] + time_jiji_char
                    except Exception as e:
                        time_pillar = "계산 오류"

                # 4. 결과 출력
                st.success("✅ 사주 명식 추출 완료!")
                
                # 사주는 오른쪽(연주)부터 왼쪽(시주)으로 읽는 것이 전통 방식입니다.
                st.markdown(f"""
                <div style="text-align: center; background-color: #1e1e2e; padding: 20px; border-radius: 10px;">
                    <h3 style="color: white;">운명의 8글자</h3>
                    <table style="width:100%; font-size:24px; color:white; text-align:center;">
                        <tr>
                            <th>시주(시간)</th>
                            <th>일주(본인)</th>
                            <th>월주(부모/사회)</th>
                            <th>연주(조상/초년)</th>
                        </tr>
                        <tr style="font-size:32px; font-weight:bold; color:#FFD700;">
                            <td>{time_pillar}</td>
                            <td>{day_pillar}</td>
                            <td>{month_pillar}</td>
                            <td>{year_pillar}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.error("해당 날짜의 만세력 데이터를 찾을 수 없습니다.")
        except Exception as e:
            st.error(f"만세력 데이터를 불러오는 데 실패했습니다: {e}")
