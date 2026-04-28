from django.contrib import admin

from .models import DiscussionReply, DiscussionThread


class DiscussionReplyInline(admin.TabularInline):
    model = DiscussionReply
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DiscussionThread)
class DiscussionThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'category', 'is_pinned', 'is_locked', 'created_by', 'created_at')
    search_fields = ('title', 'course__code', 'course__title', 'created_by__username')
    list_filter = ('category', 'is_pinned', 'is_locked', 'created_at')
    inlines = [DiscussionReplyInline]


@admin.register(DiscussionReply)
class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = ('thread', 'created_by', 'created_at')
    search_fields = ('thread__title', 'created_by__username')
    list_filter = ('created_at',)