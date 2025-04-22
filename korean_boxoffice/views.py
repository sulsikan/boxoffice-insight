from datetime import datetime, timezone, timedelta
from django.shortcuts import render

from korean_boxoffice.models import DailyBoxoffice

# Create your views here.
KST = timezone(timedelta(hours=+9))
def index(request):
    context = {
        'my_text':'hello world',
    }
    return render(request, 'korean_boxoffice/index.html', context=context)

def daily_boxoffice(request):
    target_ranking_date = datetime(2025, 4, 16, tzinfo=KST)
    print(target_ranking_date)
    daily_boxoffices = DailyBoxoffice.objects.filter(ranking_date = target_ranking_date)
    print(daily_boxoffices)
    context = {
        'my_text': 'hello world',
        'target_ranking_date': target_ranking_date,
        'daily_boxoffices':daily_boxoffices

    }

    dbo=  daily_boxoffices[0]
    return render(request, 'korean_boxoffice/daily_boxoffice.html', context=context)