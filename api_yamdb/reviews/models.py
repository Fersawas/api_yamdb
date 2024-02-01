from django.db import models

# Create your models here.
class Review(models.Model):
    name = models.CharField(max_length=50)


class Category(models.Model):
    ''' Категории произведений '''
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=50)


class Genre(models.Model):
    ''' Жанры произведений '''
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=50)


class Title(models.Model):
    ''' Произведения хранят в себе Жанры и Категории'''
    name = models.CharField(max_length=255)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    genres = models.ManyToManyField(
        Genre
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='title'
    )
    reviews = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        null=True,
        related_name='title'
    )
