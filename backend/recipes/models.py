from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.functions import Length
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    RegexValidator
)
from colorfield.fields import ColorField

from foodgram import settings


models.CharField.register_lookup(Length)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        unique=True,
        verbose_name='Тэг',
        max_length=settings.MAX_LEN_CHARFIELD,
    )
    color = ColorField(
        verbose_name='Цвет HEX-код',
        max_length=settings.MAX_LEN_COLOR_HEX_CODE,
        format='hex',
        unique=True,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message='Проверьте вводимый формат',
            )
        ],
    )
    slug = models.CharField(
        unique=True,
        verbose_name='Slug тэга',
        max_length=settings.MAX_LEN_CHARFIELD,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)
        constraints = (
            models.CheckConstraint(
                name='\nrecipes-tag-name is empty\n',
                check=models.Q(name__length__gt=0),
            ),
            models.CheckConstraint(
                name='\nrecipes-tag-color is empty\n',
                check=models.Q(color__length__gt=0),
            ),
            models.CheckConstraint(
                name='\nrecipes-tag-slug is empty\n',
                check=models.Q(slug__length__gt=0),
            ),
        )

    def __str__(self):
        return f'{self.name}/{self.color}'


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=settings.MAX_LEN_CHARFIELD,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=settings.MAX_LEN_CHARFIELD,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                name='unique_for_ingredient',
                fields=('name', 'measurement_unit'),
            ),
            models.CheckConstraint(
                name='\nrecipes-ingredient-name is empty\n',
                check=models.Q(name__length__gt=0),
            ),
            models.CheckConstraint(
                name='\nrecipes-ingredient-measurement_unit is empty\n',
                check=models.Q(measurement_unit__length__gt=0),
            ),
        )

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=settings.MAX_LEN_CHARFIELD,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientsList',
        related_name='recipe',
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='static/recipe/',
    )
    text = models.TextField(
        verbose_name='Описание',
        max_length=settings.MAX_LEN_TEXTFIELD,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
        validators=(
            MinValueValidator(settings.MIN_COOKING_TIME),
            MaxValueValidator(settings.MAX_COOKING_TIME),
        ),
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'name',
                    'author'
                ),
                name='unique_for_author'
            ),
            models.CheckConstraint(
                name='\nrecipes-recipe-name is empty\n',
                check=models.Q(name__length__gt=0),
            ),
        )

    def __str__(self):
        return f'{self.name} ({self.author.username})'


class IngredientsList(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='recipe',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='ingredient',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=1,
        validators=(
            MinValueValidator(settings.MIN_INGREDIENTS_QUANTITY),
            MaxValueValidator(settings.MAX_INGREDIENTS_QUANTITY),
        ),
    )

    class Meta:
        verbose_name = 'Список ингредиентов'
        verbose_name_plural = 'Списки ингредиентов'
        ordering = ('recipe', )
        constraints = (
            models.UniqueConstraint(
                name='unique_ingredients_list',
                fields=('recipe', 'ingredient', ),
            ),
        )

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class UserFavourite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='user_favorite',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='user_favorite',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                name='unique_user_favourite',
                fields=['user', 'recipe'],
            ),
        ]

    def __str__(self):
        return f'"{self.recipe}" добавлен в избранное пользователя {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='shopping_cart',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='shopping_cart',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            models.UniqueConstraint(
                name='unique_user_cart',
                fields=['user', 'recipe'],
            )
        ]

    def __str__(self):
        return (f'рецепт "{self.recipe}" добавлен ',
                f'в корзину пользователем {self.user}')
