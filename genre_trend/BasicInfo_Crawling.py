from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ChromeOptions
import os
import django
import sys
from selenium.webdriver.support.ui import Select

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boxoffice.settings")

django.setup()

from genre_trend.models import MovieBasicInfo
# 사이트 꺼짐 방지
options = ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.kobis.or.kr/kobis/business/stat/offc/findYearlyBoxOfficeList.do")
driver.implicitly_wait(0.5)


def movie_info():
    for i in range(0, 50):
        try:
            # 영화 기본 정보 가져오기
            parts = driver.find_element(By.ID, f"tr_tot{i}")
            parts = parts.text.split()
            release_date = parts[-5]  # 개봉일
            movie_name = ' '.join(parts[1:-5])  # 영화 제목

            # 링크 클릭
            xpath = f'//tr[@id="tr_tot{i}"]//a[@class="boxMNm"]'
            movie_link = driver.find_element(By.XPATH, xpath)
            movie_link.click()
            sleep(0.3)

            # 영화 상세 정보 가져오기
            is_now_showing = True
            elements = driver.find_elements(By.XPATH, '//*[text()="영화상영관상영중"]')
            if elements:
                print("현재 상영 중임")
            else:
                is_now_showing = False
                print("현재 상영 중 아님")
            xpath = '//*/div/div[1]/div[2]/dl/dd[4]'
            element = driver.find_element(By.XPATH, xpath)
            element = element.text.split("|")
            genre = element[2]  # 장르
            country = element[5]  # 국가

            # 영화 기본 정보
            result_1 = {
                "movie_name": movie_name,
                "release_date": release_date,
                "genre": genre,
                "is_now_showing": is_now_showing,
                "country": country
            }

            # DB 저장!
            MovieBasicInfo.objects.update_or_create(
                movie_name=movie_name,
                release_date=release_date,
                genre=genre,
                is_now_showing=is_now_showing,
                country=country,
                defaults=result_1
            )


            print("저장 완료:", result_1)
            close_button = driver.find_element(By.CLASS_NAME, "close")
            close_button.click()
            sleep(0.3)

        except Exception as e:
            print(f"[ERROR] {i}번째 영화 에러: {e}")
            continue


# 페이지 내 셀렉트 리스트와 버튼
search_button = driver.find_element(By.CLASS_NAME, "btn_blue")  # 검색 버튼
# 반복문 밖에서 전체 연도 리스트 먼저 수집
select_element = driver.find_element(By.ID, "sSearchYearFrom")
all_years = [option.get_attribute("value") for option in Select(select_element).options]
# 날짜 선택 
filtered_years = [year for year in all_years if int(year) >= 2014]

# 반복문 돌리기
for year_value in filtered_years:
    # 매번 select 객체 다시 가져오기 (안 그러면 stale element 에러나 무한 루프 가능성)
    select_element = driver.find_element(By.ID, "sSearchYearFrom")
    year_select = Select(select_element)

    print("선택 연도 :", year_value)
    year_select.select_by_value(year_value)

    # 검색 버튼 클릭
    search_button = driver.find_element(By.CLASS_NAME, "btn_blue")
    search_button.click()

    # 페이지 로딩 대기
    sleep(2)

    # 결과 크롤링 함수 호출
    movie_info()