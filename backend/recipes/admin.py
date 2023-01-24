from django.contrib import admin

from foodgram import settings

from . import models


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = (
        'name',
    )
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
        'measurement_unit',
    )
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


class IngredientsListInline(admin.TabularInline):
    model = models.IngredientsList
    fields = (
        'ingredient', 'amount'
    )
    verbose_name = 'Ингредиенты'


@admin.register(models.IngredientsList)
class IngredientsListAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'ingredient',
    )
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(models.ShoppingCart)
class UserCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(models.UserFavourite)
class UserFavouriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'get_user_favorite',
    )
    fields = (
        ('name',),
        ('cooking_time',),
        ('author',),
        ('tags',),
        ('text',),
        ('image',),
    )
    raw_id_fields = (
        'author',
        'tags',
    )
    search_fields = (
        'name',
        'author',
        'tags',
    )
    list_filter = (
        'name',
        'author__username',
        'tags',
    )
    inlines = (IngredientsListInline, )
    empty_value_display = settings.EMPTY_VALUE_DISPLAY

    def get_user_favorite(self, obj):
        return obj.user_favorite.count()

    get_user_favorite.short_description = 'Добавлений в избранное'
