from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Sum, Count
from datetime import datetime
from .models import InternationalBoxOffice
from genre_trend.models import MovieBasicInfo
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractQuarter
from django.db import models
import json

COUNTRY_NAMES = {
    'US': '미국',
    'UK': '영국',
    'DE': '독일',
    'JP': '일본'
}

# 2015-2025년 평균 환율 (USD 기준)
CURRENCY_TO_USD = {
    'USD': 1.0,
    'GBP': 1.31,  # 영국 파운드 to USD
    'EUR': 1.12,  # 유로 to USD
    'JPY': 0.0084  # 일본 엔화 to USD (1엔 = 0.0084 달러)
}

CURRENCY_BY_COUNTRY = {
    'US': 'USD',
    'UK': 'GBP',
    'DE': 'EUR',
    'JP': 'JPY'
}

def convert_to_usd(amount, currency):
    """Convert amount from given currency to USD"""
    if currency in CURRENCY_TO_USD:
        return amount * CURRENCY_TO_USD[currency]
    return amount  # 변환할 수 없는 경우 원래 금액 반환

# Create your views here.

def international_visualization_view(request):
    """Render the international visualization page"""
    return render(request, 'international_boxoffice/international-visualization.html')

@require_http_methods(["GET"])
def get_boxoffice_data(request):
    """Get international box office data with optional filters"""
    try:
        # Get query parameters
        country = request.GET.get('country')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Base query
        query = InternationalBoxOffice.objects.all()
        
        # Apply filters if provided
        if country:
            query = query.filter(country=country.upper())
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(release_date__gte=start_date)
            except ValueError:
                return JsonResponse({'error': 'Invalid start_date format. Use YYYY-MM-DD'}, status=400)
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(release_date__lte=end_date)
            except ValueError:
                return JsonResponse({'error': 'Invalid end_date format. Use YYYY-MM-DD'}, status=400)

        # Get monthly aggregated data for chart
        monthly_data = query.values(
            'year',
            'country',
            month=ExtractMonth('release_date')
        ).annotate(
            total_revenue=Sum('weekend_revenue')
        ).order_by('year', 'month', 'country')

        chart_data = []
        for record in monthly_data:
            country_code = record['country']
            currency = CURRENCY_BY_COUNTRY.get(country_code, 'USD')
            usd_revenue = convert_to_usd(record['total_revenue'], currency)
            
            chart_data.append({
                'country': COUNTRY_NAMES.get(country_code, country_code),
                'year': record['year'],
                'month': record['month'],
                'revenue': usd_revenue
            })
        
        # Get detailed data for table
        table_data = []
        for record in query.order_by('year', 'release_date', 'country', 'rank'):
            currency = CURRENCY_BY_COUNTRY.get(record.country, 'USD')
            usd_revenue = convert_to_usd(record.weekend_revenue, currency)
            
            table_data.append({
                'country': COUNTRY_NAMES.get(record.country, record.country),
                'country_code': record.country,
                'date': record.release_date.strftime('%Y-%m-%d'),
                'rank': record.rank,
                'movie_title': record.title,
                'revenue': usd_revenue,
                'original_revenue': record.weekend_revenue,
                'original_currency': currency,
                'year': record.year,
                'month': record.release_date.month
            })
        
        return JsonResponse({
            'status': 'success',
            'count': len(table_data),
            'chart_data': chart_data,
            'table_data': table_data
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_countries(request):
    """Get list of available countries in the database"""
    try:
        countries = InternationalBoxOffice.objects.values_list('country', flat=True).distinct()
        country_list = [{'code': code, 'name': COUNTRY_NAMES.get(code, code)} for code in countries]
        return JsonResponse({
            'status': 'success',
            'countries': country_list
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_date_range(request):
    """Get the available date range in the database"""
    try:
        first_record = InternationalBoxOffice.objects.order_by('release_date').first()
        last_record = InternationalBoxOffice.objects.order_by('-release_date').first()
        
        if not first_record or not last_record:
            return JsonResponse({
                'status': 'error',
                'message': 'No data available'
            }, status=404)
        
        return JsonResponse({
            'status': 'success',
            'start_date': first_record.release_date.strftime('%Y-%m-%d'),
            'end_date': last_record.release_date.strftime('%Y-%m-%d')
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def movie_international_visualization_view(request):
    """Render the movie international visualization page"""
    years = range(2015, 2026)
    # 영화 제목 목록 가져오기 (중복 제거)
    movies = InternationalBoxOffice.objects.values_list('title', flat=True).distinct().order_by('title')
    return render(request, 'international_boxoffice/movie-international-visualization.html', {
        'years': years,
        'movies': movies
    })

@require_http_methods(["GET"])
def get_movie_revenue_data(request):
    """Get movie revenue data by country and period"""
    try:
        movie_title = request.GET.get('movie_title')
        year = request.GET.get('year')
        period = request.GET.get('period', 'year')

        if not movie_title:
            return JsonResponse({
                'status': 'error',
                'message': 'Movie title is required'
            }, status=400)

        # Base query
        query = InternationalBoxOffice.objects.filter(
            title__icontains=movie_title
        )

        if year:
            query = query.filter(year=year)

        # Group by period
        if period == 'year':
            data = query.values(
                'year',
                'country'
            ).annotate(
                total_revenue=Sum('weekend_revenue')
            ).order_by('year', 'country')
        elif period == 'quarter':
            data = query.annotate(
                quarter=ExtractQuarter('release_date')
            ).values(
                'year',
                'quarter',
                'country'
            ).annotate(
                total_revenue=Sum('weekend_revenue')
            ).order_by('year', 'quarter', 'country')
        else:  # month
            data = query.values(
                'year',
                'country',
                month=ExtractMonth('release_date')
            ).annotate(
                total_revenue=Sum('weekend_revenue')
            ).order_by('year', 'month', 'country')

        # Process data for chart and table
        chart_data = {}
        table_data = []

        for record in data:
            country_code = record['country']
            country_name = COUNTRY_NAMES.get(country_code, country_code)
            currency = CURRENCY_BY_COUNTRY.get(country_code, 'USD')
            
            # Convert revenue to USD
            revenue_usd = convert_to_usd(record['total_revenue'], currency)
            
            # Format period string
            if period == 'year':
                period_str = f"{record['year']}년"
            elif period == 'quarter':
                period_str = f"{record['year']}년 {record['quarter']}분기"
            else:
                period_str = f"{record['year']}년 {record['month']}월"

            # Add to chart data
            if country_name not in chart_data:
                chart_data[country_name] = {
                    'periods': [],
                    'revenues': []
                }
            chart_data[country_name]['periods'].append(period_str)
            chart_data[country_name]['revenues'].append(revenue_usd)

            # Add to table data
            table_data.append({
                'country': country_name,
                'period': period_str,
                'revenue_usd': revenue_usd,
                'revenue_local': record['total_revenue'],
                'currency': currency
            })

        return JsonResponse({
            'status': 'success',
            'chart_data': chart_data,
            'table_data': table_data
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def genre_analysis_view(request):
    """Render the genre analysis page"""
    # Get available years from MovieBasicInfo
    years = MovieBasicInfo.objects.values_list('release_date', flat=True).distinct()
    years = sorted(set(year[:4] for year in years if year))  # Extract year part and remove duplicates
    
    # Get unique single countries
    countries = set()
    for movie in MovieBasicInfo.objects.values_list('country', flat=True).distinct():
        if movie:  # if country is not None
            # Split multiple countries and take the first one
            primary_country = movie.split(',')[0].strip()
            countries.add(primary_country)
    
    # Convert to list and sort by country name
    country_list = []
    for code in countries:
        name = COUNTRY_NAMES.get(code, code)
        country_list.append({'code': code, 'name': name})
    
    # Sort by name
    country_list.sort(key=lambda x: x['name'])
    
    context = {
        'years': years,
        'countries': country_list
    }
    return render(request, 'international_boxoffice/genre-analysis.html', context)

@require_http_methods(["GET"])
def get_genre_analysis_data(request):
    try:
        country = request.GET.get('country')
        year = request.GET.get('year')
        
        print("\n" + "="*50)
        print(f"요청된 검색 조건 - 국가: {country}, 연도: {year}")
        
        # Base query
        query = MovieBasicInfo.objects.all()
        print(f"전체 데이터 수: {query.count()}")
        
        # Apply filters
        if country:
            from django.db.models import Q
            country_conditions = Q()
            
            # 국가 코드로 검색
            country_conditions |= Q(country__icontains=country)
            
            # 국가 이름으로도 검색
            for code, name in COUNTRY_NAMES.items():
                if name == country:
                    print(f"국가 이름 '{country}'에 매칭되는 코드 찾음: {code}")
                    country_conditions |= Q(country__icontains=code)
            
            query = query.filter(country_conditions)
            print(f"국가 필터 후 데이터 수: {query.count()}")
            
            # 샘플 데이터 출력
            sample_data = query.values('country', 'genre')[:5]
            print("\n처음 5개 데이터 샘플:")
            for item in sample_data:
                print(f"country: {item['country']}, genre: {item['genre']}")
        
        if year:
            query = query.filter(release_date__startswith=year)
            print(f"\n연도 필터 후 데이터 수: {query.count()}")
        
        # 장르 데이터 정제 및 통합
        genre_map = {}  # 장르별 영화 수를 저장할 딕셔너리
        
        # 모든 영화의 장르를 순회하면서 정제
        for movie in query:
            # 장르 문자열을 쉼표로 분리하고 각각의 장르를 정제
            if movie.genre:
                genres = [g.strip() for g in movie.genre.split(',')]
                for genre in genres:
                    # 기본 장르만 추출 (예: "액션, SF" -> "액션"과 "SF"로 분리)
                    base_genre = genre.split(',')[0].strip()
                    
                    # 장르가 비어있지 않은 경우만 처리
                    if base_genre:
                        if base_genre in genre_map:
                            genre_map[base_genre] += 1
                        else:
                            genre_map[base_genre] = 1
        
        print("\n정제된 장르별 집계:")
        for genre, count in genre_map.items():
            print(f"장르: {genre}, 수: {count}")
        
        # 전체 영화 수 계산
        total_movies = sum(genre_map.values())
        
        # 장르 데이터 생성
        genre_data = []
        for genre, count in genre_map.items():
            percentage = (count / total_movies * 100) if total_movies > 0 else 0
            genre_data.append({
                'genre': genre,
                'count': count,
                'percentage': round(percentage, 2)
            })
        
        # 비율 기준 내림차순 정렬
        genre_data.sort(key=lambda x: x['percentage'], reverse=True)
        
        print("\n최종 장르 데이터:")
        for item in genre_data:
            print(f"장르: {item['genre']}, 수: {item['count']}, 비율: {item['percentage']}%")
        
        print("="*50 + "\n")
        
        return JsonResponse({
            'status': 'success',
            'total_movies': total_movies,
            'genre_data': genre_data
        })
    
    except Exception as e:
        print(f"에러 발생: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def genre_stat_view(request):
    """장르 통계 페이지를 렌더링합니다."""
    # 장르별 영화 수 집계
    genre_counts = MovieBasicInfo.objects.values('genre').annotate(
        count=Count('id')
    ).order_by('-count')

    # 차트에 필요한 데이터 준비
    labels = [item['genre'] for item in genre_counts]
    values = [item['count'] for item in genre_counts]

    context = {
        'labels': json.dumps(labels),
        'values': json.dumps(values)
    }
    
    return render(request, 'international_boxoffice/genre_stat.html', context)
