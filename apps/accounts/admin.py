from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'full_name',
        'role',
        'is_staff',
        'is_active',
    )
    list_filter = (
        'role',
        'is_staff',
        'is_superuser',
        'is_active',
    )
    search_fields = (
        'username',
        'email',
        'full_name',
    )
    ordering = ('username',)

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Information', {
            'fields': ('full_name', 'email', 'role')
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'full_name',
                'role',
                'usable_password',
                'password1',
                'password2',
            ),
        }),
    )


admin.site.site_header = "ClassADDA Admin"
admin.site.site_title = "ClassADDA Admin Portal"
admin.site.index_title = "ClassADDA Administration"