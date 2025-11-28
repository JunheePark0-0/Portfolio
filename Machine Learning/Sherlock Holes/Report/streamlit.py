# import streamlit as st
# import pandas as pd
# import numpy as np
# import pickle

# # ✅ 항상 최상단에서 세션 상태 초기화
# if 'reports' not in st.session_state:
#     st.session_state.reports = []

# if 'show_results' not in st.session_state:
#     st.session_state.show_results = False


# # 1. 페이지 설정
# st.set_page_config(page_title="Pothole Report", layout="wide")

# # 2. 상단 고정 요소
# st.title("Pothole Report")
# st.markdown("<div style='text-align:right; font-size:18px; color:gray;'>SHERLOCK HOLES</div>", unsafe_allow_html=True)
# st.markdown("---")


# # 3. 사이드바 메뉴 (목차 역할)
# menu = st.sidebar.radio(
#     "📌 메뉴 선택",
#     ("변수 영향력 확인 (SHAP)", "모델 예측 확인", "특정 장소 요인 분석 (SHAP)", "개선 방향 (DiCE)")
# )

# # 4. 안내 콜아웃 (공통)
# if menu != '변수 영향력 확인 (SHAP)':

#     # 메뉴별 state key 정의
#     key_map = {
#         "모델 예측 확인": "prediction",
#         "특정 장소 요인 분석 (SHAP)": "place",
#         "개선 방향 (DiCE)": "dice"
#     }
#     key_suffix = key_map[menu]

#     # 각 메뉴별 세션 상태 초기화
#     if f"reports_{key_suffix}" not in st.session_state:
#         st.session_state[f"reports_{key_suffix}"] = []
#     if f"show_results_{key_suffix}" not in st.session_state:
#         st.session_state[f"show_results_{key_suffix}"] = False

#     # 입력 콜아웃
#     st.markdown("""
#         <div style="text-align: right;">
#             <div class="info-container">
#                 <img src="https://img.icons8.com/ios-filled/50/000000/search--v1.png" class="info-icon"/>
#                 <p class="info-text">아래에 주소와 날짜를 입력한 뒤 Enter를 눌러주세요!</p>
#             </div>
#         </div>
#         <div style='height: 25px;'></div>
#     """, unsafe_allow_html=True)

#     # 주소 & 날짜 입력창
#     address = st.text_input("주소를 입력해주세요 :)", placeholder="예: 서울시 서초구 ...", key=f"address_{key_suffix}")
#     date_str = st.text_input("날짜를 입력해주세요 :)", placeholder="예: 2025/06/12", key=f"date_{key_suffix}")


#     # Enter 버튼 처리
# if st.button("Enter", key=f"enter_{key_suffix}"):
#         if not address.strip():
#             st.warning("주소를 입력해 주세요.")
#         elif not date_str.strip():
#             st.warning("날짜를 입력해 주세요.")
#         else:
#             st.session_state[f"reports_{key_suffix}"].append({"날짜": date_str, "주소": address})

#     # 누적 표 출력
# if st.session_state[f"reports_{key_suffix}"]:
#         df = pd.DataFrame(st.session_state[f"reports_{key_suffix}"])

#         col1, col2 = st.columns([2.1, 7.9])
        
#         with col1:
#             st.markdown("#### 🔍 확인할 날짜/장소 목록")

#         with col2:
#             if menu == "모델 예측 확인":
#                 if st.button("결과 보기", key="result_button_prediction"):
#                     st.session_state.show_results_prediction = True
#             elif menu == "특정 장소 요인 분석 (SHAP)":
#                 if st.button("결과 보기", key="result_button_place"):
#                     st.session_state.show_results_place = True
#             elif menu == "개선 방향 (DiCE)":
#                 if st.button("결과 보기", key="result_button_dice"):
#                     st.session_state.show_results_dice = True


#             st.markdown("""
#                 <style>
#                     div[data-testid="column"] div:has(button) {
#                         display: flex;
#                         justify-content: flex-end;
#                     }
#                     .stButton > button {
#                         background-color: black !important;
#                         color: white !important;
#                         font-weight: bold !important;
#                         font-size: 12px !important;
#                         padding: 6px 12px !important;
#                         border: none !important;
#                         border-radius: 6px !important;
#                     }
#                 </style>
#             """, unsafe_allow_html=True)

#         st.dataframe(df, use_container_width=True)


