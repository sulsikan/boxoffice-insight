# 영화 연도별 시각화와 TOP 200 리스트를 위한 코드입니다.
# 실행 방법 : 프로젝트 루트 폴더에서 python movie_performance_summary/crawl_info.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

import django
import os
import sys
# Django 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Django 설정 불러오기
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boxoffice.settings")
django.setup()

from movie_performance_summary.models import Movie
def save_data_to_db(data_list):
    for item in data_list:
        try:
            movie = Movie(
                rank=item['rank'],
                movie_name=item['movie_name'],
                release_date=item['release_date'],
                total_revenue=int(item['total_revenue'].replace(',', '')),
                total_moviegoers_num=int(item['total_moviegoers_num'].replace(',', '')),
            )
            movie.save()
        except Exception as e:
            print(f"저장 실패: {e}")


# 역대 박스오피스 기본 정보 웹 스크래핑
rank = []
movie_name = []
release_date = []
revenue = []
moviegoers_num = []
movie_data_list = []

with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
    driver.get("https://www.kobis.or.kr/kobis/business/stat/boxs/findFormerBoxOfficeList.do")
    # 순위
    for element in driver.find_elements(By.XPATH, '//*[@id="td_rank"]'):
        rank.append(element.text)
    # 영화 제목
    for element in driver.find_elements(By.XPATH, '//*[@id="td_movie"]/span/a'):
        movie_name.append(element.text)
    # 개봉일
    for element in driver.find_elements(By.ID, 'td_openDt'):
        release_date.append(element.text)
    # 매출액
    for element in driver.find_elements(By.ID, 'td_salesAcc'):
        revenue.append(element.text)
    # 관객 수
    for element in driver.find_elements(By.ID, 'td_audiAcc'):
        moviegoers_num.append(element.text)


    for i in range(len(movie_name)):
        movie_data = {
                        "rank": rank[i],
                        "movie_name": movie_name[i],
                        "release_date": release_date[i],
                        "total_revenue": revenue[i],
                        "total_moviegoers_num": moviegoers_num[i],
                    }
        movie_data_list.append(movie_data)

save_data_to_db(movie_data_list)