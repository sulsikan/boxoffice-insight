from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta, timezone

import os

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

with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
    driver.get('https://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do')
    driver.implicitly_wait(20)

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

            print(row_data)
            row_data['ranking_date_rank'] = f"{ranking_date.year}-{ranking_date.month:02d}-{ranking_date.day:02d}@{row_data['rank']:02d}"

            boxoffice = DailyBoxoffice(**row_data)
            boxoffice.save()