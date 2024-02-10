import csv
from typing import Any
from django.core.management.base import BaseCommand
from reviews.models import (UserMain, Category, Genre,
                            Title, Review, Comment, Genre_Title)

BASE_PATH = 'static/data/'

BASE_FILES: dict = {
    'user': [UserMain, (BASE_PATH + 'users.csv')],
    'genre': [Genre_Title, (BASE_PATH) + 'genre_title.csv'],
    'genre_title': [Genre, (BASE_PATH + 'genre.csv')],
    'category': [Category, (BASE_PATH + 'category.csv')],
    'titles': [Title, (BASE_PATH + 'titles.csv')],
    'review': [Review, (BASE_PATH + 'review.csv')],
    'comments': [Comment, (BASE_PATH + 'comments.csv')],
}


class Command(BaseCommand):
    def make_table(self, model, csv_table) -> str | None:
        with open(csv_table, 'r', encoding='utf-8') as csv_default:
            csv_file = csv.DictReader(csv_default)
            model.objects.bulk_create(
                model(**table) for table in csv_file)

    def handle(self, *args: Any, **options: Any) -> str | None:
        for key, value in BASE_FILES.items():
            self.make_table(model=value[0], csv_table=value[1])
