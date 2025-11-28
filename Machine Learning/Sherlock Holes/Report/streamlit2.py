import streamlit as st
import pandas as pd
import numpy as np
import pickle

# ✅ 항상 최상단에서 세션 상태 초기화
if 'reports' not in st.session_state:
    st.session_state.reports = []

if 'show_results' not in st.session_state:
    st.session_state.show_results = False


# 1. 페이지 설정
st.set_page_config(page_title="Pothole Report", layout="wide")

# 2. 상단 고정 요소
st.title("Pothole Report")
st.markdown("<div style='text-align:right; font-size:18px; color:gray;'>SHERLOCK HOLES</div>", unsafe_allow_html=True)
st.markdown("---")


# 3. 사이드바 메뉴 (목차 역할)
menu = st.sidebar.radio(
    "📌 메뉴 선택",
    ("변수 영향력 확인 (SHAP)", "모델 예측 확인", "특정 장소 요인 분석 (SHAP)", "개선 방향 (DiCE)")
)

# 4. 안내 콜아웃 (공통)
if menu != '변수 영향력 확인 (SHAP)':

    # 메뉴별 state key 정의
    key_map = {
        "모델 예측 확인": "prediction",
        "특정 장소 요인 분석 (SHAP)": "place",
        "개선 방향 (DiCE)": "dice"
    }
    key_suffix = key_map[menu]

    # 각 메뉴별 세션 상태 초기화
    if f"reports_{key_suffix}" not in st.session_state:
        st.session_state[f"reports_{key_suffix}"] = []
    if f"show_results_{key_suffix}" not in st.session_state:
        st.session_state[f"show_results_{key_suffix}"] = False

    # 입력 콜아웃
    st.markdown("""
        <div style="text-align: right;">
            <div class="info-container">
                <img src="https://img.icons8.com/ios-filled/50/000000/search--v1.png" class="info-icon"/>
                <p class="info-text">아래에 주소와 날짜를 입력한 뒤 Enter를 눌러주세요!</p>
            </div>
        </div>
        <div style='height: 25px;'></div>
    """, unsafe_allow_html=True)

    # 주소 & 날짜 입력창
    address = st.text_input("주소를 입력해주세요 :)", placeholder="예: 서울시 서초구 ...", key=f"address_{key_suffix}")
    date_str = st.text_input("날짜를 입력해주세요 :)", placeholder="예: 2025/06/12", key=f"date_{key_suffix}")


    # Enter 버튼 처리
if st.button("Enter", key=f"enter_{key_suffix}"):
        if not address.strip():
            st.warning("주소를 입력해 주세요.")
        elif not date_str.strip():
            st.warning("날짜를 입력해 주세요.")
        else:
            st.session_state[f"reports_{key_suffix}"].append({"날짜": date_str, "주소": address})

    # 누적 표 출력
if st.session_state[f"reports_{key_suffix}"]:
        df = pd.DataFrame(st.session_state[f"reports_{key_suffix}"])

        col1, col2 = st.columns([2.1, 7.9])
        
        with col1:
            st.markdown("#### 🔍 확인할 날짜/장소 목록")

        with col2:
            if menu == "모델 예측 확인":
                if st.button("결과 보기", key="result_button_prediction"):
                    st.session_state.show_results_prediction = True
            elif menu == "특정 장소 요인 분석 (SHAP)":
                if st.button("결과 보기", key="result_button_place"):
                    st.session_state.show_results_place = True
            elif menu == "개선 방향 (DiCE)":
                if st.button("결과 보기", key="result_button_dice"):
                    st.session_state.show_results_dice = True


            st.markdown("""
                <style>
                    div[data-testid="column"] div:has(button) {
                        display: flex;
                        justify-content: flex-end;
                    }
                    .stButton > button {
                        background-color: black !important;
                        color: white !important;
                        font-weight: bold !important;
                        font-size: 12px !important;
                        padding: 6px 12px !important;
                        border: none !important;
                        border-radius: 6px !important;
                    }
                </style>
            """, unsafe_allow_html=True)

        st.dataframe(df, use_container_width=True)


