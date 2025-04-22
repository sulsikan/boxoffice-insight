from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import RegionalBoxOffice
from django.contrib import messages

# 연도 필터
class YearListFilter(admin.SimpleListFilter):
    title = _('기준 시작 연도')
    parameter_name = 'start_year'

    def lookups(self, request, model_admin):
        years = RegionalBoxOffice.objects.dates('기준_시작일', 'year')
        return [(str(y.year), f"{y.year}년") for y in years]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(기준_시작일__year=self.value())
        return queryset

# 월 필터
class MonthListFilter(admin.SimpleListFilter):
    title = _('기준 시작 월')
    parameter_name = 'start_month'

    def lookups(self, request, model_admin):
        months = RegionalBoxOffice.objects.dates('기준_시작일', 'month')
        return [(f"{m.year}-{m.month:02}", f"{m.year}년 {m.month}월") for m in months]

    def queryset(self, request, queryset):
        if self.value():
            year, month = map(int, self.value().split("-"))
            return queryset.filter(기준_시작일__year=year, 기준_시작일__month=month)
        return queryset

@admin.register(RegionalBoxOffice)
class RegionalBoxOfficeAdmin(admin.ModelAdmin):
    list_display = (
        "기준_시작일", "기준_종료일", "지역",
        "한국_상영편수", "한국_매출액", "한국_관객수", "한국_점유율",
        "외국_상영편수", "외국_매출액", "외국_관객수", "외국_점유율",
        "전체_상영편수", "전체_매출액", "전체_관객수", "전체_점유율",
    )
    list_filter = (
        "지역", YearListFilter, MonthListFilter
    )
    search_fields = ("지역",)
    ordering = ("-기준_시작일", "지역")
    
    def changelist_view(self, request, extra_context=None):
        count = RegionalBoxOffice.objects.count()
        messages.info(request, f"총 {count:,}개의 지역별 점유율 데이터가 있습니다.")
        return super().changelist_view(request, extra_context)