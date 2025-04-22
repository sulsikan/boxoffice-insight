import logging
import traceback
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta, timezone
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

import os

TIMEOUT = 20  # 20초
logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boxoffice.settings")
import django

django.setup()
from korean_boxoffice.models import DailyBoxoffice

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


key_funcs = {
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


def crawl_korean_boxoffice(driver: webdriver.Chrome):
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
            for k, data in zip(key_funcs, row.find_elements(By.TAG_NAME, 'td')):
                func = key_funcs.get(k, None)
                row_data[k] = func(data.text.strip())

            row_data[
                'ranking_date_rank'] = f'{ranking_date.year}-{ranking_date.month:02d}-{ranking_date.day:02d}@{row_data['rank']:02d}'

            try:
                boxoffice = DailyBoxoffice(**row_data)
                boxoffice.save()
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                print(row_data)
                continue


if __name__ == '__main__':
    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
        driver.get('https://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do')
        driver.implicitly_wait(TIMEOUT)
        dt_start = datetime(2025, 1, 1, tzinfo=KST)
        now = datetime.now(KST)
        dt_end = datetime(now.year, now.month, now.day, tzinfo=KST)

        dt = dt_start
        print(dt)
        while dt < dt_end:
            print(dt)
            select_day(driver, dt.year, dt.month, dt.day)
            crawl_korean_boxoffice(driver)

            dt += timedelta(days=7)
