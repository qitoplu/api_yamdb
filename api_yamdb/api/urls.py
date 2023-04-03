from django.urls import include, path
from rest_framework import routers

from .views import (SignUpView, TokenView,
                    UserViewSet, CategoryViewSet,
                    GenreViewSet, TitleViewSet, CommentViewSet,
                    ReviewViewSet,)

v1_router = routers.DefaultRouter()
v1_router.register('users', UserViewSet)
v1_router.register('categories', CategoryViewSet)
v1_router.register('genres', GenreViewSet)
v1_router.register('titles', TitleViewSet)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)

urlpatterns = [
    path(
        'v1/auth/signup/',
        SignUpView.as_view({'post': 'create', 'get': 'retrieve'}),
        name='auth-signup'
    ),
    path(
        'v1/auth/token/',
        TokenView.as_view(),
        name='auth-token'
    ),
    path('v1/', include(v1_router.urls)),
]
