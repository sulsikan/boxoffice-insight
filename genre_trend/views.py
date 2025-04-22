from django.http import HttpResponse
from django.shortcuts import render

from genre_trend.models import MovieBasicInfo


def index(request):
    return render(request,'base.html')
def genre_stat(request):

    movies = MovieBasicInfo.objects.all()
    data = {}
    for movie in movies :
        genres = movie.genre.split(",")
        for genre in genres :
            genre = genre.strip()
            data[genre] = data.get(genre, 0) +1
    context = {
        'labels': list(data.keys()),
        'values': list(data.values()),
    }
    return render(request,'genre_stat.html', context)
