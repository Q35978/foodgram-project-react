# Generated by Django 3.2.15 on 2023-01-12 17:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('recipes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='userfavourite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_favorites', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='usercart',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_cart', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AddField(
            model_name='usercart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_cart', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.CheckConstraint(check=models.Q(('name__length__gt', 0)), name='\nrecipes-tag-name is empty\n'),
        ),
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.CheckConstraint(check=models.Q(('color__length__gt', 0)), name='\nrecipes-tag-color is empty\n'),
        ),
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.CheckConstraint(check=models.Q(('slug__length__gt', 0)), name='\nrecipes-tag-slug is empty\n'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='recipes.IngredientsList', to='recipes.Ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', to='recipes.Tag', verbose_name='Тэги'),
        ),
        migrations.AddField(
            model_name='ingredientslist',
            name='ingredients',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients_list', to='recipes.ingredient', verbose_name='Ингредиент'),
        ),
        migrations.AddField(
            model_name='ingredientslist',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients_list', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_for_ingredient'),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.CheckConstraint(check=models.Q(('name__length__gt', 0)), name='\nrecipes-ingredient-name is empty\n'),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.CheckConstraint(check=models.Q(('measurement_unit__length__gt', 0)), name='\nrecipes-ingredient-measurement_unit is empty\n'),
        ),
        migrations.AddConstraint(
            model_name='userfavourite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_user_favourite'),
        ),
        migrations.AddConstraint(
            model_name='usercart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_user_cart'),
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.UniqueConstraint(fields=('name', 'author'), name='unique_for_author'),
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.CheckConstraint(check=models.Q(('name__length__gt', 0)), name='\nrecipes-recipe-name is empty\n'),
        ),
        migrations.AddConstraint(
            model_name='ingredientslist',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredients'), name='unique_ingredients_list'),
        ),
    ]
