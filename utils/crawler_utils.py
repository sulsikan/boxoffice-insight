import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict, List, Optional
import time
import logging

logger = logging.getLogger(__name__)

class KOBISCrawler:
    BASE_URL = "https://www.kobis.or.kr"
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """공통 요청 메서드"""
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def parse_date(self, date_str: str) -> datetime:
        """날짜 문자열을 datetime 객체로 변환"""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Expected format: YYYY-MM-DD")
    
    def get_week_number(self, date: datetime) -> int:
        """주차 계산"""
        return date.isocalendar()[1]
    
    def get_week_range(self, date: datetime) -> tuple:
        """해당 주의 시작일과 종료일 반환"""
        start = date - timedelta(days=date.weekday())
        end = start + timedelta(days=6)
        return start, end 