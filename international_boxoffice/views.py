from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Sum
from datetime import datetime
from .models import InternationalBoxOffice
from django.db.models.functions import ExtractYear, ExtractMonth

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
