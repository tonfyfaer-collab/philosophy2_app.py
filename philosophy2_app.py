import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. 페이지 기본 설정 및 디자인 테마
# ==========================================
st.set_page_config(page_title="재화의 프라이빗 사주 관제탑", layout="centered", page_icon="☯️")

# ==========================================
# 🔒 VIP 전용 비밀번호 출입 통제소
# ==========================================
st.title("🔒 철학 관제탑 출입 통제소")

pwd_input = st.text_input("접근 권한이 필요합니다. 비밀번호를 입력하세요:", type="password")

# 💡 기본 비밀번호: 1234 (원하시는 비밀번호로 변경 가능)
if pwd_input != "1234":
    st.warning("올바른 비밀번호를 입력해야 분석 엔진이 가동됩니다.")
    st.stop()  # 비밀번호 불일치 시 하단 화면 렌더링 완전 차단

# ==========================================
# 🔓 프라이빗 사주 분석 메인 관제탑 (비밀번호 통과 시 실행)
# ==========================================
st.divider()
st.title("☯️ 사주 명식 및 운세 관제탑")
st.subheader("사주 8글자(명식) 및 맞춤형 실천 비책 추출기")

# 한글 ↔ 한자 변환 매핑 사전
CHEONGAN_LIST = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
JIJI_LIST = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]

HANJA_CHEONGAN = {"갑": "甲", "을": "乙", "병": "丙", "정": "丁", "무": "戊", "기": "己", "경": "庚", "신": "辛", "임": "壬", "계": "癸"}
HANJA_JIJI = {"자": "子", "축": "丑", "인": "寅", "묘": "卯", "진": "辰", "사": "巳", "오": "午", "미": "未", "신": "申", "유": "酉", "술": "戌", "해": "亥"}

# ==========================================
# ⚡ 데이터베이스 캐싱 로더 (초고속 로딩 & 트래픽 방어)
# ==========================================
@st.cache_data(ttl=600)
def load_manse_db():
    # 100년 치 만세력 시트 CSV 주소
    manse_url = "https://docs.google.com/spreadsheets/d/1Fn-s98Yn1aJYRMy0_kbE0id4gDwMqkOD008qNsS3vyk/export?format=csv&gid=0"
    df = pd.read_csv(manse_url)
    df['양력'] = df['양력'].astype(str)
    df['음력'] = df['음력'].astype(str)
    return df

@st.cache_data(ttl=600)
def load_rules_db():
    # 220개 Saju_Rules 시트 CSV 주소
    rules_url = "https://docs.google.com/spreadsheets/d/1xWW9qUeDeppN7HsRh9hBq1zlWvLDCOLrpkUH2Jo2_k4/export?format=csv&gid=1543031817"
    df = pd.read_csv(rules_url)
    # 데이터 공백 제거 및 문자열 정제
    df['Daymaster'] = df['Daymaster'].astype(str).str.strip()
    df['Target_Word'] = df['Target_Word'].astype(str).str.strip()
    return df

# ==========================================
# 1. 정보 입력 인터페이스
# ==========================================
col1, col2, col3 = st.columns(3)
with col1:
    cal_type = st.selectbox("달력 기준", ["양력", "음력"])
with col2:
    birth_date = st.date_input("생년월일", value=pd.to_datetime("1975-01-01"), min_value=pd.to_datetime("1970-01-01"), max_value=pd.to_datetime("2070-12-31"))
with col3:
    time_options = [
        "모름 (시주 제외)", "자시 (23:30~01:29)", "축시 (01:30~03:29)", "인시 (03:30~05:29)",
        "묘시 (05:30~07:29)", "진시 (07:30~09:29)", "사시 (09:30~11:29)", "오시 (11:30~13:29)",
        "미시 (13:30~15:29)", "신시 (15:30~17:29)", "유시 (17:30~19:29)", "술시 (19:30~21:29)", "해시 (21:30~23:29)"
    ]
    birth_time = st.selectbox("태어난 시간", time_options)

