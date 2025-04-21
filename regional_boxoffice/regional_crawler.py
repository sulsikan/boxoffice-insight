import os
import sys
import django

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boxoffice.settings")
django.setup()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from regional_boxoffice.models import RegionalBoxOffice
from datetime import date, timedelta, datetime
import pandas as pd
import time

def crawl_regional(start_date, end_date):
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.kobis.or.kr/kobis/business/stat/them/findAreaShareList.do")  # ✅ URL 오타 수정됨

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "sSearchFrom")))
    driver.execute_script(f"document.getElementById('sSearchFrom').value = '{start_date}'")
    driver.execute_script(f"document.getElementById('sSearchTo').value = '{end_date}'")
    driver.find_element(By.XPATH, "//button[text()='조회']").click()
    time.sleep(5)

    rows = driver.find_elements(By.CSS_SELECTOR, "table.tbl_comm tbody tr")
    result = []

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) == 13:
            values = [col.text.strip().replace(",", "").replace("%", "") for col in cols]
            result.append([
                values[0], 
                int(values[1]), int(values[2]), int(values[3]), float(values[4]),
                int(values[5]), int(values[6]), int(values[7]), float(values[8]),
                int(values[9]), int(values[10]), int(values[11]), float(values[12])
            ])

    driver.quit()

    df = pd.DataFrame(result, columns=[
        "지역",
        "한국_상영편수", "한국_매출액", "한국_관객수", "한국_점유율",
        "외국_상영편수", "외국_매출액", "외국_관객수", "외국_점유율",
        "전체_상영편수", "전체_매출액", "전체_관객수", "전체_점유율"
    ])

    return df


def save_df_to_db(df, 기준_시작일, 기준_종료일):
    for _, row in df.iterrows():
        RegionalBoxOffice.objects.create(
            기준_시작일=기준_시작일,
            기준_종료일=기준_종료일,
            지역=row["지역"],
            한국_상영편수=row["한국_상영편수"],
            한국_매출액=row["한국_매출액"],
            한국_관객수=row["한국_관객수"],
            한국_점유율=row["한국_점유율"],
            외국_상영편수=row["외국_상영편수"],
            외국_매출액=row["외국_매출액"],
            외국_관객수=row["외국_관객수"],
            외국_점유율=row["외국_점유율"],
            전체_상영편수=row["전체_상영편수"],
            전체_매출액=row["전체_매출액"],
            전체_관객수=row["전체_관객수"],
            전체_점유율=row["전체_점유율"],
        )


def crawl_yearly_by_month(year):
    today = date.today()
    yesterday = today - timedelta(days=1)

    for month in range(1, 13):
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(year, month + 1, 1) - timedelta(days=1)

        if end > yesterday:
            end = yesterday

        if start > end:
            continue

        print(f"{start} ~ {end} 크롤링 중...")

        df = crawl_regional(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

        if df is not None and not df.empty:
            save_df_to_db(df, 기준_시작일=start, 기준_종료일=end)
            print(f"{start.month}월 데이터 저장 완료")
        else:
            print(f"{start.month}월 데이터 없음")

if __name__ == "__main__":
    crawl_yearly_by_month(year=2023)
