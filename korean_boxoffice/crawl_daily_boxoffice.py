import logging
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta, timezone
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)
TIMEOUT = 20  # 20초
logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boxoffice.settings")
import django

django.setup()
from korean_boxoffice.models import DailyBoxoffice, MovieInfo

KST = timezone(timedelta(hours=+9))
UTC = timezone.utc


def to_ranking_date(string):
    tokens = string.split()
    year = tokens[0][:4]
    month = tokens[1][:2]
    day = tokens[2][:2]

    return datetime(int(year), int(month), int(day), tzinfo=KST)


def to_datetime_KST(str_date):
    try:
        year, month, day = str_date.split('-')
    except:
        return None
    return datetime(int(year), int(month), int(day), tzinfo=KST)


def str_replace_symbol(str_num):
    if '\n' in str_num:
        str_num = str_num.split('\n')[0]

    return str_num.replace(',', '').replace('%', '')


def str_to_int(str_int):
    return int(str_replace_symbol(str_int))


def str_to_float(str_float):
    return float(str_replace_symbol(str_float))


dayily_boxoffice_parsing_funcs = {
    'rank': str_to_int,
    'movie_name': str_replace_symbol,
    'release_date': to_datetime_KST,
    'revenue': str_to_int,
    'revenue_share': str_to_float,
    'revenue_fluctuation': str_to_int,
    # ('revenue_fluctuation_rate', str_to_float),  # 필요하면 씀
    'revenue_cumulative': str_to_int,
    'moviegoers_num': str_to_int,
    'moviegoers_fluctuation': str_to_int,
    # ('moviegoers_fluctuation_rate', str_to_float),  # 필요하면 씀
    'moviegoers_cumulative': str_to_int,
    'screens_num': str_to_int,
    'screenings_num': str_to_int,
}


def select_day(driver: webdriver.Chrome, year, month, day):
    # 2. 날짜 선택 시작
    logger.info(f"Setting date to: {f'{year}-{month}-{day}'}")

    # 달력 아이콘 찾기 (label.btn_cal > span.ico_comm)
    calendar_icon = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "label.btn_cal span.ico_comm"))
    )
    calendar_icon.click()
    sleep(2)

    # 년도 선택
    year_select = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ui-datepicker-year"))
    )
    # Select 요소 생성
    Select(year_select).select_by_value(str(year))
    sleep(2)

    # 월 선택
    month_select = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ui-datepicker-month"))
    )
    # 월은 0부터 시작하므로 1을 빼줌
    Select(month_select).select_by_value(str(month - 1))
    sleep(2)

    # 일자 선택
    day_cell = WebDriverWait(driver, TIMEOUT).until(
        EC.element_to_be_clickable((By.XPATH, f"//a[text()='{day}']"))
    )
    day_cell.click()
    sleep(2)

    # 3. 검색 버튼 클릭
    logger.info("Clicking search button")
    search_button = WebDriverWait(driver, TIMEOUT).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn_blue"))
    )
    search_button.click()
    sleep(3)


def crawl_daily_boxoffice(driver: webdriver.Chrome):
    ranking_dates = []
    for h4 in driver.find_elements(By.TAG_NAME, 'h4'):
        if h4.text.strip() == '':
            continue
        ranking_dates.append(to_ranking_date(h4.text.strip()))

    print(ranking_dates)

    for i, tbody in enumerate(driver.find_elements(By.TAG_NAME, 'tbody')):
        if tbody.text.strip() == '':
            break

        ranking_date = ranking_dates[i]
        for row in tbody.find_elements(By.TAG_NAME, 'tr'):
            row_data = {'ranking_date': ranking_date}
            for k, data in zip(dayily_boxoffice_parsing_funcs, row.find_elements(By.TAG_NAME, 'td')):
                func = dayily_boxoffice_parsing_funcs.get(k, None)
                row_data[k] = func(data.text.strip())

            row_data[
                'ranking_date_rank'] = f'{ranking_date.year}-{ranking_date.month:02d}-{ranking_date.day:02d}@{row_data['rank']:02d}'

            try:
                boxoffice = DailyBoxoffice(**row_data)
                boxoffice.save()
            except Exception as e:
                print(e)
                print(row_data)


