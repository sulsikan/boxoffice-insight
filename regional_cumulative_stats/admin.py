from django.contrib import admin
from .models import RegionalCumulativeStats

@admin.register(RegionalCumulativeStats)
class RegionalCumulativeStatsAdmin(admin.ModelAdmin):
    list_display = (
        "title", "region", "screens",
        "revenue_total", "revenue_share",
        "audience_total", "audience_share"
    )
    search_fields = ("title", "region")
    list_filter = ("region",)
    ordering = ("-revenue_total",)
