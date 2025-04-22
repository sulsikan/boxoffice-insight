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

def collect_data_for_month(year: int, month: int, crawler: InternationalBoxOfficeCrawler) -> None:
    """한 달의 모든 국가 박스오피스 데이터를 수집"""
    date = datetime(year, month, 1)
    countries = ["US", "UK", "DE", "JP"]
    
    logger.info(f"Collecting data for {year}-{month:02d}")
    
    for country in countries:
        try:
            logger.info(f"Processing {country} for {year}-{month:02d}")
            crawler.get_weekly_boxoffice(country, date)
            logger.info(f"Successfully collected data for {country} - {year}-{month:02d}")
            time.sleep(2)  # 국가 간 전환 시 2초 대기
        except Exception as e:
            logger.error(f"Failed to collect data for {country} - {year}-{month:02d}: {str(e)}")
            continue

if __name__ == "__main__":
    crawler = InternationalBoxOfficeCrawler()
    
    try:
        # 2015년부터 2024년까지 데이터 수집
        for year in range(2014, 2025):
            for month in range(1, 13):
                try:
                    collect_data_for_month(year, month, crawler)
                    logger.info(f"Completed data collection for {year}-{month:02d}")
                    time.sleep(5)  # 다음 달로 넘어가기 전 5초 대기
                except Exception as e:
                    logger.error(f"Error collecting data for {year}-{month:02d}: {str(e)}")
                    time.sleep(10)  # 에러 발생 시 대기 시간 증가
                    continue
        
        # 2025년 1월부터 4월까지 데이터 수집
        for month in range(1, 5):
            try:
                collect_data_for_month(2025, month, crawler)
                logger.info(f"Completed data collection for 2025-{month:02d}")
                time.sleep(5)  # 다음 달로 넘어가기 전 5초 대기
            except Exception as e:
                logger.error(f"Error collecting data for 2025-{month:02d}: {str(e)}")
                time.sleep(10)  # 에러 발생 시 대기 시간 증가
                continue
                
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
    finally:
        if crawler.driver:
            crawler.driver.quit()
            crawler.driver = None 