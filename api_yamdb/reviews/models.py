from collections.abc import Collection
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator


# Create your models here.
USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

CHOICES = ((USER, 'user'),
           (MODERATOR, 'moderator'),
           (ADMIN, 'admin'))


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
        max_length=150,
        validators=(
            RegexValidator(r'[\w.@+-]+'),
            ),
        unique=True
    )
    email = models.EmailField(max_length=254,
                              unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(choices=ROLES, default='user', max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]
    
    @property
    def is_user(self):
        return self.role == self.USER
    @property
    def is_admin(self):
        return self.role == self.ADMIN
    @property
    def is_moderator(self):
        return self.role == self.MODERATOR


User = get_user_model()


class Category(models.Model):
    ''' Категории произведений '''
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    ''' Жанры произведений '''
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self) -> str:
        return self.name


class Title(models.Model):
    ''' Произведения хранят в себе Жанры и Категории'''
    name = models.CharField(max_length=255)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(
        Genre
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        null=True,
        related_name='title'
    )

    def __str__(self) -> str:
        return self.name


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
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique'
            )
        ]
        #unique_together = ('author', 'title')


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
