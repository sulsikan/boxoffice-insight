# 누락된 데이터가 있어서 코드를 수정했는데 이 코드가 실행이 안되면 crawl_info.py를 실항한 후 crawl_10days_plus.py를 사용하세요. 
# 실행 방법 : 프로젝트 루트 폴더에서 python movie_performance_summary/crawl_10days.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import sys
import django
import os
# Django 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Django 설정 불러오기
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boxoffice.settings")
django.setup()

from movie_performance_summary.models import Movie10days

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

with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
    driver.get("https://www.kobis.or.kr/kobis/business/stat/boxs/findFormerBoxOfficeList.do")
    
    # 일일 박스오피스 저장할 리스트
    movie_daily_data_list = []
    
    # 영화 제목 누르기
    for i in range(200):
        try:
            button = driver.find_element(By.CSS_SELECTOR, f"#tr_{i} a")
            button.click()
            driver.implicitly_wait(10)

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
                print(f"데이터 로드 실패")
            else:
                # td 태그 텍스트 가져오기
                cnt = 0
                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    texts = [col.get_attribute("innerText").strip() for col in cols]

                    movie_daily_data = {
                        "movie_name": button,
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
            button = driver.find_element(By.LINK_TEXT, "닫기")
            button.click()


        except Exception as e:
            print("영화 링크 클릭 실패:", e) 

        
        
        

save_data_to_db(movie_daily_data_list)