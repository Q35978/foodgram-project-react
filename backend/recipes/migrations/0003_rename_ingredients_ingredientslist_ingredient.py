# Generated by Django 3.2.14 on 2023-01-21 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredientslist',
            old_name='ingredients',
            new_name='ingredient',
        ),
    ]
