# Generated by Django 3.2.14 on 2023-01-29 15:56

import colorfield.fields
import django.core.validators
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_alter_tag_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(default='#FFFFFF', image_field=None, max_length=18, samples=None, unique=True, validators=[django.core.validators.RegexValidator(message='Проверьте вводимый формат', regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')], verbose_name='Цвет HEX-код'),
        ),
    ]
