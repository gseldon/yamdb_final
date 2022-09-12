import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


def current_year():
    return datetime.date.today().year


def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)


class Categories(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('pk',)


class Genres(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('pk',)


class Title(models.Model):
    name = models.CharField(max_length=64)
    year = models.IntegerField(
        validators=[
            MinValueValidator(-9999),
            max_value_current_year
        ]
    )
    category = models.ForeignKey(
        Categories,
        on_delete=models.SET_NULL,
        related_name='title',
        null=True
    )
    genre = models.ManyToManyField(
        Genres,
        through='GenreTitle'
    )
    description = models.TextField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ('pk',)


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genres, on_delete=models.SET_NULL, null=True)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    text = models.TextField()
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='review'
    )
    score = models.PositiveSmallIntegerField(
        default=None,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1),
        ]
    )
    pub_date = models.DateTimeField(
        'Дата добавления отзыва', auto_now_add=True, db_index=True
    )

    class Meta:
        unique_together = ['title', 'author']
        ordering = ('pk',)


class Comments(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления комментария', auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ('pk',)
