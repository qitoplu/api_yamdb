from rest_framework import viewsets
from .serializers import GenreSerializer
from reviews.models import Genres


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenreSerializer

