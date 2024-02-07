# -*- encoding:utf-8 -*-

import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
from streamlit_option_menu import option_menu

SEOUL_PUBLIC_API = st.secrets["SEOUL_PUBLIC_API"]

@st.cache_data
def load_data():
    df = pd.read_csv('./data/data.csv')
    data = df.loc[:, ['SGG_NM',  # 자치구명
    'BJDONG_NM',  # 법정동명
    'CNTRCT_DE',  # 계약일
    'RENT_GBN',  # 전월세 구분
    'RENT_AREA',  # 임대면적
    'RENT_GTN',  # 보증금(만원)
    'RENT_FEE',  # 임대료(만원)
    'BLDG_NM',  # 건물명
    'BUILD_YEAR',  # 건축년도
    'HOUSE_GBN_NM',  # 건물용도
    'BEFORE_GRNTY_AMOUNT',  # 종전보증금
    'BEFORE_MT_RENT_CHRGE']]  # 종전임대료
    data['평수'] = data['RENT_AREA'] * 0.3025
    data['BLDG_NM'] = data['BLDG_NM'].fillna(data['HOUSE_GBN_NM'])
    return data

# 임대료 보증금 평균 그래프
def plot_graph(data, x, y1, y2=None, secondary_y=False, title=''):
    fig = make_subplots(specs=[[{"secondary_y": secondary_y}]])    
    # y1에 대한 막대 차트 추가
    fig.add_trace(go.Bar(x=data[x], y=data[y1],
                         name='보증금 평균', marker=dict(color=data[y1], colorscale='Blues')), secondary_y=False)    
    # y2가 제공되면 y2에 대한 선 차트 추가
    if y2:    
        fig.add_trace(go.Scatter(x=data[x], y=data[y2], name='임대료 평균', line=dict(color='white')), secondary_y=True)
    # 레이아웃 및 축 제목 업데이트
    fig.update_layout(title=title)
    fig.update_yaxes(title_text='보증금(만 원)', secondary_y=False, tickformat=',.0f')
    if y2:
        fig.update_yaxes(title_text='임대료(만 원)', secondary_y=True, tickformat=',.0f')
    # Streamlit에서 Plotly 차트 표시
    st.plotly_chart(fig, use_container_width=True)

# 표를 생성하는 함수
def show_dataframe(dataframe):
    # 사용자가 체크박스를 선택하면 표를 보여줌
    if st.checkbox('표 보이기'):
        # 표를 출력함
        st.dataframe(dataframe, hide_index=True, use_container_width=True)

# 메인 페이지
def main_page():
    st.title("🏠 내집을 찾아서")
    st.subheader("서울 집 값, 어디까지 알아보고 오셨어요?")

# 자치구별 시세 페이지
def sgg_page(recent_data):
    st.title("자치구별 시세")

    # 최대 평수 구해서 정수로 나타내기(반올림)
    max_area_value = math.ceil(recent_data['평수'].max())

    # 필터 설정
    rent_filter = st.selectbox('전·월세', recent_data['RENT_GBN'].unique())
    house_filter = st.multiselect('건물용도', recent_data['HOUSE_GBN_NM'].unique())
    area_filter = st.slider('평수', min_value=0, max_value=max_area_value, value=(0, max_area_value))

    # 필터 적용
    filtered_recent_data = recent_data[(recent_data['RENT_GBN'] == rent_filter) &
                    (recent_data['HOUSE_GBN_NM'].isin(house_filter)) &
                    (recent_data['평수'] >= area_filter[0]) &
                    (recent_data['평수'] <= area_filter[1])]

    # 자치구별 평균 계산
    average_data = filtered_recent_data.groupby('SGG_NM').agg({'RENT_FEE': 'mean', 'RENT_GTN': 'mean', '평수': 'mean'}).reset_index()

    # 그래프 및 표 생성
    if rent_filter == '월세' and not average_data.empty:
        plot_graph(average_data, x='SGG_NM', y1='RENT_GTN', y2='RENT_FEE', secondary_y=True, title='자치구별 시세')
        show_dataframe(average_data[['SGG_NM', 'RENT_GTN', 'RENT_FEE', '평수']].rename(columns={'SGG_NM': '자치구', 'RENT_GTN': '보증금 평균', 'RENT_FEE': '임대료 평균', '평수': '평수 평균'}))
    elif rent_filter == '전세' and not average_data.empty:
        plot_graph(average_data, x='SGG_NM', y1='RENT_GTN', title='자치구별 시세')
        show_dataframe(average_data[['SGG_NM', 'RENT_GTN', '평수']].rename(columns={'SGG_NM': '자치구', 'RENT_GTN': '보증금 평균', 'RENT_FEE': '임대료 평균', '평수': '평수 평균'}))
    else:
        st.write("최근 1개월 내 계약 내역이 없습니다. 다른 옵션을 선택하세요.")

