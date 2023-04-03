from django.urls import include, path
from rest_framework import routers

from .views import (SignUpView, TokenView,
                    UserViewSet)

router = routers.DefaultRouter()
router.register('users', UserViewSet)

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
    path('v1/', include(router.urls)),
]
