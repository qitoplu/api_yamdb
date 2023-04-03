from rest_framework import filters, status, viewsets
from django.db.models import Avg
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase

from reviews.models import User, Category, Genres, Title, Review
from .permissions import AdminOnly
from .serializers import (SignUpSerializer,
                          TokenSerializer,
                          UserSerializer,
                          CategorySerializer,
                          GenreSerializer,
                          CommentsSerializer,
                          ReviewSerializer,)

from api.permissions import (
    ReviewAndCommentPermission,
)


class SignUpView(CreateModelMixin,
                 RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.data)
        username = serializer.data["username"]
        user = get_object_or_404(User, username=username)
        user.email_user(
            subject='confirmation_code',
            message=user.confirmation_code,
            fail_silently=False
        )
        return Response(serializer.data)


class TokenView(TokenViewBase):
    permission_classes = (AllowAny,)
    serializer_class = TokenSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    def get_object(self):
        user_username = self.kwargs['pk']
        user = get_object_or_404(User, username=user_username)
        return user

    @action(methods=['get', 'patch', 'put', 'delete'], detail=False)
    def me(self, request):
        if request.method == 'GET':
            user = User.objects.get(username=request.user.username)
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        if request.method == 'PATCH' or request.method == 'PUT':
            partial = True if request.method == 'PATCH' else False
            user = User.objects.get(username=request.user.username)
            data = request.data.copy()
            data['role'] = user.role
            serializer = self.get_serializer(
                user,
                data=data,
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(user, '_prefetched_objects_cache', None):
                user._prefetched_objects_cache = {}

            return Response(serializer.data)

        if request.method == 'DELETE':
            raise MethodNotAllowed(method='DELETE')

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return (AdminOnly(),)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenreSerializer


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
