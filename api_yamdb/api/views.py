from rest_framework import filters, status, viewsets
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    DestroyModelMixin
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenViewBase

from reviews.models import User, Category, Genres, Title, Review
from .filters import TitlesFilter
from .permissions import AdminOnly, AdminOrReadOnly, AuthorOrHasRoleOrReadOnly
from .serializers import (
    SignUpSerializer,
    TokenSerializer,
    UserSerializer,
    CategorySerializer,
    GenreSerializer,
    FirstTitleSerializer,
    SecondTitleSerializer,
    CommentsSerializer,
    ReviewSerializer,
)


class SignUpView(CreateModelMixin,
                 RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get("username", None)
        email = request.data.get("email", None)
        if username:
            user = User.objects.filter(username=username)
            if user.exists():
                user = user.first()
                if email and user.email != email:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                serializer = self.get_serializer(user)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data,
                                status=status.HTTP_200_OK,
                                headers=headers)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data,
                        status=status.HTTP_200_OK,
                        headers=headers)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.data)
        username = serializer.data["username"]
        user = get_object_or_404(User, username=username)
        user.email_user(
            subject='confirmation_code',
            message=user.confirmation_code,
            fail_silently=False
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


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

    @action(methods=['get', 'patch', 'delete'], detail=False)
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        if request.method == 'PATCH':
            partial = request.method = 'PATCH'
            data = request.data.copy()
            data['role'] = request.user.role
            serializer = self.get_serializer(
                request.user,
                data=data,
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(request.user, '_prefetched_objects_cache', None):
                request.user._prefetched_objects_cache = {}

            return Response(serializer.data)

        if request.method == 'DELETE':
            raise MethodNotAllowed(method='DELETE')

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def update(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data,
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return (AdminOnly(),)


class CategoryViewSet(CreateModelMixin, ListModelMixin,
                      DestroyModelMixin, GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateModelMixin, ListModelMixin,
                   DestroyModelMixin, GenericViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title.objects.all().annotate(Avg('reviews__score')).order_by('name')
    )
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return FirstTitleSerializer
        return SecondTitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = (AuthorOrHasRoleOrReadOnly, )

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
    permission_classes = (AuthorOrHasRoleOrReadOnly, )

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)
