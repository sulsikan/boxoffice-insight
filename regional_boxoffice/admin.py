from django.contrib import admin
from .models import RegionalBoxOffice

@admin.register(RegionalBoxOffice)
class RegionalBoxOfficeAdmin(admin.ModelAdmin):
    list_display = (
        "기준_시작일", "기준_종료일", "지역",
        "한국_상영편수", "한국_매출액", "한국_관객수", "한국_점유율",
        "외국_상영편수", "외국_매출액", "외국_관객수", "외국_점유율",
        "전체_상영편수", "전체_매출액", "전체_관객수", "전체_점유율",
    )
    list_filter = ("기준_시작일", "기준_종료일", "지역")
    search_fields = ("지역",)
    ordering = ("-기준_시작일", "지역")