# 법정동별 시세 페이지
def bjdong_page(recent_data):
    st.title("법정동별 시세")

    # 최대 평수 구해서 정수로 나타내기(반올림)
    max_area_value = math.ceil(recent_data['평수'].max())

    # 필터 설정
    rent_filter = st.selectbox('전·월세', recent_data['RENT_GBN'].unique())
    sgg_filter = st.selectbox('자치구', recent_data['SGG_NM'].unique())
    house_filter = st.multiselect('건물용도', recent_data['HOUSE_GBN_NM'].unique())
    area_filter = st.slider('평수', min_value=0, max_value=max_area_value, value=(0, max_area_value))

    # 필터 적용
    filtered_recent_data = recent_data[(recent_data['SGG_NM'] == sgg_filter) &
                    (recent_data['RENT_GBN'] == rent_filter) &
                    (recent_data['HOUSE_GBN_NM'].isin(house_filter)) &
                    (recent_data['평수'] >= area_filter[0]) &
                    (recent_data['평수'] <= area_filter[1])]

    # 법정동별 평균 계산
    average_data = filtered_recent_data.groupby('BJDONG_NM').agg({'RENT_FEE': 'mean', 'RENT_GTN': 'mean', '평수': 'mean'}).reset_index()

    # 그래프 및 표 생성
    if rent_filter == '월세' and not average_data.empty:
        plot_graph(average_data, x='BJDONG_NM', y1='RENT_GTN', y2='RENT_FEE', secondary_y=True, title='법정동별 시세')
        show_dataframe(average_data[['BJDONG_NM', 'RENT_GTN', 'RENT_FEE', '평수']].rename(columns={'BJDONG_NM': '법정동', 'RENT_GTN': '보증금 평균', 'RENT_FEE': '임대료 평균', '평수': '평수 평균'}))
    elif rent_filter == '전세' and not average_data.empty:
        plot_graph(average_data, x='BJDONG_NM', y1='RENT_GTN', title='법정동별 시세')
        show_dataframe(average_data[['BJDONG_NM', 'RENT_GTN', '평수']].rename(columns={'BJDONG_NM': '법정동', 'RENT_GTN': '보증금 평균', '평수': '평수 평균'}))
    else:
        st.write("최근 1개월 내 계약 내역이 없습니다. 다른 옵션을 선택하세요.")

# 건물별 시세 페이지
def bldg_page(recent_data):
    st.title("건물별 시세")

    # 최대 평수 구해서 정수로 나타내기(반올림)
    max_area_value = math.ceil(recent_data['평수'].max())

    # 필터 설정
    rent_filter = st.selectbox('전·월세', recent_data['RENT_GBN'].unique())
    sgg_filter = st.selectbox('자치구', recent_data['SGG_NM'].unique())
    bjdong_options = recent_data[recent_data['SGG_NM'] == sgg_filter]['BJDONG_NM'].unique()
    bjdong_filter = st.selectbox('법정동', bjdong_options)
    house_filter = st.multiselect('건물용도', recent_data['HOUSE_GBN_NM'].unique())
    area_filter = st.slider('평수', min_value=0, max_value=max_area_value, value=(0, max_area_value))

    # 필터 적용
    filtered_recent_data = recent_data[(recent_data['BJDONG_NM'] == bjdong_filter) &
                    (recent_data['RENT_GBN'] == rent_filter) &
                    (recent_data['HOUSE_GBN_NM'].isin(house_filter)) &
                    (recent_data['평수'] >= area_filter[0]) &
                    (recent_data['평수'] <= area_filter[1])]

    # 건물별 평균 계산
    average_data = filtered_recent_data.groupby('BLDG_NM').agg({'RENT_FEE': 'mean', 'RENT_GTN': 'mean', '평수': 'mean'}).reset_index()

    # 그래프 및 표 생성
    if rent_filter == '월세' and not average_data.empty:
        plot_graph(average_data, x='BLDG_NM', y1='RENT_GTN', y2='RENT_FEE', secondary_y=True, title='건물별 시세')
        show_dataframe(average_data[['BLDG_NM', 'RENT_GTN', 'RENT_FEE', '평수']].rename(columns={'BLDG_NM': '건물명', 'RENT_GTN': '보증금 평균', 'RENT_FEE': '임대료 평균', '평수': '평수 평균'}))
    elif rent_filter == '전세' and not average_data.empty:
        plot_graph(average_data, x='BLDG_NM', y1='RENT_GTN', title='법정동별 시세')
        show_dataframe(average_data[['BLDG_NM', 'RENT_GTN', '평수']].rename(columns={'BLDG_NM': '건물명', 'RENT_GTN': '보증금 평균', '평수': '평수 평균'}))
    else:
        st.write("최근 1개월 내 계약 내역이 없습니다. 다른 옵션을 선택하세요.")

