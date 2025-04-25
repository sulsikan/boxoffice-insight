from datetime import datetime, timezone, timedelta
from django.http import Http404, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from rest_framework.status import HTTP_400_BAD_REQUEST

from korean_boxoffice.models import DailyBoxoffice, MovieInfo, MonthlyBoxoffice, AnnualBoxoffice

# Create your views here.
KST = timezone(timedelta(hours=+9))


def index(request):
    return render(request, 'korean_boxoffice/index.html')


def daily_boxoffice(request):
    # yesterday = datetime.now(KST) - timedelta(days=1)
    # target_date = request.GET.get('target_date',
    #                               f'{yesterday.year:04d}-{yesterday.month:02d}-{yesterday.day:02d}')  # 날자 정보 없으면 어제날자로

    target_date = request.GET.get('target_date',
                                  '2025-01-01')  # 날자 정보 없으면 크롤링 시작날로


    try:
        year, month, day = [int(token) for token in target_date.split('-')]
        target_dt = datetime(year=year, month=month, day=day, tzinfo=KST)
    except Exception as e:
        print(e)
        return HttpResponseBadRequest('부적합한 요청 입니다.')

    boxoffices = DailyBoxoffice.objects.filter(ranking_date=target_dt).order_by('rank')[:10]
    if not boxoffices:
        return HttpResponseNotFound('해당 데이터가 없습니다.')
        # raise Http404('데이터가 없습니다.')

    percent_total = sum(db.revenue_share for db in boxoffices)
    etc_share = 100 - percent_total

    context = {
        'target_dt': target_dt,
        'target_date': f'{year:04d}-{month:02d}-{day:02d}',
        'boxoffices': boxoffices,
        'etc_share': round(etc_share, 3)
    }

    return render(request, 'korean_boxoffice/daily_boxoffice.html', context=context)


def monthly_boxoffice(request):
    yesterday = datetime.now(KST) - timedelta(days=1)
    target_date = request.GET.get('target_date',
                                  f'{yesterday.year:04d}-{yesterday.month:02d}')  # 날자 정보 없으면 어제날자로

    try:
        str_year, str_month = target_date.split('-')
        year = int(str_year)
        month = int(str_month)
        day = 1
        target_dt = datetime(year=year, month=month, day=day, tzinfo=KST)
    except Exception as e:
        print(e)
        return HttpResponseBadRequest('부적합한 요청 입니다.')

    target_date = f'{year:04d}-{month:02d}'
    boxoffices = MonthlyBoxoffice.objects.filter(ranking_date=target_date).order_by('rank')[:10]
    if not boxoffices:
        return HttpResponseNotFound('해당 데이터가 없습니다.')
        # raise Http404('데이터가 없습니다.')

    percent_total = sum(db.revenue_share for db in boxoffices)
    etc_share = 100 - percent_total

    select_dates = sorted(set(MonthlyBoxoffice.objects.values_list('ranking_date', flat=True)), reverse=True)[:24]
    context = {
        'target_dt':target_dt,
        'target_date': target_date,
        'select_dates': select_dates,
        'boxoffices': boxoffices,
        'etc_share': round(etc_share, 3)
    }

    return render(request, 'korean_boxoffice/monthly_boxoffice.html', context=context)


def annual_boxoffice(request):
    yesterday = datetime.now(KST) - timedelta(days=1)
    target_date = request.GET.get('target_date',
                                  f'{yesterday.year:04d}')  # 날자 정보 없으면 어제날자로

    try:
        year = int(target_date)
        target_dt = datetime(year=year, month=1, day=1, tzinfo=KST)
    except Exception as e:
        print(e)
        return HttpResponseBadRequest('부적합한 요청 입니다.')

    boxoffices = AnnualBoxoffice.objects.filter(ranking_date=target_date).order_by('rank')[:10]
    if not boxoffices:
        return HttpResponseNotFound('해당 데이터가 없습니다.')
        # raise Http404('데이터가 없습니다.')

    percent_total = sum(db.revenue_share for db in boxoffices)
    etc_share = 100 - percent_total

    select_dates = [str(i) for i in range(yesterday.year, 2010 - 1, -1)]


    context = {
        'target_dt': target_dt,
        'target_date': target_date,
        'select_dates': select_dates,
        'boxoffices': boxoffices,
        'etc_share': round(etc_share, 3)
    }

    return render(request, 'korean_boxoffice/annual_boxoffice.html', context=context)

def movie_info(request, pk):
    movie_info = get_object_or_404(MovieInfo, pk=pk)
    context = {
        'movie_info': movie_info,
        'release_date': movie_info.release_date.astimezone(KST) if movie_info.release_date else None   ,
    }

    return render(request, 'korean_boxoffice/movie_info.html', context=context)