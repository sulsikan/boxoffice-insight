from datetime import datetime, timezone, timedelta

from IPython.core.usage import default_banner
from django.shortcuts import render

from korean_boxoffice.models import DailyBoxoffice

# Create your views here.
KST = timezone(timedelta(hours=+9))
default_dt = datetime(2025, 4, 16, tzinfo=KST)


def index(request):
    target_dt = f'{default_dt.year:04d}{default_dt.month:02d}{default_dt.day:02d}'
    context = {
        'year': default_dt.year,
        'target_date': int(target_dt),
    }
    print(target_dt)
    return render(request, 'korean_boxoffice/index.html', context=context)


def daily_boxoffice(request, target_date: int):
    str_target_date = str(target_date)
    year = int(str_target_date[:4])
    month = int(str_target_date[4:6])
    day = int(str_target_date[6:])
    target_dt = datetime(year=year, month=month, day=day, tzinfo=KST)

    # target_ranking_date = datetime(year, month, day, tzinfo=KST)
    # print(target_ranking_date)
    daily_boxoffices = DailyBoxoffice.objects.filter(ranking_date=target_dt)
    print(daily_boxoffices)
    context = {
        'my_text': 'hello world',
        'target_ranking_date': target_dt,
        'daily_boxoffices': daily_boxoffices

    }

    return render(request, 'korean_boxoffice/daily_boxoffice.html', context=context)
