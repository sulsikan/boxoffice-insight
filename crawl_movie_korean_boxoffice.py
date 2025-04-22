from time import sleep
from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta, timezone

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boxoffice.settings")
import django

django.setup()
from crawl_korean_boxoffice import select_day, to_datetime_KST

from korean_boxoffice.models import Movie

KST = timezone(timedelta(hours=+9))


def crawl_movie(driver: webdriver.Chrome, visited_movie_names: set):
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
            sleep(2)
            try:
                is_now_showing = True if driver.find_element(By.XPATH,
                                                             '/html/body/div[3]/div[1]/div[1]/div/span') else False
            except:
                # 여기서 timeout까지 기다리기 때문에 시간이 좀 걸립니다.
                is_now_showing = False

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
                'movie_id': int(movie_id), # 중복 입력 방지용
                'movie_name': movie_name,
                'genre': genre,
                'is_now_showing': is_now_showing,
                'nation': nation,
                'release_date': release_date,
                'movie_img': img_src,
            }

            print(movie_data)
            try:
                Movie(**movie_data).save()
            except Exception as e:
                print(e)
                pass

            close_btn = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[1]/a[2]/span')
            close_btn.click()
            sleep(3)
            inclease += 2


if __name__ == '__main__':
    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
        driver.get('https://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do')
        driver.implicitly_wait(20)

        dt_start = datetime(2025, 1, 1, tzinfo=KST)
        now = datetime.now(KST)
        dt_end =datetime(now.year, now.month, now.day, tzinfo=KST)

        visited_movie_names = set()
        dt = dt_start
        while dt < dt_end:
            print(dt)
            select_day(driver, dt.year, dt.month, dt.day)
            crawl_movie(driver, visited_movie_names)
            dt += timedelta(days=7)
