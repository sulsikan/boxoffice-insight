from datetime import datetime, timezone, timedelta
from django.http import Http404, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from rest_framework.status import HTTP_400_BAD_REQUEST

from korean_boxoffice.models import DailyBoxoffice, MovieInfo

# Create your views here.
KST = timezone(timedelta(hours=+9))


def index(request):
    return render(request, 'korean_boxoffice/index.html')


def daily_boxoffice(request):
    yesterday = datetime.now(KST) - timedelta(days=1)
    target_date = request.GET.get('target_date',
                                  f'{yesterday.year:04d}-{yesterday.month:02d}-{yesterday.day:02d}')  # 날자 정보 없으면 어제날자로

    try:
        year, month, day = [int(token) for token in target_date.split('-')]
        target_dt = datetime(year=year, month=month, day=day, tzinfo=KST)
    except Exception as e:
        print(e)
        return HttpResponseBadRequest('부적합한 요청 입니다.')

    daily_boxoffices = DailyBoxoffice.objects.filter(ranking_date=target_dt)
    if not daily_boxoffices:
        return HttpResponseNotFound('해당 데이터가 없습니다.')
        # raise Http404('데이터가 없습니다.')

    percent_total = sum(db.revenue_share for db in daily_boxoffices)
    etc_share = 100 - percent_total

    context = {
        'target_dt': target_dt,
        'target_date': f'{year:04d}-{month:02d}-{day:02d}',
        'daily_boxoffices': daily_boxoffices,
        'etc_share': etc_share
    }

    return render(request, 'korean_boxoffice/daily_boxoffice.html', context=context)


def movie_info(request, pk):
    movie_info = get_object_or_404(MovieInfo, pk=pk)

    return render(request, 'korean_boxoffice/movie_info.html', {'movie_info': movie_info})