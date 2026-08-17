import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. 페이지 설정 및 VIP 출입 통제
# ==========================================
st.set_page_config(page_title="재화의 프라이빗 사주 관제탑", layout="centered", page_icon="☯️")

st.title("🔒 철학 관제탑 출입 통제소")
pwd_input = st.text_input("접근 권한이 필요합니다. 비밀번호를 입력하세요:", type="password")

if pwd_input != "1234":
    st.warning("올바른 비밀번호를 입력해야 분석 엔진이 가동됩니다.")
    st.stop()

st.divider()
st.title("☯️ 사주 명식 및 연도별 자동 운세 관제탑")
st.subheader("사주 8글자 원국 도출 및 연도별 실천 비책(Action Guide) 자동 분석")

CHEONGAN_LIST = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
JIJI_LIST = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
HANJA_CHEONGAN = {"갑": "甲", "을": "乙", "병": "丙", "정": "丁", "무": "戊", "기": "己", "경": "庚", "신": "辛", "임": "壬", "계": "癸"}

# 연도별 세운 간지 매핑 데이터베이스
YEAR_GANJI = {
    2024: {"ganji": "갑진(甲辰)년", "stem": "甲", "branch": "辰"},
    2025: {"ganji": "을사(乙巳)년", "stem": "乙", "branch": "巳"},
    2026: {"ganji": "병오(丙午)년", "stem": "丙", "branch": "午"},
    2027: {"ganji": "정미(丁未)년", "stem": "丁", "branch": "未"},
    2028: {"ganji": "무신(戊申)년", "stem": "戊", "branch": "申"},
    2029: {"ganji": "기유(己酉)년", "stem": "己", "branch": "酉"},
    2030: {"ganji": "경술(庚戌)년", "stem": "庚", "branch": "戌"}
}

@st.cache_data(ttl=600)
def load_manse_db():
    manse_url = "https://docs.google.com/spreadsheets/d/1Fn-s98Yn1aJYRMy0_kbE0id4gDwMqkOD008qNsS3vyk/export?format=csv&gid=0"
    df = pd.read_csv(manse_url)
    df['양력'] = df['양력'].astype(str)
    df['음력'] = df['음력'].astype(str)
    return df

@st.cache_data(ttl=600)
def load_rules_db():
    rules_url = "https://docs.google.com/spreadsheets/d/1xWW9qUeDeppN7HsRh9hBq1zlWvLDCOLrpkUH2Jo2_k4/export?format=csv&gid=1543031817"
    df = pd.read_csv(rules_url)
    df['Daymaster'] = df['Daymaster'].astype(str).str.strip()
    df['Target_Word'] = df['Target_Word'].astype(str).str.strip()
    return df

if 'saju_calculated' not in st.session_state:
    st.session_state.saju_calculated = False
if 'saju_data' not in st.session_state:
    st.session_state.saju_data = {}

# 1. 입력 인터페이스
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

if st.button("🔍 사주 명식 및 운세 분석 시작"):
    with st.spinner("만세력 데이터를 조회 중입니다..."):
        try:
            df_saju = load_manse_db()
            target_date_str = birth_date.strftime("%Y-%m-%d")
            
            if cal_type == "양력":
                result = df_saju[df_saju['양력'] == target_date_str]
            else:
                result = df_saju[df_saju['음력'].str.startswith(target_date_str)]
                
            if not result.empty:
                saju_row = result.iloc[0]
                year_p = saju_row['연주']
                month_p = saju_row['월주']
                day_p = saju_row['일주']
                
                time_p = "모름"
                if birth_time != "모름 (시주 제외)":
                    day_stem = day_p[0]
                    try:
                        day_stem_idx = CHEONGAN_LIST.index(day_stem)
                        time_jiji_char = birth_time[0]
                        time_jiji_idx = JIJI_LIST.index(time_jiji_char)
                        stem_start_idx = (day_stem_idx % 5) * 2
                        time_stem_idx = (stem_start_idx + time_jiji_idx) % 10
                        time_p = CHEONGAN_LIST[time_stem_idx] + time_jiji_char
                    except:
                        time_p = "계산 오류"

                st.session_state.saju_data = {
                    "year": year_p,
                    "month": month_p,
                    "day": day_p,
                    "time": time_p,
                    "day_stem_hangul": day_p[0],
                    "day_stem_hanja": HANJA_CHEONGAN.get(day_p[0], day_p[0])
                }
                st.session_state.saju_calculated = True
            else:
                st.error("해당 날짜의 만세력 데이터를 찾을 수 없습니다.")
                st.session_state.saju_calculated = False
        except Exception as e:
            st.error(f"만세력 로딩 오류: {e}")

