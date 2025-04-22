from django.contrib import admin
from .models import RegionalCumulativeStats
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

# 매출액 구간 필터
class RevenueRangeFilter(admin.SimpleListFilter):
    title = _('매출액 구간')
    parameter_name = 'revenue_range'

    def lookups(self, request, model_admin):
        return [
            ('0-1억', _('0 ~ 1억')),
            ('1-10억', _('1억 ~ 10억')),
            ('10-50억', _('10억 ~ 50억')),
            ('50+', _('50억 이상')),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == '0-1억':
            return queryset.filter(revenue_total__lt=100_000_000)
        elif value == '1-10억':
            return queryset.filter(revenue_total__gte=100_000_000, revenue_total__lt=1_000_000_000)
        elif value == '10-50억':
            return queryset.filter(revenue_total__gte=1_000_000_000, revenue_total__lt=5_000_000_000)
        elif value == '50+':
            return queryset.filter(revenue_total__gte=5_000_000_000)
        return queryset

# 스크린수 구간 필터
class ScreenCountFilter(admin.SimpleListFilter):
    title = _('스크린수 구간')
    parameter_name = 'screen_range'

    def lookups(self, request, model_admin):
        return [
            ('0-50', _('0 ~ 50개')),
            ('51-100', _('51 ~ 100개')),
            ('101-300', _('101 ~ 300개')),
            ('300+', _('300개 이상')),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == '0-50':
            return queryset.filter(screens__lte=50)
        elif value == '51-100':
            return queryset.filter(screens__gt=50, screens__lte=100)
        elif value == '101-300':
            return queryset.filter(screens__gt=100, screens__lte=300)
        elif value == '300+':
            return queryset.filter(screens__gt=300)
        return queryset

@admin.register(RegionalCumulativeStats)
class RegionalCumulativeStatsAdmin(admin.ModelAdmin):
    list_display = (
        "title", "region", "screens",
        "revenue_total", "revenue_share",
        "audience_total", "audience_share"
    )
    search_fields = ("title",)
    list_filter = ("region", RevenueRangeFilter, ScreenCountFilter)
    ordering = ("-revenue_total",)

    def changelist_view(self, request, extra_context=None):
        count = RegionalCumulativeStats.objects.count()
        messages.info(request, f"총 {count:,}개의 지역별 누적 통계 데이터가 있습니다.")
        return super().changelist_view(request, extra_context)