from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework import viewsets

from reviews.models import Review, Title
from api.permissions import (
    ReviewAndCommentPermission,
)
from api.serializers import (
    CommentsSerializer,
    ReviewSerializer,
)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведения."""
    # С помощью annotate добавляем к объектам из Title среднюю оценку.
    queryset = (
        Title.objects.all().annotate(Avg('reviews__score')).order_by('name')
    )
    ...

class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = [ReviewAndCommentPermission]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев."""

    serializer_class = CommentsSerializer
    permission_classes = [ReviewAndCommentPermission]

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)
