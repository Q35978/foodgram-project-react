# Generated by Django 3.2.14 on 2023-01-29 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_alter_tag_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(blank=True, default='FF', max_length=7, null=True, verbose_name='Цвет HEX-код'),
        ),
    ]