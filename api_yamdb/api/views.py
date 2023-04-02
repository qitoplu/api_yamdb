from rest_framework import viewsets
from .serializers import CategorySerializer, GenreSerializer
from reviews.models import Category, Genres


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenreSerializer

