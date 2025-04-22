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

from .models import Movie10days
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


# 마지막 비긴어게인 보충
with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
    driver.get("https://www.kobis.or.kr/kobis/business/stat/boxs/findFormerBoxOfficeList.do")
    movie_daily_data_list = []
    button = driver.find_element(By.CSS_SELECTOR, "#tr_199 a")
    button.click()
    driver.implicitly_wait(10)
    rows = driver.find_elements(By.CSS_SELECTOR, "div.info.info2 table.tbl_comm.topico tbody tr")
    # td 태그 텍스트 가져오기
    cnt = 0
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        texts = [col.get_attribute("innerText").strip() for col in cols]

        movie_daily_data = {
            "movie_name": button.text,
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

save_data_to_db(movie_daily_data_list)