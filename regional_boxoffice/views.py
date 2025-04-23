from django.shortcuts import render

def regional_boxoffice(request):
    return render(request, 'regional_boxoffice/regional_boxoffice.html')