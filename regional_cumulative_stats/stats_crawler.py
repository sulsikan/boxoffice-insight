import os
import sys
import django
import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boxoffice.settings")
django.setup()

from regional_cumulative_stats.models import RegionalCumulativeStats

# 매출액/관객수 문자열에서 숫자와 점유율(%) 분리
def split_number_percent(value):
    match = re.match(r"([\d,]+)\s*\(([\d.]+)%\)", value)
    if match:
        num = int(match.group(1).replace(",", ""))
        percent = float(match.group(2))
        return num, percent
    return None, None

def crawl_and_save_all_movies():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://www.kobis.or.kr/kobis/business/stat/offc/findFormerBoxOfficeList.do")

    # 더보기 버튼
    for _ in range(4):
        try:
            more_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn_more"))
            )
            driver.execute_script("arguments[0].click();", more_button)
            time.sleep(1.5)
        except:
            break

    rows = driver.find_elements(By.CSS_SELECTOR, "table.tbl_comm tbody tr")

    for idx, row in enumerate(rows):
        try:
            link = row.find_element(By.CSS_SELECTOR, "a.boxMNm")
            title = link.text.strip()
            print(f"[{idx+1}] ▶ {title}")

            if RegionalCumulativeStats.objects.filter(title=title).exists():
                print(f"이미 저장된 영화 → 스킵: {title}")
                continue

            # 상세페이지 열기
            driver.execute_script("arguments[0].click();", link)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "wrap_tab"))
            )

            # 통계정보 탭 클릭
            try:
                stats_tab = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '통계정보')]"))
                )
                driver.execute_script("arguments[0].click();", stats_tab)
                print("통계정보 탭 클릭 완료")
            except Exception as e:
                print("통계정보 탭 클릭 실패:", e)
                driver.find_element(By.XPATH, "//a[contains(@onclick, 'dtlRmAll')]").click()
                continue

            # 지역별 누적통계 테이블 로딩 대기
            try:
                WebDriverWait(driver, 40).until(
                    EC.presence_of_element_located((By.XPATH, "//caption[contains(text(), '지역별 누적통계')]/following-sibling::thead"))
                )
                rows = driver.find_elements(By.XPATH, "//caption[contains(text(), '지역별 누적통계')]/following-sibling::tbody/tr")
                print("지역별 누적통계 테이블 로딩 완료")
            except Exception as e:
                print("지역별 누적통계 로딩 실패:", e)
                driver.find_element(By.XPATH, "//a[contains(@onclick, 'dtlRmAll')]").click()
                continue

            for tr in rows:
                tds = tr.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 4:
                    region = tds[0].text.strip()
                    screens = int(tds[1].text.strip().replace(",", ""))
                    revenue, revenue_share = split_number_percent(tds[2].text.strip())
                    audience, audience_share = split_number_percent(tds[3].text.strip())

                    try:
                        RegionalCumulativeStats.objects.create(
                            title=title,
                            region=region,
                            screens=screens,
                            revenue_total=revenue,
                            revenue_share=revenue_share,
                            audience_total=audience,
                            audience_share=audience_share
                        )
                        print(f"저장 성공: {title} - {region}")
                    except Exception as save_err:
                        print(f"저장 실패: {title} - {region} → {save_err}")

            # 팝업 닫기
            driver.find_element(By.XPATH, "//a[contains(@onclick, 'dtlRmAll')]").click()
            WebDriverWait(driver, 10).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "layer_popup"))
            )

        except Exception as e:
            print(f"오류 발생: {e}")
            continue

    driver.quit()
    print("모든 영화 저장 완료")

if __name__ == "__main__":
    crawl_and_save_all_movies()