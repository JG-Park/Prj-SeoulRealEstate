# -*- encoding:utf-8 -*-

import requests
import json
import pandas as pd
import streamlit as st

SEOUL_PUBLIC_API = st.secrets["SEOUL_PUBLIC_API"]

# API 크롤링
def fetch_data(start, end):
    URL = f'http://openapi.seoul.go.kr:8088/{SEOUL_PUBLIC_API}/json/tbLnOpendataRentV/{start}/{end}/'
    req = requests.get(URL)
    content = req.json()
    # 데이터 추출 및 DataFrame으로 변환
    return pd.DataFrame(content['tbLnOpendataRentV']['row'])

# Streamlit 앱으로 나타내기
def main():
    st.title('서울시 부동산 전월세가 정보')

    # 데이터 범위를 선택하는 슬라이더
    N = st.slider('범위:', 0, 6000, step=1000)

    data = None
    # API 요청 제한을 피하기 위해 1000개씩 데이터 가져오기
    start = 580000
    for i in range(start, start+N+1, 1000):
        result = fetch_data(i, i+999)
        data = pd.concat([data, result], ignore_index=True)

    # 데이터를 앱에 표시
    st.write(data)

if __name__ == '__main__':
    main()