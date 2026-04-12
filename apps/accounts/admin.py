from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


admin.site.site_header = "SmartLMS Admin"
admin.site.site_title = "SmartLMS Admin Portal"
admin.site.index_title = "SmartLMS Administration"


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'full_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'full_name')

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('full_name', 'role')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('full_name', 'role')}),
    )