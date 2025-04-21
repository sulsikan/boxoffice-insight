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
from regional_cumulative_stats.models import RegionalCumulativeStats
import pandas as pd
import time
import re

# 매출액/관객수 문자열에서 숫자와 점유율(%) 분리
def split_number_percent(value):
    match = re.match(r"([\d,]+)\s*\(([\d.]+)%\)", value)
    if match:
        num = int(match.group(1).replace(",", ""))
        percent = float(match.group(2))
        return pd.Series([num, percent])
    else:
        return pd.Series([None, None])

# 수치 문자열 → 정수형으로 변환, 컬럼 정리
def clean_and_convert(df):
    df["스크린수"] = df["스크린수"].str.replace(",", "").astype(int)
    df[["누적매출액(원)", "매출점유율(%)"]] = df["누적매출액"].apply(split_number_percent)
    df[["누적관객수(명)", "관객점유율(%)"]] = df["누적관객수"].apply(split_number_percent)
    df["누적매출액(원)"] = df["누적매출액(원)"].astype("int64")
    df["누적관객수(명)"] = df["누적관객수(명)"].astype("int64")
    df = df.drop(columns=["누적매출액", "누적관객수"])
    return df

# 전체 영화의 지역별 누적통계 크롤링 함수
def crawl_all_movie_area_stats():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.kobis.or.kr/kobis/business/stat/offc/findFormerBoxOfficeList.do")

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table.tbl_comm tbody tr"))
    )
    rows = driver.find_elements(By.CSS_SELECTOR, "table.tbl_comm tbody tr")

    all_data = []

    for idx, row in enumerate(rows):
        try:
            link = row.find_element(By.CSS_SELECTOR, "a.boxMNm")
            title = link.text.strip()
            print(f"[{idx + 1}] ▶ {title}")

            driver.execute_script("arguments[0].click();", link)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "wrap_tab"))
            )
            time.sleep(1)

            try:
                stats_tab = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '통계정보')]"))
                )
                driver.execute_script("arguments[0].click();", stats_tab)
            except Exception as e:
                close_btn = driver.find_element(By.XPATH, "//a[@class='close' and contains(@onclick, 'dtlRmAll')]")
                driver.execute_script("arguments[0].click();", close_btn)
                WebDriverWait(driver, 10).until_not(
                    EC.presence_of_element_located((By.CLASS_NAME, "layer_popup"))
                )
                continue

            try:
                WebDriverWait(driver, 25).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//caption[contains(text(), '지역별 누적통계')]/following-sibling::thead")
                    )
                )
                table_rows = driver.find_elements(
                    By.XPATH,
                    "//caption[contains(text(), '지역별 누적통계')]/following-sibling::tbody/tr"
                )
                print("지역별 누적통계 테이블 로딩 완료")
            except Exception as e:
                print(f"지역별 누적통계 로딩 실패: {e}")
                close_btn = driver.find_element(By.XPATH, "//a[@class='close' and contains(@onclick, 'dtlRmAll')]")
                driver.execute_script("arguments[0].click();", close_btn)
                WebDriverWait(driver, 10).until_not(
                    EC.presence_of_element_located((By.CLASS_NAME, "layer_popup"))
                )
                continue

            for tr in table_rows:
                tds = tr.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 4:
                    지역 = tds[0].text.strip()
                    스크린수 = tds[1].text.strip()
                    누적매출액 = tds[2].text.strip()
                    누적관객수 = tds[3].text.strip()
                    all_data.append({
                        "제목": title,
                        "지역": 지역,
                        "스크린수": 스크린수,
                        "누적매출액": 누적매출액,
                        "누적관객수": 누적관객수
                    })

            close_btn = driver.find_element(By.XPATH, "//a[@class='close' and contains(@onclick, 'dtlRmAll')]")
            driver.execute_script("arguments[0].click();", close_btn)
            WebDriverWait(driver, 10).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "layer_popup"))
            )

        except Exception as e:
            print(f"오류 발생: {e}")
            continue

    driver.quit()
    df = pd.DataFrame(all_data)
    df = clean_and_convert(df)
    return df

def save_to_db(df):
    for _, row in df.iterrows():
        try:
            RegionalCumulativeStats.objects.create(
                제목=row["제목"],
                지역=row["지역"],
                스크린수=row["스크린수"],
                누적매출액=row["누적매출액(원)"],
                매출점유율=row["매출점유율(%)"],
                누적관객수=row["누적관객수(명)"],
                관객점유율=row["관객점유율(%)"],
            )
        except Exception as e:
            print(f"❌ 저장 실패: {row['제목']} - {row['지역']} → {e}")

if __name__ == "__main__":
    df = crawl_all_movie_area_stats()
    df = clean_and_convert(df)
    save_to_db(df)
    print("모든 데이터를 DB에 저장 완료!")