# # 6. 메뉴에 따라 다른 콘텐츠 출력 -----------------------
# if menu == "변수 영향력 확인 (SHAP)":
#         st.subheader("🔍 변수 영향력 확인 (SHAP)")
#         col1, col2, col3 = st.columns([4,2,4])
#         with col1:
#             st.image("전체 feature importance.png", caption="SHAP 변수 중요도", use_container_width=True)
#         with col3:
#             st.markdown("##### 그래프 설명")
#             st.markdown("""
#             - 이 그래프는 SHAP 값을 기준으로 변수들의 중요도를 나타냅니다.
#             - 값이 클수록 해당 변수가 예측에 많은 영향을 줍니다.
#             - 예를 들어, `중대형차량 교통량`이 가장 영향력이 높습니다.
#             - 색상은 평균 SHAP 값의 방향(양/음)을 나타냅니다.
#             """)

#         col1, col2, col3 = st.columns([4,2,4])
#         with col1:
#             st.image("평균 feature importance.png", caption="SHAP 변수 중요도", use_container_width=True)
#         with col3:
#             st.markdown("##### 그래프 설명")
#             st.markdown("""
#             - 이 그래프는 SHAP 값을 기준으로 변수들의 중요도를 나타냅니다.
#             - 값이 클수록 해당 변수가 예측에 많은 영향을 줍니다.
#             - 예를 들어, `중대형차량 교통량`이 가장 영향력이 높습니다.
#             - 색상은 평균 SHAP 값의 방향(양/음)을 나타냅니다.
#             """)

#         col1, col2, col3 = st.columns([4,2,4])
#         with col1:
#             st.image("승용차 feature importance.png", caption="SHAP 변수 중요도", use_container_width=True)
#         with col3:
#             st.markdown("##### 그래프 설명")
#             st.markdown("""
#             - 이 그래프는 SHAP 값을 기준으로 변수들의 중요도를 나타냅니다.
#             - 값이 클수록 해당 변수가 예측에 많은 영향을 줍니다.
#             - 예를 들어, `중대형차량 교통량`이 가장 영향력이 높습니다.
#             - 색상은 평균 SHAP 값의 방향(양/음)을 나타냅니다.
#             """)

# if menu == "모델 예측 확인":
#     if st.session_state.get("show_results_prediction", False):

#         st.subheader("📈 모델 예측 결과")
#         df = pd.read_csv("new_places_org_pres.csv")
#         df.drop(['Unnamed: 0'], axis = 1, inplace = True)
#         st.dataframe(df)
#         df2 = pd.read_csv("new_places_output_pres.csv")
#         df2.drop(['Unnamed: 0'], axis = 1, inplace = True)
#         st.dataframe(df2)
        

# elif menu == "특정 장소 요인 분석 (SHAP)":
#     if st.session_state.get("show_results_place", False):

#         st.subheader("📍 특정 장소 SHAP 분석")
#         col1, col2, col3 = st.columns([4,2,4])
#         with col1:
#             st.image("전체 feature importance_개별.png", caption="SHAP 변수 중요도", use_container_width=True)
#         with col3:
#             st.markdown("##### 그래프 설명")
#             st.markdown("""
#             - 이 그래프는 SHAP 값을 기준으로 변수들의 중요도를 나타냅니다.
#             - 값이 클수록 해당 변수가 예측에 많은 영향을 줍니다.
#             - 예를 들어, `중대형차량 교통량`이 가장 영향력이 높습니다.
#             - 색상은 평균 SHAP 값의 방향(양/음)을 나타냅니다.
#             """)

#         col1, col2, col3 = st.columns([4,2,4])
#         with col1:
#             st.image("평균 feature importance_개별.png", caption="SHAP 변수 중요도", use_container_width=True)
#         with col3:
#             st.markdown("##### 그래프 설명")
#             st.markdown("""
#             - 이 그래프는 SHAP 값을 기준으로 변수들의 중요도를 나타냅니다.
#             - 값이 클수록 해당 변수가 예측에 많은 영향을 줍니다.
#             - 예를 들어, `중대형차량 교통량`이 가장 영향력이 높습니다.
#             - 색상은 평균 SHAP 값의 방향(양/음)을 나타냅니다.
#             """)


# elif menu == "개선 방향 (DiCE)":
#     if st.session_state.get("show_results_dice", False):

