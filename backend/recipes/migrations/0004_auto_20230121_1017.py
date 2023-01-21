# Generated by Django 3.2.14 on 2023-01-21 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_rename_ingredients_ingredientslist_ingredient'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='ingredientslist',
            name='unique_ingredients_list',
        ),
        migrations.AddConstraint(
            model_name='ingredientslist',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_ingredients_list'),
        ),
    ]