# ==========================================
# 2. 결과 출력 및 연도별 자동 운세 분석
# ==========================================
if st.session_state.saju_calculated:
    sdata = st.session_state.saju_data
    
    st.success("✅ 사주 원국 분석 완료!")
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
                <td style="padding: 12px;">{sdata['time']}</td>
                <td style="padding: 12px;">{sdata['day']}</td>
                <td style="padding: 12px;">{sdata['month']}</td>
                <td style="padding: 12px;">{sdata['year']}</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    # ==========================================
    # 🌟 연도별 전자동 운세 분석 코칭 시스템
    # ==========================================
    st.subheader("🔮 연도별(세운) 전자동 운세 및 실천 비책 (Action Guide)")
    
    my_hangul = sdata['day_stem_hangul']
    my_hanja = sdata['day_stem_hanja']
    
    st.markdown(f"👤 **분석 대상 일간(나의 본원):** `{my_hangul} ({my_hanja}金)`")
    
    try:
        df_rules = load_rules_db()
        
        # 사용자가 연도만 고르면 시스템이 자동 연산!
        year_options = [f"{y}년 - {info['ganji']}" for y, info in YEAR_GANJI.items()]
        # 기본 선택을 2026년(index=2)으로 자동 설정
        selected_year_label = st.selectbox(
            "📅 운세를 분석할 연도를 선택하세요 (시스템이 천간/지지를 자동 분석합니다):",
            options=year_options,
            index=2,
            key="auto_year_selector"
        )
        
        selected_year_num = int(selected_year_label.split("년")[0])
        year_info = YEAR_GANJI[selected_year_num]
        
        stem_char = year_info['stem']     # 천간 (예: 丙)
        branch_char = year_info['branch'] # 지지 (예: 午)
        
        # 1. 천간(하늘의 운) 규칙 조회
        rule_stem = df_rules[
            (df_rules['Daymaster'].str.contains(my_hanja, na=False) | df_rules['Daymaster'].str.contains(my_hangul, na=False)) &
            (df_rules['Target_Word'].str.contains(stem_char, na=False))
        ]
        
        # 2. 지지(땅의 환경) 규칙 조회
        rule_branch = df_rules[
            (df_rules['Daymaster'].str.contains(my_hanja, na=False) | df_rules['Daymaster'].str.contains(my_hangul, na=False)) &
            (df_rules['Target_Word'].str.contains(branch_char, na=False))
        ]
        
        st.markdown(f"### 🚩 {selected_year_num}년 {year_info['ganji']} 총합 운세 리포트")
        
        tab1, tab2 = st.tabs(["🌤️ 1. 하늘의 기운 (명예·사회적 목표)", "🌍 2. 땅의 환경 (현실·활동 영역)"])
        
        with tab1:
            if not rule_stem.empty:
                r_s = rule_stem.iloc[0]
                st.markdown(f"""
                <div style="background-color: #2e3440; padding: 16px; border-radius: 10px; border-left: 6px solid #88c0d0; margin-bottom: 12px;">
                    <b>[천간 작용]</b> {stem_char} 기운과 조우 ➔ <b>{r_s['Sipsin_Relation']}</b> 작용 발생 | <b>길흉:</b> <span style="color:#ebcb8b;">{r_s['Fortune_Grade']}</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("##### 📖 핵심 심리 및 환경 변화")
                st.info(r_s['Core_Interpretation'])
                st.markdown("##### 🎯 실행해야 할 행동 전략 비책")
                st.success(f"**[Action Guide]:**\n\n{r_s['Action_Guide']}")
            else:
                st.warning("천간 규칙 데이터를 찾을 수 없습니다.")
                
        with tab2:
            if not rule_branch.empty:
                r_b = rule_branch.iloc[0]
                st.markdown(f"""
                <div style="background-color: #2e3440; padding: 16px; border-radius: 10px; border-left: 6px solid #a3be8c; margin-bottom: 12px;">
                    <b>[지지 작용]</b> {branch_char} 기운과 조우 ➔ <b>{r_b['Sipsin_Relation']}</b> 작용 발생 | <b>길흉:</b> <span style="color:#ebcb8b;">{r_b['Fortune_Grade']}</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("##### 📖 현실적 환경 변화 해설")
                st.info(r_b['Core_Interpretation'])
                st.markdown("##### 🎯 현실 기반 행동 전략 비책")
                st.success(f"**[Action Guide]:**\n\n{r_b['Action_Guide']}")
            else:
                st.warning("지지 규칙 데이터를 찾을 수 없습니다.")
                
    except Exception as e:
        st.error(f"운세 데이터 자동 매칭 중 오류 발생: {e}")
