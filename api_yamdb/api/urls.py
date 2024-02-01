from django.urls import path, include

from rest_framework import routers

from api.views import CategoryViewSet, GenreViewSet, TitleViewSet

router = routers.DefaultRouter()

router.register(r'titles', TitleViewSet)

urlpatterns = [
    path('categoties/', CategoryViewSet.as_view({
        'get': 'list',
        'post': 'create',
        'delete': 'destroy'
    }), name='category'),
    path('genres/', GenreViewSet.as_view({
        'get': 'list',
        'post': 'create',
        'delete': 'destroy'
    }), name='genre'),
    path('', include(router.urls))
]