# -*- encoding:utf-8 -*-

import requests
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import os

# 환경 변수 로딩
load_dotenv()
SEOUL_PUBLIC_API = os.getenv("SEOUL_PUBLIC_API")

# 2024년~2023년 자료 탐색
## datachek.py

# 데이터 csv 파일 생성
'''
# API 크롤링
def fetch_data(start, end):
    URL = f'http://openapi.seoul.go.kr:8088/{SEOUL_PUBLIC_API}/json/tbLnOpendataRentV/{start}/{end}/'
    req = requests.get(URL)
    content = req.json()
    # 데이터 추출 및 DataFrame으로 변환
    return pd.DataFrame(content['tbLnOpendataRentV']['row'])

# 390,001~580,000 데이터 수집
data = None
start = 390001
end = 580000
for i in range(start, end+1, 1000):
    result = fetch_data(i, i+999)
    data = pd.concat([data, result], ignore_index=True)

# 580,000~580,507 데이터 수집
result = fetch_data(580001, 580507)
data = pd.concat([data, result], ignore_index=True)

# csv 파일 변환
data = data.reset_index(drop = True)
data.to_csv('data4.csv', encoding='utf-8', index = False)


# 데이터 합치기
data1 = pd.read_csv('./data/data1.csv', encoding='euc-kr', index_col=0)  # 'euc-kr'로 인코딩된 파일
data2 = pd.read_csv('./data/data2.csv', encoding='euc-kr')  # 'euc-kr'로 인코딩된 파일
data3 = pd.read_csv('./data/data3.csv')
data4 = pd.read_csv('./data/data4.csv')

data = pd.concat([data1, data2, data3, data4], ignore_index=True)

data.to_csv('./data/merged_data.csv', encoding='utf-8', index=False)
'''

# 데이터 불러오기
df = pd.read_csv('./data/data.csv')

# 데이터 정제하기
'''
SGG_NM: 자치구명
BJDONG_NM: 법정동명
CNTRCT_DE: 계약일
RENT_GBN: 전월세 구분
RENT_AREA: 임대면적
RENT_GTN: 보증금(만원)
RENT_FEE: 임대료(만원)
BLDG_NM: 건물명
BUILD_YEAR: 건축년도
HOUSE_GBN_NM: 건물용도
BEFORE_GRNTY_AMOUNT: 종전보증금
BEFORE_MT_RENT_CHRGE: 종전임대료
'''

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

# 범주형 데이터 값 확인
columns_categorical = ['SGG_NM', 'BJDONG_NM', 'RENT_GBN', 'BLDG_NM', 'HOUSE_GBN_NM']

for column in columns_categorical:
    value_counts = df[column].value_counts()
    print(f'{column} value counts:')
    print(value_counts)
    print()

# 연속형 데이터 최댓값 최솟값 확인
columns_continuous = ['CNTRCT_DE', 'RENT_AREA', 'RENT_GTN', 'RENT_FEE', 'BUILD_YEAR', 'BEFORE_GRNTY_AMOUNT', 'BEFORE_MT_RENT_CHRGE']

for column in columns_continuous:
    max = df[column].max()
    min = df[column].min()
    print(f'{column}')
    print(f'max: {max}, min: {min}')
    print()

# 임대료, 보증금이 0인 케이스 확인: 전월세 차이
print(data.loc[data['RENT_GTN'] == 0, :].head())
print(data.loc[data['RENT_GTN'] == 0, :].head())

# 평수 열 생성
data['평수'] = data['RENT_AREA'] * 0.3025

# 최근 한 달 데이터만 가져오기
# 정수로 된 날짜 열을 날짜로 변환
data['CNTRCT_DE'] = pd.to_datetime(data['CNTRCT_DE'], format='%Y%m%d')

# 데이터 중에서 가장 최근의 날짜 찾기
latest_date = data['CNTRCT_DE'].max()

# 최근 한 달 데이터 선택
recent_data = data[data['CNTRCT_DE'] >= (latest_date - pd.DateOffset(days=30))]