# 최근 1개월 시세 페이지
def onemonth_page(recent_data):
    st.title("건물별 시세")

    # 최대 평수 구해서 정수로 나타내기(반올림)
    max_area_value = math.ceil(recent_data['평수'].max())

    # 필터 설정
    rent_filter = st.selectbox('전·월세', recent_data['RENT_GBN'].unique())
    sgg_filter = st.selectbox('자치구', recent_data['SGG_NM'].unique())
    bjdong_options = recent_data[recent_data['SGG_NM'] == sgg_filter]['BJDONG_NM'].unique()
    bjdong_filter = st.selectbox('법정동', bjdong_options)
    house_filter = st.multiselect('건물용도', recent_data['HOUSE_GBN_NM'].unique())
    bldg_options = recent_data[(recent_data['RENT_GBN'] == rent_filter) & (recent_data['BJDONG_NM'] == bjdong_filter) & (recent_data['HOUSE_GBN_NM'].isin(house_filter))]['BLDG_NM'].unique()
    bldg_filter = st.multiselect('건물명', bldg_options)
    area_filter = st.slider('평수', min_value=0, max_value=max_area_value, value=(0, max_area_value))


    # 필터 적용
    filtered_recent_data = recent_data[(recent_data['BLDG_NM'].isin(bldg_filter)) &
                    (recent_data['RENT_GBN'] == rent_filter) &
                    (recent_data['HOUSE_GBN_NM'].isin(house_filter)) &
                    (recent_data['평수'] >= area_filter[0]) &
                    (recent_data['평수'] <= area_filter[1])]

    # 표 생성
    if rent_filter == '월세' and not filtered_recent_data.empty:
        st.dataframe(filtered_recent_data[['BLDG_NM', 'RENT_GTN', 'RENT_FEE', '평수']].rename(columns={'BLDG_NM': '건물명', 'RENT_GTN': '보증금', 'RENT_FEE': '임대료'}), hide_index=True, use_container_width=True)
    elif rent_filter == '전세' and not filtered_recent_data.empty:
        st.dataframe(filtered_recent_data[['BLDG_NM', 'RENT_GTN', '평수']].rename(columns={'BLDG_NM': '건물명', 'RENT_GTN': '보증금'}), hide_index=True, use_container_width=True)
    else:
        st.write("최근 1개월 내 계약 내역이 없습니다. 다른 옵션을 선택하세요.")

def main():
    # 데이터 불러오기
    data = load_data()

    # 최근 한 달 데이터만 가져오기
    # 정수로 된 날짜 열을 날짜로 변환
    data['CNTRCT_DE'] = pd.to_datetime(data['CNTRCT_DE'], format='%Y%m%d')

    # 데이터 중에서 가장 최근의 날짜 찾기
    latest_date = data['CNTRCT_DE'].max()

    # 최근 한 달 데이터 선택
    recent_data = data[data['CNTRCT_DE'] >= (latest_date - pd.DateOffset(days=30))]

    # 사이드바 메뉴
    with st.sidebar:
        selected_menu = option_menu("메뉴 선택", ["메인 페이지", "내가 살 곳 찾기", "집 값 파악하기"],
                            icons=['bi bi-house-fill','bi bi-geo-alt-fill', 'bi bi-graph-up-arrow'], menu_icon='bi bi-check',
                            styles={"container": {"background-color": "#3081D0", "padding": "0px"},
                                    "nav-link-selected": {"background-color": "#EEEEEE", "color": "#262730"}})

        if selected_menu == "메인 페이지":
            choice = "메인 페이지"
            
        elif selected_menu == "내가 살 곳 찾기":
            choice = option_menu("내가 살 곳 찾기", ["자치구 정하기", "동네 정하기", "건물 정하기"],
                                 icons=['bi bi-1-circle','bi bi-2-circle', 'bi bi-3-circle'], menu_icon='bi bi-house-fill',
                                 styles={"container": {"background-color": "#FC6736"}, "nav-link-selected": {"background-color": "#EEEEEE", "color": "#262730"}})

        elif selected_menu == "집 값 파악하기":
            choice = option_menu("집 값 파악하기", ["최근 1개월 시세", "2"],
                                 icons=['bi bi-1-circle','bi bi-2-circle'], menu_icon='bi bi-graph-up-arrow',
                                 styles={"container": {"background-color": "#FC6736"}, "nav-link-selected": {"background-color": "#EEEEEE", "color": "#262730"}})

    # 페이지 보이기
    if choice == "메인 페이지":
        main_page()

    if choice == "자치구 정하기":
        sgg_page(recent_data)
    
    if choice == "동네 정하기":
        bjdong_page(recent_data)
    
    if choice == "건물 정하기":
        bldg_page(recent_data)
    
    if choice == "최근 1개월 시세":
        onemonth_page(recent_data)
    
if __name__ == '__main__':
    main()