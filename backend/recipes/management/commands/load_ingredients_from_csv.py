from csv import reader

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from csv file.'

    def handle(self, *args, **kwargs):
        with open(
                './data/ingredients.csv', 'r',
                encoding='UTF-8'
        ) as ingredients_csv:
            for ingredien_row in reader(ingredients_csv):
                if len(ingredien_row) == 2:
                    Ingredient.objects.get_or_create(
                        name=ingredien_row[0],
                        measurement_unit=ingredien_row[1],
                    )
