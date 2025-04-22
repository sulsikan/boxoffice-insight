import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boxoffice.settings")
import django

django.setup()

from korean_boxoffice.models import Movie, DailyBoxoffice

if __name__ == '__main__':
    # 영화상세페이지와 박스오피스에 나오는 이름이 조금 다르면 fk로 연결이 안됨
    # ex)
    # 레드벨벳 해피니스 다이어리 : 마이 디어 레베럽 인 시네마
    # 레드벨벳 해피니스 다이어리 : 마이 디어, 레베럽 인 시네마

    movie_name_to_movie = dict()
    for movie in Movie.objects.all():
        movie_name_to_movie[movie.movie_name] = movie

    for daily_boxoffice in DailyBoxoffice.objects.all():
        daily_boxoffice.movie_id = movie_name_to_movie.get(daily_boxoffice.movie_name, None)
        daily_boxoffice.save()
