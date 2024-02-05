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
    return data

# 자치구별 시세
def sgg_page(recent_data):
    st.title("자치구별 시세")

    # 최대 평수 구해서 정수로 나타내기(반올림)
    max_area_value = math.ceil(recent_data['평수'].max())

    # 필터 설정
    rent_filter = st.selectbox('전월세', recent_data['RENT_GBN'].unique())
    house_filter = st.multiselect('건물용도', recent_data['HOUSE_GBN_NM'].unique())
    area_filter = st.slider('평수', min_value=0, max_value=max_area_value, value=(0, max_area_value))

    # 필터 적용
    filtered_recent_data = recent_data[(recent_data['RENT_GBN'] == rent_filter) &
                    (recent_data['HOUSE_GBN_NM'].isin(house_filter)) &
                    (recent_data['평수'] >= area_filter[0]) &
                    (recent_data['평수'] <= area_filter[1])]

    # 자치구별 평균 계산
    average_data = filtered_recent_data.groupby('SGG_NM').agg({'RENT_FEE': 'mean', 'RENT_GTN': 'mean'}).reset_index()

    # 그래프 생성
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 월세인 경우에만 선 그래프 추가
    if rent_filter == '월세' and not average_data.empty:
        # 바 차트 추가
        fig.add_trace(go.Bar(x=average_data['SGG_NM'], y=average_data['RENT_GTN'],
                            name='보증금', marker=dict(color=average_data['RENT_GTN'], colorscale='Reds')), secondary_y=False)

        # 선 그래프 추가
        fig.add_trace(go.Scatter(x=average_data['SGG_NM'], y=average_data['RENT_FEE'], name='임대료', line=dict(color='black')), secondary_y=True)

        # 그래프 레이아웃 설정
        fig.update_layout(title='자치구별 시세')

        # y축 설정
        fig.update_yaxes(title_text='보증금', secondary_y=False)
        fig.update_yaxes(title_text='임대료', secondary_y=True)

        # Streamlit에서 Plotly 그래프 표시
        st.plotly_chart(fig)
    
    elif rent_filter == '전세' and not average_data.empty:
        # 전세인 경우 바 차트만 추가
        fig.add_trace(go.Bar(x=average_data['SGG_NM'], y=average_data['RENT_GTN'],
                            name='보증금', marker=dict(color=average_data['RENT_GTN'], colorscale='Reds')), secondary_y=False)

        # 그래프 레이아웃 설정
        fig.update_layout(title='자치구별 시세')

        # y축 설정
        fig.update_yaxes(title_text='보증금', secondary_y=False)

        # Streamlit에서 Plotly 그래프 표시
        st.plotly_chart(fig)
    
    else:
        # 그래프가 그려지지 않을 때 대체 문구 출력
        st.write("죄송합니다. 최근 1개월 내 계약 내역이 없습니다. 다른 옵션을 선택하세요.")


# 법정동별 시세
def bjdong_page(recent_data):
    st.title("법정동별 시세")

    # 최대 평수 구해서 정수로 나타내기(반올림)
    max_area_value = math.ceil(recent_data['평수'].max())

    # 필터 설정
    sgg_filter = st.selectbox('자치구', recent_data['SGG_NM'].unique())
    rent_filter = st.selectbox('전월세', recent_data['RENT_GBN'].unique())
    house_filter = st.multiselect('건물용도', recent_data['HOUSE_GBN_NM'].unique())
    area_filter = st.slider('평수', min_value=0, max_value=max_area_value, value=(0, max_area_value))

    # 필터 적용
    filtered_recent_data = recent_data[(recent_data['SGG_NM'] == sgg_filter) &
                    (recent_data['RENT_GBN'] == rent_filter) &
                    (recent_data['HOUSE_GBN_NM'].isin(house_filter)) &
                    (recent_data['평수'] >= area_filter[0]) &
                    (recent_data['평수'] <= area_filter[1])]

    # 법정동별 평균 계산
    average_data = filtered_recent_data.groupby('BJDONG_NM').agg({'RENT_FEE': 'mean', 'RENT_GTN': 'mean'}).reset_index()

    # 그래프 생성
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 월세인 경우에만 선 그래프 추가
    if rent_filter == '월세' and not average_data.empty:
        # 바 차트 추가
        fig.add_trace(go.Bar(x=average_data['BJDONG_NM'], y=average_data['RENT_GTN'],
                            name='보증금', marker=dict(color=average_data['RENT_GTN'], colorscale='Reds')), secondary_y=False)

        # 선 그래프 추가
        fig.add_trace(go.Scatter(x=average_data['BJDONG_NM'], y=average_data['RENT_FEE'], name='임대료', line=dict(color='black')), secondary_y=True)

        # 그래프 레이아웃 설정
        fig.update_layout(title='법정동별 시세')

        # y축 설정
        fig.update_yaxes(title_text='보증금', secondary_y=False)
        fig.update_yaxes(title_text='임대료', secondary_y=True)

        # Streamlit에서 Plotly 그래프 표시
        st.plotly_chart(fig)
    
    elif rent_filter == '전세' and not average_data.empty:
        # 전세인 경우 바 차트만 추가
        fig.add_trace(go.Bar(x=average_data['BJDONG_NM'], y=average_data['RENT_GTN'],
                            name='보증금', marker=dict(color=average_data['RENT_GTN'], colorscale='Reds')), secondary_y=False)

        # 그래프 레이아웃 설정
        fig.update_layout(title='법정동별 시세')

        # y축 설정
        fig.update_yaxes(title_text='보증금', secondary_y=False)

        # Streamlit에서 Plotly 그래프 표시
        st.plotly_chart(fig)
    
    else:
        # 그래프가 그려지지 않을 때 대체 문구 출력
        st.write("죄송합니다. 최근 1개월 내 계약 내역이 없습니다. 다른 옵션을 선택하세요.")

