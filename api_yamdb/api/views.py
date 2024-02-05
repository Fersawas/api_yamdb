from rest_framework import viewsets, filters, mixins
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    IsAdminUser,
    AllowAny
)

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import api_view, permission_classes

from django.shortcuts import get_object_or_404

from reviews.models import Review, Genre, Category, Title

from .permissions import IsAdminOrRead
from .serializers import CategorySerializer, GenreSerializer, TitleSerializer


class ReviewViewSet(viewsets.ViewSet):
    pass


class DestroyCreateViewSet(viewsets.GenericViewSet,
                           mixins.CreateModelMixin,
                           mixins.DestroyModelMixin):

    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter)
    search_fields = ('slug')

    @permission_classes([IsAdminUser])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @permission_classes([IsAdminUser])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)  


class CategoryViewSet(DestroyCreateViewSet,
                      mixins.ListModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(mixins.ListModelMixin,
                   DestroyCreateViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrRead,]
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('category', 'genre', 'name', 'year')
    pagination_class = LimitOffsetPagination