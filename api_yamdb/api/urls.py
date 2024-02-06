from django.urls import path, include

from rest_framework import routers
from . import views

from api.views import (
    CategoryViewSet, GenreViewSet, TitleViewSet, UserViewSet, ReviewViewSet, CategoryViewSet,
    CommentViewSet
)

router = routers.SimpleRouter()

router.register(r'api/v1/titles', TitleViewSet, basename='title')
router.register(r'api/v1/users', UserViewSet, basename='users')
router.register(r'api/v1/titles/(?P<title_pk>\d+)/reviews', ReviewViewSet, basename='review')
router.register(r'api/v1/categories', CategoryViewSet)
router.register(r'api/v1/genres', GenreViewSet)
router.register(r'api/v1/titles/(?P<title_pk>\d+)/reviews/(?P<review_pk>\d+)/comments',
                CommentViewSet, basename='comment' )

urlpatterns = [
    path('', include(router.urls)),
    path('api/v1/auth/signup/', views.send_confcode_to_user),
    path('api/v1/auth/token/', views.send_token_to_user)
]