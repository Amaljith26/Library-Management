from django.contrib import admin
from .models import Member

@admin.register(Member)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership_type', 'start_date', 'expiry_date','is_verified_by_faculty')
    list_filter = ('membership_type','is_verified_by_faculty')
    search_fields = ('user__username', 'phone')

