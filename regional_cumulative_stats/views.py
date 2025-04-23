from django.shortcuts import render
from django.http import JsonResponse
from .models import RegionalCumulativeStats
from django.db.models import Sum
import random
import json

# views.py
def regional_cumulative(request):
    stats = RegionalCumulativeStats.objects.filter(
        title__icontains='극한직업'
    ).values('region').annotate(
        total_sales=Sum('revenue_total'),
        total_audience=Sum('audience_total')
    ).order_by('-total_sales')

    # 총합 계산
    total = sum(item['total_sales'] for item in stats) or 1

    # 비율 계산
    percentages = [item['total_sales'] / total * 100 for item in stats]

    # pie chart 데이터 세팅
    pie_data = {
        'values': [item['total_sales'] for item in stats],
        'labels': [item['region'] for item in stats],
        'type': 'pie',
        'textinfo': 'label+percent',
        'textposition': ['none' if p < 3.5 else 'inside' for p in percentages],
        'texttemplate': ['' if p < 3.5 else '%{label}<br>%{percent:.1%}' for p in percentages],
        'hovertemplate': '%{label}<br>%{percent:.1%}<br>매출액: %{value:,.0f}원<extra></extra>',
        'showlegend': False,
        'automargin': True,
        'insidetextorientation': 'horizontal'
    }

    # 테이블 데이터
    table_data = [
        {
            'region': item['region'],
            'sales': format(item['total_sales'], ','),
            'audience': format(item['total_audience'], ',')
        }
        for item in stats
    ]

    context = {
        'initial_pie_data': json.dumps(pie_data),
        'initial_table_data': json.dumps(table_data)
    }

    return render(request, 'regional_cumulative_stats/regional_cumulative.html', context)

def get_movie_stats(request):
    title = request.GET.get('title', '')
    if not title:
        return JsonResponse({'error': '영화 제목이 필요합니다.'}, status=400)
    
    # 영화 제목으로 검색하여 지역별 누적매출액 조회
    stats = RegionalCumulativeStats.objects.filter(
        title__icontains=title
    ).values('region').annotate(
        total_sales=Sum('revenue_total'),
        total_audience=Sum('audience_total')
    ).order_by('-total_sales')
    
    # 파이차트 데이터 준비
    pie_data = {
        'values': [item['total_sales'] for item in stats],
        'labels': [item['region'] for item in stats],
        'type': 'pie',
        'textinfo': 'label+percent',
        'textposition': 'auto',
        'hoverinfo': 'label+percent',
        'showlegend': False,
        'automargin': True,
        'insidetextorientation': 'horizontal'
    }
    
    # 테이블 데이터 준비
    table_data = [
        {
            'region': item['region'],
            'sales': format(item['total_sales'], ','),
            'audience': format(item['total_audience'], ',')
        }
        for item in stats
    ]
    
    return JsonResponse({
        'pie_data': pie_data,
        'table_data': table_data
    })

def get_top_movies_by_region(request):
    region = request.GET.get('region', '')
    if not region:
        return JsonResponse({'error': '지역이 필요합니다.'}, status=400)

    # 해당 지역의 상위 20개 영화 조회
    top_movies = RegionalCumulativeStats.objects.filter(
        region=region
    ).order_by('-revenue_total')[:20]

    if not top_movies.exists():
        return JsonResponse({'wordcloud_data': [], 'message': f'{region}에 대한 데이터가 없습니다.'})

    # 매출 최대값 기준 정규화 (최소값 10 보장)
    revenue_list = list(top_movies.values_list('revenue_total', flat=True))
    max_value = max(revenue_list) if revenue_list else 1

    wordcloud_data = [
        {
            'text': movie.title,
            'value': max(int((movie.revenue_total / max_value) * 100), 10)  # 최소 10 보장
        }
        for movie in top_movies
    ]

    return JsonResponse({'wordcloud_data': wordcloud_data})

def get_random_color():
    colors = [ 
        '#3498DB', '#E74C3C', '#2ECC71', '#F1C40F', '#9B59B6',
        '#1ABC9C', '#E67E22', '#34495E', '#16A085', '#27AE60',
        '#2980B9', '#8E44AD', '#2C3E50', '#F39C12', '#D35400',
        '#C0392B', '#7F8C8D', '#BDC3C7', '#95A5A6'
    ]
    return random.choice(colors)