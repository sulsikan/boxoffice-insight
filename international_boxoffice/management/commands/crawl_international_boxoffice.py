from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from international_boxoffice.crawlers import InternationalBoxOfficeCrawler
from international_boxoffice.models import InternationalBoxOffice
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Crawl international box office data and save to database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--years',
            type=int,
            default=10,
            help='Number of years of data to crawl (default: 10)'
        )
    
    def handle(self, *args, **options):
        crawler = InternationalBoxOfficeCrawler()
        years = options['years']
        
        # 현재 날짜로부터 years년 전까지의 데이터 크롤링
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*years)
        
        try:
            # 데이터 크롤링
            df = crawler.get_historical_data(start_date, end_date)
            
            # DB에 저장
            for _, row in df.iterrows():
                InternationalBoxOffice.objects.update_or_create(
                    title=row['title'],
                    country=row['country'],
                    week=row['week'],
                    defaults={
                        'rank': row['rank'],
                        'release_date': datetime.strptime(row['release_date'], '%Y-%m-%d').date(),
                        'weekend_revenue': row['weekend_revenue'],
                        'total_revenue': row['total_revenue'],
                        'distributor': row['distributor']
                    }
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully crawled and saved {len(df)} records')
            )
        except Exception as e:
            logger.error(f"Error in crawl_international_boxoffice command: {e}")
            self.stdout.write(
                self.style.ERROR(f'Error occurred: {str(e)}')
            ) 