# ==========================================
# 2. 분석 엔진 가동
# ==========================================
if st.button("🔍 사주 명식 및 실천 비책 도출"):
    with st.spinner("만세력 및 220개 명리 규칙 DB를 검색 중입니다..."):
        try:
            df_saju = load_manse_db()
            df_rules = load_rules_db()
            
            target_date_str = birth_date.strftime("%Y-%m-%d")
            
            # 양력/음력 검색
            if cal_type == "양력":
                result = df_saju[df_saju['양력'] == target_date_str]
            else:
                result = df_saju[df_saju['음력'].str.startswith(target_date_str)]
                
            if not result.empty:
                saju_row = result.iloc[0]
                year_pillar = saju_row['연주']
                month_pillar = saju_row['월주']
                day_pillar = saju_row['일주']
                
                # 3. 시간으로 '시주' 자동 계산 (시두법 공식 적용)
                time_pillar = "모름"
                if birth_time != "모름 (시주 제외)":
                    day_stem = day_pillar[0]  # 일간 (예: '경')
                    try:
                        day_stem_idx = CHEONGAN_LIST.index(day_stem)
                        time_jiji_char = birth_time[0]  # 시지 (예: '인')
                        time_jiji_idx = JIJI_LIST.index(time_jiji_char)
                        
                        stem_start_idx = (day_stem_idx % 5) * 2
                        time_stem_idx = (stem_start_idx + time_jiji_idx) % 10
                        
                        time_pillar = CHEONGAN_LIST[time_stem_idx] + time_jiji_char
                    except Exception:
                        time_pillar = "계산 오류"

                # 4. 운명의 8글자 UI 출력
                st.success("✅ 사주 명식 추출 성공!")
                
                st.markdown(f"""
                <div style="text-align: center; background-color: #1e1e2e; padding: 22px; border-radius: 12px; margin-bottom: 20px;">
                    <h3 style="color: #ECEFF4; margin-bottom: 15px;">운명의 8글자 (사주 원국)</h3>
                    <table style="width:100%; font-size:22px; color:white; text-align:center; border-collapse: collapse;">
                        <tr style="color: #88C0D0; border-bottom: 1px solid #4C566A;">
                            <th style="padding: 8px;">시주(시간)</th>
                            <th style="padding: 8px;">일주(본인)</th>
                            <th style="padding: 8px;">월주(사회/부모)</th>
                            <th style="padding: 8px;">연주(초년/조상)</th>
                        </tr>
                        <tr style="font-size:30px; font-weight:bold; color:#EBCB8B;">
                            <td style="padding: 12px;">{time_pillar}</td>
                            <td style="padding: 12px;">{day_pillar}</td>
                            <td style="padding: 12px;">{month_pillar}</td>
                            <td style="padding: 12px;">{year_pillar}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
                
                st.divider()

                # ==========================================
                # 5. Saju_Rules 연동: 일간 기준 운세 & 실천 비책(Action Guide)
                # ==========================================
                st.subheader("🔮 명리 분석 및 맞춤형 실천 비책 (Action Guide)")
                
                # 본인의 일간(천간) 추출 및 한자 변환
                my_day_stem_hangul = day_pillar[0]  # 예: '경'
                my_day_stem_hanja = HANJA_CHEONGAN.get(my_day_stem_hangul, my_day_stem_hangul) # 예: '庚'
                
                # Saju_Rules DB에서 일간 매칭
                # DB의 Daymaster 컬럼이 한자(庚) 또는 한글을 포함하는 경우 모두 대응
                user_rules = df_rules[df_rules['Daymaster'].str.contains(my_day_stem_hanja, na=False) | 
                                      df_rules['Daymaster'].str.contains(my_day_stem_hangul, na=False)]
                
                if not user_rules.empty:
                    # 분석하고 싶은 운(Target Word) 선택 UI
                    st.markdown(f"**본인의 일간(日干):** `{my_day_stem_hangul}({my_day_stem_hanja})`")
                    
                    # 2026년 세운 '병(丙)'을 기본 타겟으로 설정하고, 다른 글자도 탐색 가능하게 구성
                    available_targets = user_rules['Target_Word'].unique().tolist()
                    default_idx = 0
                    for idx, tw in enumerate(available_targets):
                        if "丙" in tw or "병" in tw:
                            default_idx = idx
                            break
                            
                    selected_target = st.selectbox("📌 분석하고 싶은 운의 글자(세운/월운/원국) 선택:", available_targets, index=default_idx)
                    
                    # 선택된 글자의 규칙 추출
                    matched_rule = user_rules[user_rules['Target_Word'] == selected_target].iloc[0]
                    
                    # 등급에 따른 뱃지 색상
                    grade = matched_rule['Fortune_Grade']
                    sipsin = matched_rule['Sipsin_Relation']
                    
                    st.info(f"**[조우한 기운]:** {selected_target} ({sipsin})  |  **[길흉 등급]:** {grade}")
                    
                    # 💡 핵심 해설 (Core Interpretation)
                    st.markdown("#### 📖 핵심 심리 및 환경 변화")
                    st.write(matched_rule['Core_Interpretation'])
                    
                    # 🚀 구체적 실천 지침 (Action Guide) - 인터랙티브 버튼/확장기
                    st.markdown("#### 🎯 행동 전략 지침")
                    with st.expander("👉 클릭하여 오늘 내가 취해야 할 '구체적 실천 비책' 확인하기", expanded=True):
                        st.success(f"**실천 가이드:**\n\n{matched_rule['Action_Guide']}")
                        
                else:
                    st.warning(f"일간 '{my_day_stem_hangul}({my_day_stem_hanja})'에 대한 Saju_Rules 데이터를 찾지 못했습니다. 시트의 Daymaster 컬럼 값을 확인해 주세요.")

            else:
                st.error("해당 날짜의 만세력 데이터를 찾을 수 없습니다. (1970~2070 범위 확인 필요)")
        except Exception as e:
            st.error(f"데이터베이스 조회 중 오류가 발생했습니다: {e}")
