from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password

from api_yamdb.settings import CODE_LENGTH

ROLE_CHOICES = (
    ('user', 'USER'),
    ('moderator', 'MODERATOR'),
    ('admin', 'ADMIN'),
)


class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        username,
        email,
        password='',
        bio='',
        role='user',
        first_name='',
        last_name=''
    ):
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            confirmation_code=self.make_random_password(length=CODE_LENGTH),
            password=password,
            role=role,
            bio=bio,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        return user

    def create_superuser(
        self,
        username,
        email,
        password=None,
        bio='',
        role='admin',
        first_name='',
        last_name=''
    ):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(
            username=username,
            email=email,
            password=make_password(password),
            role=role,
            bio=bio,
            first_name=first_name,
            last_name=last_name
        )
        user.is_superuser = True
        user.is_staff = True
        user.email_user(
            subject='confirmation_code',
            message=user.confirmation_code,
            fail_silently=False
        )
        user.save()

        return user


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )
    role = models.CharField(
        'Роль',
        max_length=16,
        choices=ROLE_CHOICES,
        default='user'
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=CODE_LENGTH
    )

    objects = CustomUserManager()

    class Meta:
        ordering = ['-date_joined']

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_staff or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'


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


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        db_index=True,
    )
    year = models.IntegerField()
    description = models.CharField(
        max_length=256,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles'
    )
    genre = models.ManyToManyField(
        Genres,
        on_delete=models.SET_NULL,
        related_name='titles'
    )

    class Meta:
        verbose_name = 'Произведение'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзыва."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )
    text = models.TextField()
    score = models.IntegerField(
        default=0,
        validators=[
            MaxValueValidator(10, 'Оценка не может быть больше 10'),
            MinValueValidator(1, 'Оценка не может быть меньше 1'),
        ],
    )

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    """Модель комментария."""
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        ordering = ['-pub_date']