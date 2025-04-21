from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re

def crawl_movie_area_stats():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://www.kobis.or.kr/kobis/business/stat/offc/findFormerBoxOfficeList.do")

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick, \"mstView('movie','20129370')\")]"))
    ).click()

    time.sleep(5)

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@class='tab' and contains(text(), '통계정보')]"))
    ).click()

    time.sleep(5)

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//table[@class='tbl_comm' and .//caption[contains(text(), '지역별 누적통계')]]/tbody/tr")
        )
    )

    rows = driver.find_elements(
        By.XPATH,
        "//table[@class='tbl_comm' and .//caption[contains(text(), '지역별 누적통계')]]/tbody/tr"
    )

    result = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 4:
            지역 = cols[0].text.strip()
            스크린수 = cols[1].text.strip()
            누적매출액 = cols[2].text.strip()
            누적관객수 = cols[3].text.strip()
            result.append([지역, 스크린수, 누적매출액, 누적관객수])

    driver.quit()

    df = pd.DataFrame(result, columns=["지역", "스크린수", "누적매출액", "누적관객수"])
    return df

def clean_and_convert(df):
    df["스크린수"] = df["스크린수"].str.replace(",", "").astype(int)

    def split_number_percent(value):
        match = re.match(r"([\d,]+)\s*\(([\d.]+)%\)", value)
        if match:
            num = int(match.group(1).replace(",", ""))
            percent = float(match.group(2))
            return pd.Series([num, percent])
        else:
            return pd.Series([None, None])

    df[["누적매출액(원)", "매출점유율(%)"]] = df["누적매출액"].apply(split_number_percent)
    df[["누적관객수(명)", "관객점유율(%)"]] = df["누적관객수"].apply(split_number_percent)

    df["누적매출액(원)"] = df["누적매출액(원)"].astype("int64")
    df["누적관객수(명)"] = df["누적관객수(명)"].astype("int64")

    df = df.drop(columns=["누적매출액", "누적관객수"])
    return df

if __name__ == "__main__":
    df = crawl_movie_area_stats()
    df = clean_and_convert(df)
    print(df.head())
    print(df.dtypes)