# 건물별 시세
def bldg_page(recent_data):
    st.title("건물별 시세")

    # 최대 평수 구해서 정수로 나타내기(반올림)
    max_area_value = math.ceil(recent_data['평수'].max())

    # 필터 설정
    sgg_filter = st.selectbox('자치구', recent_data['SGG_NM'].unique())
    bjdong_options = recent_data[recent_data['SGG_NM'] == sgg_filter]['BJDONG_NM'].unique()
    bjdong_filter = st.selectbox('법정동', bjdong_options)
    rent_filter = st.selectbox('전월세', recent_data['RENT_GBN'].unique())
    house_filter = st.multiselect('건물용도', recent_data['HOUSE_GBN_NM'].unique())
    area_filter = st.slider('평수', min_value=0, max_value=max_area_value, value=(0, max_area_value))

    # 필터 적용
    filtered_recent_data = recent_data[(recent_data['BJDONG_NM'] == bjdong_filter) &
                    (recent_data['RENT_GBN'] == rent_filter) &
                    (recent_data['HOUSE_GBN_NM'].isin(house_filter)) &
                    (recent_data['평수'] >= area_filter[0]) &
                    (recent_data['평수'] <= area_filter[1])]

    # 건물명 결측값 건물용도로 대체하기
    recent_data['BLDG_NM'] = recent_data['BLDG_NM'].fillna(recent_data['HOUSE_GBN_NM'])

    # 건물별 평균 계산
    average_data = filtered_recent_data.groupby('BLDG_NM').agg({'RENT_FEE': 'mean', 'RENT_GTN': 'mean'}).reset_index()

    # 그래프 생성
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 월세인 경우에만 선 그래프 추가
    if rent_filter == '월세' and not average_data.empty:
        # 바 차트 추가
        fig.add_trace(go.Bar(x=average_data['BLDG_NM'], y=average_data['RENT_GTN'],
                            name='보증금', marker=dict(color=average_data['RENT_GTN'], colorscale='Reds')), secondary_y=False)

        # 선 그래프 추가
        fig.add_trace(go.Scatter(x=average_data['BLDG_NM'], y=average_data['RENT_FEE'], name='임대료', line=dict(color='black')), secondary_y=True)

        # 그래프 레이아웃 설정
        fig.update_layout(title='건물별 시세')

        # y축 설정
        fig.update_yaxes(title_text='보증금', secondary_y=False)
        fig.update_yaxes(title_text='임대료', secondary_y=True)

        # Streamlit에서 Plotly 그래프 표시
        st.plotly_chart(fig)
    elif rent_filter == '전세' and not average_data.empty:
        # 전세인 경우 바 차트만 추가
        fig.add_trace(go.Bar(x=average_data['BLDG_NM'], y=average_data['RENT_GTN'],
                            name='보증금', marker=dict(color=average_data['RENT_GTN'], colorscale='Reds')), secondary_y=False)

        # 그래프 레이아웃 설정
        fig.update_layout(title='건물별 시세')

        # y축 설정
        fig.update_yaxes(title_text='보증금', secondary_y=False)

        # Streamlit에서 Plotly 그래프 표시
        st.plotly_chart(fig)
    else:
        # 그래프가 그려지지 않을 때 대체 문구 출력
        st.write("죄송합니다. 최근 1개월 내 계약 내역이 없습니다. 다른 옵션을 선택하세요.")

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

    # 선택된 데이터 출력
    # st.dataframe(recent_data)

    # 사이드바 메뉴
    with st.sidebar:
        choice = option_menu("내 집 찾기", ["자치구", "법정동", "건물"],
            icons=['bi bi-1-circle','bi bi-2-circle', 'bi bi-3-circle'],
            menu_icon='house', default_index=0)

    # 페이지 보이기
    if choice == "자치구":
        sgg_page(recent_data)
    
    if choice == "법정동":
        bjdong_page(recent_data)
    
    if choice == "건물":
        bldg_page(recent_data)
    
if __name__ == '__main__':
    main()