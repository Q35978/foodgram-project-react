from django.contrib import admin

from .models import User, Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
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
        'id',
        'subscriber',
        'author',
    )