# 6. 메뉴에 따라 다른 콘텐츠 출력 -----------------------
if menu == "변수 영향력 확인 (SHAP)":
        st.subheader("🔍 변수 영향력 확인 (SHAP)")
        col1, col2, col3 = st.columns([4,2,4])
        with col1:
            st.image("전체 feature importance.png", caption="SHAP 변수 중요도", use_container_width=True)
        with col3:
            st.markdown("##### 그래프 설명")
            st.markdown("""
            - 이 그래프는 SHAP 값을 기준으로 변수들의 중요도를 나타냅니다.
            - 값이 클수록 해당 변수가 예측에 많은 영향을 줍니다.
            - 예를 들어, `중대형차량 교통량`이 가장 영향력이 높습니다.
            - 색상은 평균 SHAP 값의 방향(양/음)을 나타냅니다.
            """)

        col1, col2, col3 = st.columns([4,2,4])
        with col1:
            st.image("평균 feature importance.png", caption="SHAP 변수 중요도", use_container_width=True)
        with col3:
            st.markdown("##### 그래프 설명")
            st.markdown("""
            - 이 그래프는 SHAP 값을 기준으로 변수들의 중요도를 나타냅니다.
            - 값이 클수록 해당 변수가 예측에 많은 영향을 줍니다.
            - 예를 들어, `중대형차량 교통량`이 가장 영향력이 높습니다.
            - 색상은 평균 SHAP 값의 방향(양/음)을 나타냅니다.
            """)

        col1, col2, col3 = st.columns([4,2,4])
        with col1:
            st.image("승용차 feature importance.png", caption="SHAP 변수 중요도", use_container_width=True)
        with col3:
            st.markdown("##### 그래프 설명")
            st.markdown("""
            - 이 그래프는 SHAP 값을 기준으로 변수들의 중요도를 나타냅니다.
            - 값이 클수록 해당 변수가 예측에 많은 영향을 줍니다.
            - 예를 들어, `중대형차량 교통량`이 가장 영향력이 높습니다.
            - 색상은 평균 SHAP 값의 방향(양/음)을 나타냅니다.
            """)

if menu == "모델 예측 확인":
    if st.session_state.get("show_results_prediction", False):

        st.subheader("📈 모델 예측 결과")
        df = pd.read_csv("new_places_org_pres.csv")
        df.drop(['Unnamed: 0'], axis = 1, inplace = True)
        st.dataframe(df)
        df2 = pd.read_csv("new_places_output_pres.csv")
        df2.drop(['Unnamed: 0'], axis = 1, inplace = True)
        st.dataframe(df2)
        

elif menu == "특정 장소 요인 분석 (SHAP)":
    if st.session_state.get("show_results_place", False):

        st.subheader("📍 특정 장소 SHAP 분석")
        col1, col2, col3 = st.columns([4,2,4])
        with col1:
            st.image("전체 feature importance_개별.png", caption="SHAP 변수 중요도", use_container_width=True)
        with col3:
            st.markdown("##### 그래프 설명")
            st.markdown("""
            - 이 그래프는 SHAP 값을 기준으로 변수들의 중요도를 나타냅니다.
            - 값이 클수록 해당 변수가 예측에 많은 영향을 줍니다.
            - 예를 들어, `중대형차량 교통량`이 가장 영향력이 높습니다.
            - 색상은 평균 SHAP 값의 방향(양/음)을 나타냅니다.
            """)

        col1, col2, col3 = st.columns([4,2,4])
        with col1:
            st.image("평균 feature importance_개별.png", caption="SHAP 변수 중요도", use_container_width=True)
        with col3:
            st.markdown("##### 그래프 설명")
            st.markdown("""
            - 이 그래프는 SHAP 값을 기준으로 변수들의 중요도를 나타냅니다.
            - 값이 클수록 해당 변수가 예측에 많은 영향을 줍니다.
            - 예를 들어, `중대형차량 교통량`이 가장 영향력이 높습니다.
            - 색상은 평균 SHAP 값의 방향(양/음)을 나타냅니다.
            """)


elif menu == "개선 방향 (DiCE)":
    if st.session_state.get("show_results_dice", False):

        st.subheader("🔁 개선 방향 제시 (DiCE)")
        df = pd.read_csv("original_one_pres.csv")
        df.drop(['Unnamed: 0'], axis = 1, inplace = True)
        st.dataframe(df)
        df2 = pd.read_csv("changed_zero_pres.csv")
        df2.drop(['Unnamed: 0'], axis = 1, inplace = True)
        st.dataframe(df2)


