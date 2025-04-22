from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import django
import os

# Django 설정 불러오기
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boxoffice.settings")
django.setup()

from korean_boxoffice.models import Movie
def save_data_to_db(data_list):
    for item in data_list:
        try:
            movie = Movie(
                # rank=item['rank'],
                movie_name=item['movie_name'],
                release_date=item['release_date'],
                total_revenue=int(item['total_revenue'].replace(',', '')),
                total_moviegoers_num=int(item['total_moviegoers_num'].replace(',', '')),
            )
            movie.save()
        except Exception as e:
            print(f"저장 실패: {e}")


# 역대 박스오피스 기본 정보 웹 스크래핑
movie_name = []
release_date = []
revenue = []
moviegoers_num = []
screens_num = []
screenings_num =[]
movie_data_list = []

with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
    driver.get("https://www.kobis.or.kr/kobis/business/stat/boxs/findFormerBoxOfficeList.do")
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
    # # 스크린 수
    # for element in driver.find_elements(By.ID, 'td_scrnCnt'):
    #     screens_num.append(element.text)
    # # 상영 횟수
    # for element in driver.find_elements(By.ID, 'td_showCnt'):
    #     screenings_num.append(element.text)

    for i in range(len(movie_name)):
        movie_data = {
                        "movie_name": movie_name[i],
                        "release_date": release_date[i],
                        "total_revenue": revenue[i],
                        "total_moviegoers_num": moviegoers_num[i],
                    }
        movie_data_list.append(movie_data)

save_data_to_db(movie_data_list)