from time import sleep

from numpy.version import release
from selenium import webdriver
from selenium.webdriver import ActionChains

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
    'movie_id': str_to_int,
    'movie_name': None,
    'release_date': to_datetime_KST,
    'genre': None,
    'is_now_showing' : None,
    'nation': None,
    'movie_img': None
}

if __name__ == '__main__':
    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
        driver.get('https://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do')
        driver.implicitly_wait(20)

        movie_names = set()

        inclease = 1
        for i, tbody in enumerate(driver.find_elements(By.TAG_NAME, 'tbody')):
            if tbody.text.strip() == '':
                break

            for a_tag in tbody.find_elements(By.TAG_NAME, 'a'):
                movie_name = a_tag.text.strip()
                if movie_name in movie_names:
                    continue

                movie_names.add(movie_name)

                ActionChains(driver).click(a_tag).perform()
                sleep(2)

                try:
                    is_now_showing= True if driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[1]/div/span').text else False
                except:
                    is_now_showing = False
                movie_id = driver.find_element(By.XPATH, f'//*[@id="ui-id-{inclease}"]/div/div[1]/div[2]/dl/dd[1]').text.strip()
                info=driver.find_element(By.XPATH, f'//*[@id="ui-id-{inclease}"]/div/div[1]/div[2]/dl/dd[4]').text.strip()
                release_date = driver.find_element(By.XPATH, f'//*[@id="ui-id-{inclease}"]/div/div[1]/div[2]/dl/dd[6]').text.strip()
                release_date =release_date if release_date else None
                print(is_now_showing, movie_id, release_date, info)


                close_btn = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[1]/a[2]/span')
                ActionChains(driver).click(close_btn).perform()
                sleep(3)
                inclease += 2



            break
