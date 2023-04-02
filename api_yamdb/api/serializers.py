from rest_framework import serializers
from reviews.models import Genres


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__',
        model = Genres
