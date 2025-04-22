from django.shortcuts import render
from .models import RegionalBoxOffice
from django.db.models import Sum, Avg
import json
from django.http import JsonResponse

def regional_boxoffice(request):
    start_year = request.GET.get("year", "2025") 
    start_month = request.GET.get("month", "1")   
    
    trend_year = request.GET.get("trendYear", "2021")  
    selected_region = request.GET.get("trendRegion", "부산시")

    qs = RegionalBoxOffice.objects.all()

    if start_year and start_month:
        qs = qs.filter(기준_시작일__year=start_year, 기준_시작일__month=start_month)

    chart_data = {
        "region": [],
        "korean_ratio": [],
        "foreign_ratio": [],
        "korean_sales": [],
        "foreign_sales": []
    }
    
    table_data = []
    
    for item in qs:
        if item.지역 != "합계":
            chart_data["region"].append(item.지역)
            chart_data["korean_ratio"].append(float(item.한국_점유율))
            chart_data["foreign_ratio"].append(float(item.외국_점유율))
            chart_data["korean_sales"].append(int(item.한국_매출액))
            chart_data["foreign_sales"].append(int(item.외국_매출액))
            
            table_data.append({
                "region": item.지역,
                "korean_ratio": round(item.한국_점유율, 2),
                "foreign_ratio": round(item.외국_점유율, 2)
            })

    trend_data = {
        "months": [],
        "korean_ratio": [],
        "foreign_ratio": []
    }
    
    if trend_year and selected_region:
        trend_qs = RegionalBoxOffice.objects.filter(
            지역=selected_region,
            기준_시작일__year=trend_year
        ).order_by('기준_시작일__month')
        
        for item in trend_qs:
            month = item.기준_시작일.month
            trend_data["months"].append(f"{month}월")
            trend_data["korean_ratio"].append(float(item.한국_점유율))
            trend_data["foreign_ratio"].append(float(item.외국_점유율))

    years = list(range(2025, 2009, -1))
    months = list(range(1, 13))
    regions = [
        '서울시', '경기도', '부산시', '대구시', '인천시', '광주시',
        '대전시', '울산시', '세종시', '강원도', '충청북도', '충청남도',
        '전라북도', '전라남도', '경상북도', '경상남도', '제주도'
    ]

    chart_data_json = json.dumps(chart_data)
    trend_data_json = json.dumps(trend_data)

    return render(request, "regional_boxoffice/regional_boxoffice.html", {
        "chart_data_json": chart_data_json,
        "trend_data_json": trend_data_json,
        "table_data": table_data,
        "years": years,
        "months": months,
        "regions": regions,
        "selected_year": start_year,
        "selected_month": start_month,
        "selected_trend_year": trend_year,
        "selected_region": selected_region,
    })

def get_trend_data(request):
    trend_year = request.GET.get("trendYear")
    selected_region = request.GET.get("trendRegion")
    
    if not trend_year or not selected_region:
        return JsonResponse({"error": "필수 파라미터가 누락되었습니다."}, status=400)
    
    trend_data = {
        "months": [],
        "korean_ratio": [],
        "foreign_ratio": []
    }
    
    trend_qs = RegionalBoxOffice.objects.filter(
        지역=selected_region,
        기준_시작일__year=trend_year
    ).order_by('기준_시작일__month')
    
    for item in trend_qs:
        month = item.기준_시작일.month
        trend_data["months"].append(f"{month}월")
        trend_data["korean_ratio"].append(float(item.한국_점유율))
        trend_data["foreign_ratio"].append(float(item.외국_점유율))
    
    return JsonResponse(trend_data)
