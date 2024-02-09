import csv
# import os
from io import StringIO
from typing import Any
# from django.conf import settings
from django.core.management.base import BaseCommand
from models import UserMain, Category, Genre, Title, Review, Comment

BASE_PATH = 'static/data/'

BASE_FILES: dict = {
    'user': [UserMain, (BASE_PATH + 'users.csv')],
    'category': [Category, (BASE_PATH + 'category.csv')],
    'genre_title': ['?'],
    'genre': [Genre, (BASE_PATH + 'genre.csv')],
    'review': [Review, (BASE_PATH + 'review.csv')],
    'title': [Title, (BASE_PATH + 'title.csv')],
    'comments': [Comment, (BASE_PATH + 'comments.csv')]
}


class TableCreator(BaseCommand):
    def __init__(self, stdout: StringIO | None = ...,
                 stderr: StringIO | None = ...,
                 no_color: bool = ...,
                 force_color: bool = ...,
                 model=None,
                 csv_table=None) -> None:
        self.model = model
        self.csv_table = csv_table
        super().__init__(stdout, stderr, no_color, force_color)

    def handle(self, *args: Any, **options: Any) -> str | None:
        with open(self.csv_table, 'r') as csv_default:
            csv_file = csv.reader(csv_default, delimiter=',', quotechar='|')
            header = csv_file.next()
            for row in csv_file:
                _object_dict = {key: value for key, value in zip(header, row)}
                self.model.obects.create(**_object_dict)


if __name__ == '__main__':
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_yamdb.settings")
    # settings.configure()
    for key, value in BASE_FILES:
        creator = TableCreator(model=value[0], csv_table=value[1])
        creator.handle()

''' не понимаю, чего ему не хватает
    django.core.exceptions.ImproperlyConfigured: Requested setting
    INSTALLED_APPS, but settings are not configured. You must either
    define the environment variable DJANGO_SETTINGS_MODULE or call
    settings.configure() before accessing settings. '''
