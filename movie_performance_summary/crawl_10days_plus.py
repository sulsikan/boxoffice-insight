# 이 코드는 crawl_info.py를 실행한 뒤 받은 movie 데이터와 비교하여 누락된 데이터를 찾고, 저장하는 코드입니다.
# Movie10days에서 누락된 데이터가 있을 때만 사용하면 됩니다.
# 실행 방법 : 프로젝트 루트 폴더에서 python movie_performance_summary/crawl_10days_plus.py
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

import django
import os
# Django 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Django 설정 불러오기
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boxoffice.settings")
django.setup()

from movie_performance_summary.models import Movie, Movie10days

def save_data_to_db(data_list):
    for item in data_list:
        try:
            movie = Movie10days(
                movie_name=item['movie_name'],
                days_since_release=item['days_since_release'],
                screen_num=int(item['screen_num'].replace(',', '')),
                screenings_num=int(item['screenings_num'].replace(',', '')),
                revenue=int(item['revenue'].replace(',', '')),
                moviegoers_num=int(item['moviegoers_num'].replace(',', '')),
                revenue_cumulative=int(item['revenue_cumulative'].replace(',', '')),
                moviegoers_cumulative=int(item['moviegoers_cumulative'].replace(',', '')),
                rank=item['rank'] if item['rank'] != 'N/A' else 'N/A',
            )
            movie.save()
        except Exception as e:
            print(f"저장 실패: {e}")


# 누락된 데이터를 찾고 저장
with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
    driver.get("https://www.kobis.or.kr/kobis/business/stat/boxs/findFormerBoxOfficeList.do")
    movie_daily_data_list = []

    # Movie 테이블에서 모든 영화 가져오기
    movies = Movie.objects.all()

    for movie in movies:
        # Movie10days 테이블에 해당 영화가 없으면 처리
        if not Movie10days.objects.filter(movie_name=movie.movie_name).exists():
            movie_id = movie.id - 1  # id - 1 계산
            try:
                # 영화 상세 데이터 버튼 클릭
                button = driver.find_element(By.CSS_SELECTOR, f"#tr_{movie_id} a")
                button.click()
                driver.implicitly_wait(20)

                # 데이터가 로드될 때까지 반복 확인
                max_retries = 10  # 최대 재시도 횟수
                retries = 0
                rows = []
                while retries < max_retries:
                    rows = driver.find_elements(By.CSS_SELECTOR, "div.info.info2 table.tbl_comm.topico tbody tr")
                    if rows:  # 데이터가 로드되었으면 반복 종료
                        break
                    retries += 1
                    time.sleep(1)  # 1초 대기 후 다시 시도

                if not rows:
                    print(f"데이터 로드 실패: {movie.movie_name}")
                else:
                    # td 태그 텍스트 가져오기
                    cnt = 0
                    for row in rows:
                        cols = row.find_elements(By.TAG_NAME, "td")
                        texts = [col.get_attribute("innerText").strip() for col in cols]

                        movie_daily_data = {
                            "movie_name": movie.movie_name,
                            "days_since_release": texts[0],
                            "screen_num": texts[1],
                            "screenings_num": texts[2],
                            "revenue": texts[3],
                            "moviegoers_num": texts[4],
                            "revenue_cumulative": texts[5],
                            "moviegoers_cumulative": texts[6],
                            "rank": texts[7],
                        }
                        movie_daily_data_list.append(movie_daily_data)

                        # 일일 박스오피스만 추출하는 조건문
                        cnt += 1
                        if cnt == 11:
                            break

                    # 스크래핑 다 했으면 나가기
                    close_button = driver.find_element(By.LINK_TEXT, "닫기")
                    close_button.click()

            except Exception as e:
                print(f"영화 상세 데이터 클릭 실패: {movie.movie_name}, 오류: {e}")

# 수집한 데이터를 데이터베이스에 저장
save_data_to_db(movie_daily_data_list)