def crawl_movie_info(driver: webdriver.Chrome, visited_movie_names: set):
    '''
        영화 상세페이지 클릭해서 크롤링
    '''
    inclease = 1
    for i, tbody in enumerate(driver.find_elements(By.TAG_NAME, 'tbody')):
        if tbody.text.strip() == '':
            break

        for a_tag in tbody.find_elements(By.TAG_NAME, 'a'):
            movie_name = a_tag.text.strip()
            if movie_name in visited_movie_names:
                continue

            visited_movie_names.add(movie_name)

            a_tag.click()
            sleep(1)

            bs = BeautifulSoup(driver.page_source, 'html.parser')
            span_text_set = set(span.text for span in bs.find_all('span'))
            is_now_showing = True if '영화상영관상영중' in span_text_set else False  # selenium xpath로 처리하면 span없을경우 타임아웃까지 오래기다림

            movie_infos = driver.find_element(By.XPATH,
                                              f'//*[@id="ui-id-{inclease}"]/div/div[1]/div[2]/dl').find_elements(
                By.TAG_NAME, 'dd')
            movie_id = movie_infos[0].text.strip()

            infos = movie_infos[3].text.strip().split('|')
            genre = infos[2].strip()
            nation = infos[5].strip()

            release_date = movie_infos[5].text.strip()

            img = driver.find_element(By.XPATH, f'//*[@id="ui-id-{inclease}"]/div/div[1]/div[2]/a/img')
            img_src = img.get_attribute('src').strip()

            release_date = to_datetime_KST(release_date) if release_date else None

            movie_data = {
                'movie_id': int(movie_id),  # 중복 입력 방지용
                'movie_name': movie_name,
                'genre': genre,
                'is_now_showing': is_now_showing,
                'nation': nation,
                'release_date': release_date,
                'movie_img': img_src,
            }

            try:
                MovieInfo(**movie_data).save()
            except Exception as e:
                print(e)
                print(movie_data)

            # close_btn = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[1]/a[2]/span')
            # close_btn.click()
            # sleep(1)

            # 상세페이지 닫기
            driver.find_element(By.XPATH, "//a[contains(@onclick, 'dtlRmAll')]").click()
            WebDriverWait(driver, 10).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "layer_popup"))
            )

            inclease += 2


def make_daily_boxoffice_fk():
    movie_name_to_movie = dict()
    for movie in MovieInfo.objects.all():
        movie_name_to_movie[movie.movie_name] = movie

    print(movie_name_to_movie)

    for daily_boxoffice in DailyBoxoffice.objects.all():
        daily_boxoffice.movie_id = movie_name_to_movie.get(daily_boxoffice.movie_name, None)
        daily_boxoffice.save()


def crawl(start_year, start_month, start_day):
    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
        driver.get('https://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do')
        driver.implicitly_wait(TIMEOUT)
        dt_start = datetime(start_year, start_month, start_day, tzinfo=KST)
        dt_now = datetime.now(KST)
        dt_yesterday = datetime(dt_now.year, dt_now.month, dt_now.day, tzinfo=KST) - timedelta(days=1)

        movie_name_set = set(MovieInfo.objects.all().values_list('movie_name', flat=True))

        dt = dt_start
        while dt <= dt_yesterday:
            print(dt)
            select_day(driver, dt.year, dt.month, dt.day)
            crawl_daily_boxoffice(driver)
            crawl_movie_info(driver, movie_name_set)
            dt += timedelta(days=7)

        make_daily_boxoffice_fk()


if __name__ == '__main__':
    crawl(2025, 1, 1)
