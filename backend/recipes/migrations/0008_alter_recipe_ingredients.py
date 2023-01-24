# Generated by Django 3.2.14 on 2023-01-24 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20230124_1934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipe', through='recipes.IngredientsList', to='recipes.Ingredient', verbose_name='Ингредиенты'),
        ),
    ]
