from django.shortcuts import render

def regional_cumulative(request):
    return render(request, 'regional_cumulative_stats/regional_cumulative.html')