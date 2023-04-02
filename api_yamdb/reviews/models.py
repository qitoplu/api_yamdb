from django.db import models


class Category(models.Model):
    name = models.CharField(
        verbose_name='Название категории',
        max_length=256
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Категория'


class Genres(models.Model):
    name = models.CharField(
        verbose_name='Название жанра',
        max_length=256
    )
    slug = models.SlugField(
        unique=True,
        db_index=True,
        max_length=50
    )

    class Meta:
        verbose_name = 'Жанр'


    def __str__(self):
        return self.name
