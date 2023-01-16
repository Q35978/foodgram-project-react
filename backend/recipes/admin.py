from django.contrib import admin

from foodgram import settings

from . import models


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
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


@admin.register(models.IngredientsList)
class IngredientsListAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredients',
    )
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(models.ShoppingCart)
class UserCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(models.UserFavourite)
class UserFavouriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
    )
    fields = (
        (
            'name',
            'cooking_time',
        ),
        (
            'author',
            'tags',
        ),
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
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
