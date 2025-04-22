# 임시로 사용되는 코드
# crawl_info.py에서 rank 데이터가 제대로 안받아와지면 해당 코드로 따로 넣어주기 
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boxoffice.settings")
django.setup()

from .models import Movie

# 모든 영화 데이터를 개봉일 기준으로 정렬 (원하는 기준으로 정렬 가능)
movies = Movie.objects.all().order_by('id')

# 순위 넣기
for idx, movie in enumerate(movies, start=1):
    movie.rank = idx
    movie.save()
