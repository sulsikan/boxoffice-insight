from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
import pandas as pd

def index(request):
    return render(request, 'boxoffice/index.html')

def get_revenue_data(request):
    year = request.GET.get('year', '2023')
    period = request.GET.get('period', 'year')
    
    # SQL 쿼리 작성
    if period == 'year':
        query = """
        SELECT country, SUM(revenue) as total_revenue
        FROM boxoffice_data
        WHERE strftime('%Y', date) = %s
        GROUP BY country
        """
        params = [year]
    elif period == 'quarter':
        quarter = request.GET.get('quarter', '1')
        query = """
        SELECT country, SUM(revenue) as total_revenue
        FROM boxoffice_data
        WHERE strftime('%Y', date) = %s
        AND CAST((strftime('%m', date) - 1) / 3 + 1 AS INTEGER) = %s
        GROUP BY country
        """
        params = [year, quarter]
    else:  # month
        month = request.GET.get('month', '1').zfill(2)
        query = """
        SELECT country, SUM(revenue) as total_revenue
        FROM boxoffice_data
        WHERE strftime('%Y', date) = %s
        AND strftime('%m', date) = %s
        GROUP BY country
        """
        params = [year, month]
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()
            
        # 결과를 DataFrame으로 변환
        df = pd.DataFrame(results, columns=columns)
        
        if not df.empty:
            result = df.set_index('country')['total_revenue'].to_dict()
        else:
            result = {}
            
        # 모든 국가에 대해 데이터가 없는 경우 0으로 설정
        countries = ['US', 'UK', 'DE', 'JP']
        for country in countries:
            if country not in result:
                result[country] = 0
                
        return JsonResponse(result)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 