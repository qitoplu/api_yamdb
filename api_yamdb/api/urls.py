from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenreViewSet

v1_router = DefaultRouter()
v1_router.register('genres', GenreViewSet)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
