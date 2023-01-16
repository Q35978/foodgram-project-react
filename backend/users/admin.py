from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Subscribe


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    fields = (
        (
            'username',
            'email',
        ),
        (
            'first_name',
            'last_name',
        ),
    )
    fieldsets = []
    search_fields = (
        'username',
        'email',
    )
    list_filter = (
        'username',
        'first_name',
        'email',
    )
    save_on_top = True


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'subscriber',
        'author',
    )
