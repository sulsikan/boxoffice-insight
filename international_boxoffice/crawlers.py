from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from utils.crawler_utils import KOBISCrawler
import logging
import time
import subprocess
import platform
import os
from selenium.webdriver.common.keys import Keys
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from .models import InternationalBoxOffice
from django.db import transaction
from selenium.webdriver.support.ui import Select

logger = logging.getLogger(__name__)

class InternationalBoxOfficeCrawler(KOBISCrawler):
    """해외 박스오피스 데이터 크롤러"""
    
    COUNTRIES = {
        'US': ('미국', 'a[href="#tab1"]', '$'),
        'UK': ('영국', 'a[href="#tab2"]', '£'),
        'DE': ('독일', 'a[href="#tab3"]', '€'),
        'JP': ('일본', 'a[href="#tab5"]', '¥')
    }
    
    def __init__(self, save_to_csv=False):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://www.kobis.or.kr/kobis/business/stat/boxs/findWeekendForeignBoxOfficeList.do"
        self.driver = None
        self.current_currency = None
        self.save_to_csv = save_to_csv  # CSV 저장 여부 설정
    
    def _get_chrome_path(self):
        """시스템에 맞는 Chrome 경로 반환"""
        if platform.system() == 'Darwin':  # macOS
            return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        return 'google-chrome'
    
    def _setup_driver(self):
        """Selenium 웹드라이버 설정"""
        if self.driver is None:
            options = webdriver.ChromeOptions()
            # options.add_argument('--headless')  # 디버깅을 위해 헤드리스 모드 비활성화
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            # ChromeDriver 설정
            service = Service('/usr/local/bin/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.maximize_window()  # 창 최대화
            self.logger.info("ChromeDriver initialized successfully")
    
    def _parse_movie_data(self, row) -> Dict:
        """영화 데이터 파싱"""
        try:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) < 6:
                return None
            
            # 수입 데이터 정제
            def clean_revenue(text: str) -> float:
                if not text or text.strip() == '-':
                    return 0.0
                
                # Remove currency symbols and commas
                cleaned = text.replace('$', '').replace('£', '').replace('€', '').replace('¥', '').replace(',', '').strip()
                
                try:
                    return float(cleaned)
                except ValueError as e:
                    print(f"Error cleaning revenue: {text} -> {cleaned}")
                    print(f"Error details: {str(e)}")
                    return 0.0
            
            # 통화 기호 추출
            def extract_currency_symbol(text: str) -> str:
                if '$' in text:
                    return '$'
                elif '£' in text:
                    return '£'
                elif '€' in text:
                    return '€'
                elif '¥' in text:
                    return '¥'
                return '$'  # 기본값
            
            weekend_revenue_text = cells[3].text.strip()
            total_revenue_text = cells[4].text.strip()
                
            return {
                'rank': int(cells[0].text.strip() or '0'),
                'title': cells[1].text.strip(),
                'release_date': cells[2].text.strip(),
                'weekend_revenue': clean_revenue(weekend_revenue_text),
                'weekend_revenue_currency': extract_currency_symbol(weekend_revenue_text),
                'total_revenue': clean_revenue(total_revenue_text),
                'total_revenue_currency': extract_currency_symbol(total_revenue_text),
                'distributor': cells[5].text.strip()
            }
        except Exception as e:
            logger.error(f"Error parsing movie data: {e}")
            return None
    
    def _save_to_db(self, movies_data: List[Dict], country: str, date: datetime) -> None:
        """데이터를 DB에 저장"""
        try:
            with transaction.atomic():
                for movie_data in movies_data:
                    # release_date 문자열을 date 객체로 변환
                    release_date_str = movie_data['release_date']
                    try:
                        if isinstance(release_date_str, str):
                            try:
                                release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
                            except ValueError:
                                release_date = datetime.strptime(release_date_str, '%Y.%m.%d').date()
                        else:
                            release_date = release_date_str
                    except ValueError as e:
                        logger.error(f"Error parsing release date {release_date_str}: {e}")
                        continue

                    try:
                        # DB에 저장
                        InternationalBoxOffice.objects.update_or_create(
                            country=country,
                            year=movie_data['year'],  # 파싱한 연도 사용
                            week=movie_data['week_number'],
                            title=movie_data['title'],
                            defaults={
                                'rank': movie_data['rank'],
                                'release_date': release_date,
                                'weekend_revenue': movie_data['weekend_revenue'],
                                'weekend_revenue_currency': movie_data['weekend_revenue_currency'],
                                'total_revenue': movie_data['total_revenue'],
                                'total_revenue_currency': movie_data['total_revenue_currency'],
                                'distributor': movie_data['distributor'],
                            }
                        )
                    except Exception as e:
                        logger.error(f"Error saving movie {movie_data['title']} to database: {e}")
                        continue

                logger.info(f"Saved {len(movies_data)} movies to database")
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            raise
    
    def _save_to_csv(self, movies_data: List[Dict], country: str, date: datetime) -> None:
        """데이터를 CSV 파일로 저장"""
        if not self.save_to_csv:  # CSV 저장이 비활성화되어 있으면 DB만 저장
            self._save_to_db(movies_data, country, date)
            return
            
        try:
            # 데이터프레임 생성
            df = pd.DataFrame(movies_data)
            
            # 날짜 정보 추가
            df['country'] = country
            df['year'] = date.year
            df['week_number'] = df['week_number']
            df['week_start_date'] = df['week_start_date']
            
            # CSV 파일 저장
            os.makedirs('data/international_boxoffice', exist_ok=True)
            filename = f'data/international_boxoffice/{country}_{date.strftime("%Y%m%d")}_week{df.iloc[0]["week_number"]}.csv'
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"Data saved to {filename}")
            
            # DB에도 저장
            self._save_to_db(movies_data, country, date)
            
        except Exception as e:
            logger.error(f"Error saving data to CSV: {e}")
            raise
    
    def get_weekly_boxoffice(self, country: str, date: datetime) -> None:
        """특정 국가의 주간 박스오피스 데이터 수집"""
        try:
            self.logger.info(f"Fetching box office data for {country} from {date}")
            
            # Set up driver and load URL
            if not self.driver:
                self._setup_driver()
            
            # Load the page
            self.logger.info(f"Loading URL: {self.base_url}")
            self.driver.get(self.base_url)
            time.sleep(5)  # 페이지 로딩 대기 시간 증가
            
            # Set currency symbol based on country
            self.current_currency = self.COUNTRIES[country][2]
            self.logger.info(f"Setting currency symbol to: {self.current_currency}")
            
            try:
                # 1. 국가 탭 선택 전에 페이지가 완전히 로드될 때까지 대기
                country_selector = self.COUNTRIES[country][1]
                self.logger.info(f"Waiting for country tab: {country_selector}")
                country_tab = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, country_selector))
                )
                self.driver.execute_script("arguments[0].click();", country_tab)
                time.sleep(3)

                # 2. 날짜 선택 시작
                self.logger.info(f"Setting date to: {date.strftime('%Y-%m-%d')}")
                
                # 달력 아이콘 찾기 (label.btn_cal > span.ico_comm)
                calendar_icon = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "label.btn_cal span.ico_comm"))
                )
                calendar_icon.click()
                time.sleep(2)

                # 년도 선택
                year_select = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ui-datepicker-year"))
                )
                # Select 요소 생성
                Select(year_select).select_by_value(str(date.year))
                time.sleep(2)

                # 월 선택
                month_select = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ui-datepicker-month"))
                )
                # 월은 0부터 시작하므로 1을 빼줌
                Select(month_select).select_by_value(str(date.month - 1))
                time.sleep(2)

                # 일자 선택
                day_cell = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//a[text()='{date.day}']"))
                )
                day_cell.click()
                time.sleep(2)

                # 3. 검색 버튼 클릭
                self.logger.info("Clicking search button")
                search_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "btn_blue"))
                )
                search_button.click()
                time.sleep(3)

                # 4. 주차별 데이터 수집
                week_headers = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.board_tit h4"))
                )
                
                all_movies_data = []
                for week_header in week_headers:
                    # 주차 정보 파싱 (예: "87주차 (2015년 02월 13일 ~ 2015년 02월 15일)")
                    header_text = week_header.text
                    self.logger.info(f"Processing week: {header_text}")
                    
                    # 년도와 날짜 정보 추출
                    import re
                    match = re.search(r'(\d+)주차 \((\d{4})년 (\d{2})월 (\d{2})일 ~ .*?\)', header_text)
                    if match:
                        week_num = int(match.group(1))
                        year = int(match.group(2))
                        month = int(match.group(3))
                        day = int(match.group(4))
                        week_date = datetime(year, month, day)
                    else:
                        self.logger.warning(f"Could not parse date from header: {header_text}")
                        continue

                    # 해당 주차의 테이블 찾기
                    table = week_header.find_element(By.XPATH, "following::table[contains(@class, 'tbl_comm')]")
                    
                    # 영화 데이터 파싱
                    rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row
                    week_movies_data = []
                    for row in rows:
                        movie_data = self._parse_movie_data(row)
                        if movie_data:
                            # 주차 정보 추가
                            movie_data['week_number'] = week_num
                            movie_data['week_start_date'] = week_date.strftime('%Y-%m-%d')
                            movie_data['year'] = year  # 파싱한 연도 정보 추가
                            week_movies_data.append(movie_data)
                    
                    if week_movies_data:
                        self.logger.info(f"Found {len(week_movies_data)} movies for week {week_num}")
                        # 각 주차별로 CSV 저장
                        self._save_to_csv(week_movies_data, country, week_date)
                        all_movies_data.extend(week_movies_data)
                    else:
                        self.logger.warning(f"No movie data found for week {week_num}")
                
                if not all_movies_data:
                    self.logger.warning("No movie data found in any week")
                else:
                    self.logger.info(f"Total movies found: {len(all_movies_data)}")
                
            except Exception as e:
                self.logger.error(f"Error during web interaction: {str(e)}")
                raise
            
        except Exception as e:
            self.logger.error(f"Error fetching weekly boxoffice for {country}: {str(e)}")
            raise
        finally:
            # Close the browser
            if self.driver:
                self.driver.quit()
                self.driver = None
        
    def get_historical_data(self, start_year: int, end_year: int, countries: Optional[List[str]] = None) -> None:
        """여러 연도의 데이터를 수집"""
        if countries is None:
            countries = list(self.COUNTRIES.keys())
        
        for year in range(start_year, end_year + 1):
            try:
                logger.info(f"Processing year {year}")
                start_date = datetime(year, 1, 1)
                end_date = datetime(year, 12, 31)
                current_date = start_date
                
                while current_date <= end_date:
                    for country in countries:
                        try:
                            self.get_weekly_boxoffice(country, current_date)
                            time.sleep(2)  # 서버 부하 방지
                        except Exception as e:
                            logger.error(f"Error processing {country} for {current_date}: {e}")
                            time.sleep(5)  # 에러 발생 시 대기 시간 증가
                    current_date += timedelta(days=7)
                    
            except Exception as e:
                logger.error(f"Error processing year {year}: {e}")
                time.sleep(10)  # 에러 발생 시 대기 시간 증가 