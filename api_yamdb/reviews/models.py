from django.db import models

from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

from .constants import MAX_LENGTH, SLUG_LENGTH, NAME_LENGTH


class UserMain(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLES = (
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin')
    )

    username = models.CharField(
        verbose_name='username',
        max_length=NAME_LENGTH,
        validators=(
            RegexValidator(r'[\w.@+-]+'),
        ),
        unique=True
    )
    email = models.EmailField(max_length=MAX_LENGTH, unique=True)
    first_name = models.CharField(max_length=NAME_LENGTH, blank=True)
    last_name = models.CharField(max_length=NAME_LENGTH, blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(choices=ROLES, default='user',
                            max_length=NAME_LENGTH)

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    def __str__(self):
        return self.username


User = get_user_model()


class Category(models.Model):
    ''' Категории произведений '''
    name = models.CharField(max_length=MAX_LENGTH)
    slug = models.SlugField(unique=True, max_length=SLUG_LENGTH)

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    ''' Жанры произведений '''
    name = models.CharField(max_length=MAX_LENGTH)
    slug = models.SlugField(unique=True, max_length=SLUG_LENGTH)

    def __str__(self) -> str:
        return self.name


class Title(models.Model):
    ''' Произведения хранят в себе Жанры и Категории'''
    name = models.CharField(max_length=MAX_LENGTH)
    year = models.IntegerField()
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        null=True,
        related_name='title'
    )

    description = models.TextField(blank=True)
    genre = models.ManyToManyField(
        Genre,
        through='Genre_Title'
    )

    def __str__(self) -> str:
        return self.name


class Genre_Title(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE
    )


class Review(models.Model):
    text = models.TextField()
    score = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                1,
                message='to low score'
            ),
            MaxValueValidator(
                10,
                message='to high score'
            ),
        ]
    )
    author = models.ForeignKey(
        User,
        related_name='review',
        on_delete=models.CASCADE,
    )
    title = models.ForeignKey(
        Title,
        related_name='review',
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('title', 'author')
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique'
            )
        ]


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment',
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(
        Review,
        related_name='comment',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.text