#         st.subheader("🔁 개선 방향 제시 (DiCE)")
#         df = pd.read_csv("original_one_pres.csv")
#         df.drop(['Unnamed: 0'], axis = 1, inplace = True)
#         st.dataframe(df)
#         df2 = pd.read_csv("changed_zero_pres.csv")
#         df2.drop(['Unnamed: 0'], axis = 1, inplace = True)
#         st.dataframe(df2)



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
        st.subheader(" ")
        # col1, col2, col3 = st.columns([4,2,4])
        col1, col2, col3, col4, col5, col6 = st.columns([1.5, 1.8, 1.5, 1.85, 1.5, 1.85])
        with col1:
            st.image("전체 feature importance.png", caption="변수 중요도_전체", use_container_width=True)
        with col2:
            st.markdown("##### 그래프 설명")
            st.markdown("""
            - 이 그래프는 전체 데이터에 대해, 모델에 사용된 변수들의 전반적인 중요도를 나타냅니다.
            - 값이 클수록 해당 변수가 예측에 많은 영향을 주었음을 의미합니다.
            - 전체 SHAP 값에 절댓값을 씌워 평균한 것으로, 예측 방향과는 무관합니다. 
            - 이번 장소에 대해서는 `총교통량`, `차선수`... 순으로 큰 영향력을 확인할 수 있습니다.
            """)

        # col1, col2, col3 = st.columns([4,2,4])
        with col3:
            st.image("평균 feature importance.png", caption="변수 중요도_평균", use_container_width=True)
        with col4:
            st.markdown("##### 그래프 설명")
            st.markdown("""
            - 이 그래프는 전체 데이터에 대해, SHAP 값을 기준으로 각 변수들의 중요도를 나타냅니다.
            - 값이 클수록 해당 변수가 예측에 많은 영향을 주었음을 의미합니다.
            - 전체 SHAP 값의 부호를 반영해 평균한 것으로, 각 변수의 색이 빨간색이라면 `포트홀 발생(y=1)` 쪽으로, 파란색이라면 `미발생(y=0)` 쪽으로 영향을 주었음을 의미합니다.
            - 이번 장소에 대해서는 양의 방향으로는 `인구수`, `총교통량`... 순으로, 음의 방향으로는 `트럭`, `평균_건물연령`... 순으로 큰 영향력을 확인할 수 있습니다.
            """)

        # col1, col2, col3 = st.columns([4,2,4])
        with col5:
            st.image("승용차 feature importance.png", caption="특정 변수 중요도", use_container_width=True)
        with col6:
            st.markdown("##### 그래프 설명")
            st.markdown("""
            - 이 그래프는 전체 데이터에 대해, 입력 받은 특정 변수의 중요도를 나타냅니다.
            - x축은 해당 변수의 데이터 값, y축은 해당 변수의 SHAP 값을 나타내며, SHAP 값이 높을수록 영향력이 큼을 의미합니다.
            - 예를 들어, `승용차` 변수의 경우, 전체적으로 우상향하는 곡선 형태를 띠고 있으므로 `포트홀 발생(y=1)`에 대해 비선형적인, 양의 영향력을 준다는 것을 알 수 있습니다.
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
        col1, col2, col3, col4 = st.columns([2,3,2,3])
    
        with col1:
            st.image("전체 feature importance_개별.png", caption="변수 중요도 _전체", use_container_width=True)
        with col2:
            st.markdown("##### 그래프 설명")
            st.markdown("""
            - 이 그래프는 모델에 사용된 변수들의 전반적인 중요도를 나타냅니다.
            - 값이 클수록 해당 변수가 예측에 많은 영향을 주었음을 의미합니다.
            - 전체 SHAP 값에 절댓값을 씌워 평균한 것으로, 예측 방향과는 무관합니다. 
            - 이번 장소에 대해서는 `총교통량`, `차선수`... 순으로 큰 영향력을 확인할 수 있습니다. 
            """)

        # col1, col2, col3 = st.columns([4,2,4])
        with col3:
            st.image("평균 feature importance_개별.png", caption="변수 중요도_평균", use_container_width=True)
        with col4:
            st.markdown("##### 그래프 설명")
            st.markdown("""
            - 이 그래프는 모델에 사용된 변수들이 예측에 준 영향을 나타냅니다.
            - 예측값이 모델의 평균으로부터 어떻게 변화하여 최종 확률에 도달했는지를 보여줍니다.
            - 그래프의 하단에서부터 시작하여, 각 변수의 색이 빨간색이라면 예측을 `포트홀 발생(y=1)` 쪽으로, 파란색이라면 `미발생(y=0)` 쪽으로 이끈다는 의미입니다. 
            - 이번 장소에 대해서는 평균 0.531의 log-odds에서 시작하여, `배수등급` 변수가 음의 방향으로 0.05만큼, `트럭` 변수가 음의 방향으로 0.07만큼.. 이동시켰음을 알 수 있습니다. 
            - 최종 도착 지점의 값이 양수라면 `포트홀 발생(y=1)`으로 예측되었음을, 음수라면 `미발생(y=0)`으로 예측되었음을 의미합니다. 
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


#### streamlit run pothole.py 터미널에 
#### 메인 페이지 하나 만들어서 모델 구조같은 거 세은이가 만들면 그거 이미지로 넣고 
#### 각 기능 설명하는 내용 하나 만들어서 넣기