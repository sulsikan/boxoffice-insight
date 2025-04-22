from django.contrib import admin
from .models import InternationalBoxOffice

@admin.register(InternationalBoxOffice)
class InternationalBoxOfficeAdmin(admin.ModelAdmin):
    """해외 박스오피스 관리자 설정"""
    
    def weekend_revenue_display(self, obj):
        return f"{obj.weekend_revenue_currency}{obj.weekend_revenue:,.0f}"
    weekend_revenue_display.short_description = '주말 매출액'
    
    def total_revenue_display(self, obj):
        return f"{obj.total_revenue_currency}{obj.total_revenue:,.0f}"
    total_revenue_display.short_description = '누적 매출액'
    
    list_display = (
        'rank', 'title', 'country', 'year', 'week', 
        'release_date', 'weekend_revenue_display', 'total_revenue_display',
        'distributor', 'created_at'
    )
    
    list_filter = ('country', 'year', 'week', 'distributor')
    
    search_fields = ('title', 'distributor')
    
    ordering = ('-created_at', 'country', 'rank')
    
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('rank', 'title', 'country', 'year', 'week', 'release_date')
        }),
        ('수익 정보', {
            'fields': (
                'weekend_revenue', 'weekend_revenue_currency',
                'total_revenue', 'total_revenue_currency'
            )
        }),
        ('기타 정보', {
            'fields': ('distributor', 'created_at')
        }),
    )
