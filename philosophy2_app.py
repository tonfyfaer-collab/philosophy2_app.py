import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="재화의 프라이빗 사주 관제탑", layout="centered", page_icon="☯️")

# VIP 비밀번호 출입문
st.title("🔒 철학 관제탑 출입 통제소")
pwd_input = st.text_input("접근 권한이 필요합니다. 비밀번호를 입력하세요:", type="password")

if pwd_input != "1234":
    st.warning("올바른 비밀번호를 입력해야 분석 엔진이 가동됩니다.")
    st.stop()

st.divider()
st.title("☯️ 사주 명식 및 맞춤형 코칭 관제탑")
st.subheader("사주 8글자 원국 분석 및 Saju_Rules 실천 비책 스캐너")

CHEONGAN_LIST = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
JIJI_LIST = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
HANJA_CHEONGAN = {"갑": "甲", "을": "乙", "병": "丙", "정": "丁", "무": "戊", "기": "己", "경": "庚", "신": "辛", "임": "壬", "계": "癸"}

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

# 입력창
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
    with st.spinner("데이터를 조회 중입니다..."):
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

    st.subheader("🔮 시점별(세운/월운) 맞춤형 실천 비책 (Action Guide)")
    
    my_hangul = sdata['day_stem_hangul']
    my_hanja = sdata['day_stem_hanja']
    
    st.markdown(f"👤 **분석 대상 본인(일간):** `{my_hangul} ({my_hanja}金)`")
    
    try:
        df_rules = load_rules_db()
        
        user_rules = df_rules[df_rules['Daymaster'].str.contains(my_hanja, na=False) | 
                              df_rules['Daymaster'].str.contains(my_hangul, na=False)]
        
        if not user_rules.empty:
            target_list = user_rules['Target_Word'].tolist()
            
            # 2026년 병(丙) 기본 선택
            default_index = 0
            for idx, t in enumerate(target_list):
                if "병" in t or "丙" in t:
                    default_index = idx
                    break
            
            # 글자가 선명하게 보이도록 selectbox 적용
            selected_target = st.selectbox(
                "🎯 분석하고 싶은 운의 글자(10천간 / 12지지)를 선택하세요:",
                options=target_list,
                index=default_index,
                key="selected_target_word"
            )
            
            matched = user_rules[user_rules['Target_Word'] == selected_target].iloc[0]
            grade = matched['Fortune_Grade']
            sipsin = matched['Sipsin_Relation']
            
            st.markdown(f"""
            <div style="background-color: #2e3440; padding: 16px; border-radius: 10px; border-left: 6px solid #88c0d0; margin: 15px 0;">
                <b style="font-size: 17px; color: #ECEFF4;">[시점 분석 요약]</b><br>
                • 내 일간 <b>{my_hangul}({my_hanja})</b>이 운에서 <b>{selected_target}</b> 기운을 만났을 때 ➔ <span style="color: #81a1c1; font-weight: bold;">{sipsin}</span> 작용 발생<br>
                • 해당 시기 길흉 평가: <span style="color: #ebcb8b; font-weight: bold;">{grade}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 📖 1. 핵심 심리 및 환경 변화")
            st.info(matched['Core_Interpretation'])
            
            st.markdown("#### 🎯 2. 상황별 구체적 행동 전략 비책")
            st.success(f"**[Action Guide - 실천 행동 지침]**\n\n{matched['Action_Guide']}")
            
        else:
            st.warning(f"일간 '{my_hangul}'에 해당하는 데이터를 찾지 못했습니다.")
            
    except Exception as e:
        st.error(f"Saju_Rules 데이터 조회 오류: {e}")
