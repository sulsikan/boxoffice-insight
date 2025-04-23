import logging
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta, timezone, date
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from korean_boxoffice.crawl_daily_boxoffice import str_to_int, to_datetime_KST, str_to_float, str_replace_symbol, \
    crawl_movie_info

import os
import sys

from korean_boxoffice.models import MonthlyBoxoffice, MovieInfo, AnnualBoxoffice

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)
TIMEOUT = 20  # 20초


def to_str_ranking_date_YYYY_MM(string):
    year, month = string.split()
    year = year[:-1]
    month = month[:-1]
    return f'{year}-{month}'


monthly_boxoffice_parsing_funcs = {
    'rank': str_to_int,
    'movie_name': str_replace_symbol,
    'release_date': to_datetime_KST,
    'revenue': str_to_int,
    'revenue_share': str_to_float,
    'revenue_cumulative': str_to_int,
    'moviegoers_num': str_to_int,
    'moviegoers_cumulative': str_to_int,
    'screens_num': str_to_int,
    'screenings_num': str_to_int,
}

annual_boxoffice_parsing_funcs = {
    'rank': str_to_int,
    'movie_name': str_replace_symbol,
    'release_date': to_datetime_KST,
    'revenue': str_to_int,
    'revenue_share': str_to_float,
    'moviegoers_num': str_to_int,
    'screens_num': str_to_int,
    'screenings_num': str_to_int,
}


def crawl_boxoffice_many(driver: webdriver.Chrome, parsing_funcs: dict):
    ranking_dates = []
    for h4 in driver.find_elements(By.TAG_NAME, 'h4'):
        if h4.text.strip() == '':
            continue
        ranking_dates.append(to_str_ranking_date_YYYY_MM(h4.text.strip()))

    print(ranking_dates)

    for i, tbody in enumerate(driver.find_elements(By.TAG_NAME, 'tbody')):
        if tbody.text.strip() == '':
            break

        ranking_date = ranking_dates[i]
        for row in tbody.find_elements(By.TAG_NAME, 'tr'):
            row_data = {'ranking_date': ranking_date}
            for k, data in zip(parsing_funcs, row.find_elements(By.TAG_NAME, 'td')):
                func = parsing_funcs.get(k, None)
                row_data[k] = func(data.text.strip())

            row_data[
                'ranking_date_rank'] = f'{ranking_date}@{row_data['rank']:02d}'

            try:
                boxoffice = MonthlyBoxoffice(**row_data)
                boxoffice.save()
            except Exception as e:
                print(e)
                print(row_data)


def crawl_boxoffice(driver: webdriver.Chrome, parsing_funcs: dict, ranking_date):
    tbody = driver.find_element(By.TAG_NAME, 'tbody')
    for row in tbody.find_elements(By.TAG_NAME, 'tr'):
        row_data = {'ranking_date': ranking_date}
        for k, data in zip(parsing_funcs, row.find_elements(By.TAG_NAME, 'td')):
            func = parsing_funcs.get(k, None)
            row_data[k] = func(data.text.strip())

        row_data[
            'ranking_date_rank'] = f'{ranking_date}@{row_data['rank']:02d}'

        try:
            boxoffice = AnnualBoxoffice(**row_data)
            boxoffice.save()
        except Exception as e:
            print(e)
            print(row_data)


def make_monthly_boxoffice_fk():
    movie_name_to_movie = dict()
    for movie in MovieInfo.objects.all():
        movie_name_to_movie[movie.movie_name] = movie

    print(movie_name_to_movie)

    for boxoffice in MonthlyBoxoffice.objects.all():
        boxoffice.movie_id = movie_name_to_movie.get(boxoffice.movie_name, None)
        boxoffice.save()


def make_annual_boxoffice_fk():
    movie_name_to_movie = dict()
    for movie in MovieInfo.objects.all():
        movie_name_to_movie[movie.movie_name] = movie

    print(movie_name_to_movie)

    for boxoffice in AnnualBoxoffice.objects.all():
        boxoffice.movie_id = movie_name_to_movie.get(boxoffice.movie_name, None)
        boxoffice.save()


def crawl_monthly_boxoffice(start_year: int, start_month: int):
    start_year = f'{start_year:04d}'
    start_month = f'{start_month:02d}'
    options = webdriver.ChromeOptions()
    with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) as driver:
        driver.get("https://www.kobis.or.kr/kobis/business/stat/boxs/findMonthlyBoxOfficeList.do")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "sSearchYearFrom")))
        driver.execute_script(f"document.getElementById('sSearchYearFrom').value = '{start_year}'")
        driver.execute_script(f"document.getElementById('sSearchMonthFrom').value = '{start_month}'")
        driver.find_element(By.XPATH, "//button[text()='조회']").click()
        sleep(10)  # 한번에 많은 월간데이터 긁어올경우 많이 늘려줘야 한다.

        crawl_boxoffice_many(driver, monthly_boxoffice_parsing_funcs)

        movie_name_set = set(MovieInfo.objects.all().values_list('movie_name', flat=True))
        crawl_movie_info(driver, movie_name_set)
        make_monthly_boxoffice_fk()


def crawl_annual_boxoffice(start_year: int):
    end_year = datetime.now().year
    options = webdriver.ChromeOptions()
    with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) as driver:
        driver.get("https://www.kobis.or.kr/kobis/business/stat/boxs/findYearlyBoxOfficeList.do")
        movie_name_set = set(MovieInfo.objects.all().values_list('movie_name', flat=True))

        for year in range(start_year, end_year + 1):
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "sSearchYearFrom")))
            driver.execute_script(f"document.getElementById('sSearchYearFrom').value = '{year}'")
            driver.find_element(By.XPATH, "//button[text()='조회']").click()
            sleep(10)  # 한번에 많은 월간데이터 긁어올경우 많이 늘려줘야 한다.

            crawl_boxoffice(driver, annual_boxoffice_parsing_funcs, year)

            crawl_movie_info(driver, movie_name_set)
            make_annual_boxoffice_fk()


if __name__ == '__main__':
    crawl_monthly_boxoffice(2024, 1)  # 인자 월
    crawl_annual_boxoffice(2010)
