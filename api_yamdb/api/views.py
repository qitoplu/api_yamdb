from rest_framework import viewsets
from django.db.models import Avg

from .serializers import (CategorySerializer,
                          GenreSerializer,
                          FirstTitleSerializer,
                          SecondTitleSerializer)
from reviews.models import Category, Genres, Title


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rate=Avg('reviews__score')
    ).all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return FirstTitleSerializer
        return SecondTitleSerializer
