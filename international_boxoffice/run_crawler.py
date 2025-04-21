import logging
from datetime import datetime, timedelta
import time
import sys
import os
import django

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boxoffice.settings')
django.setup()

from international_boxoffice.crawlers import InternationalBoxOfficeCrawler

def collect_monthly_data(year: int, month: int, country: str):
    # 크롤러 인스턴스 생성 (CSV 저장 비활성화)
    crawler = InternationalBoxOfficeCrawler(save_to_csv=False)
    
    # 해당 월의 1일로 설정
    start_date = datetime(year, month, 1)
    
    try:
        logger.info(f"Collecting data for {country} starting from {start_date}")
        crawler.get_weekly_boxoffice(country, start_date)
        time.sleep(5)  # 서버 부하 방지를 위한 대기
    except Exception as e:
        logger.error(f'Error collecting data for {year}-{month:02d}: {str(e)}')
        time.sleep(10)  # 에러 발생 시 더 긴 대기 시간

def collect_year_data(year: int, start_month: int, end_month: int, country: str):
    logger.info(f"Starting data collection for {year} from month {start_month} to {end_month}")
    
    for month in range(start_month, end_month + 1):
        logger.info(f"Processing {year}-{month:02d}")
        collect_monthly_data(year, month, country)

if __name__ == '__main__':
    # 2017년 1월부터 12월까지 데이터 수집 (CSV 저장 없이)
    collect_year_data(2017, 1, 12, 'US') 