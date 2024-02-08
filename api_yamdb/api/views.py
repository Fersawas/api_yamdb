from rest_framework import viewsets, filters, mixins
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    IsAdminUser,
    AllowAny, 
)


from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework import status, filters

from rest_framework_simplejwt.tokens import RefreshToken

from django.shortcuts import get_object_or_404
from django.core.mail import send_mail 
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg



from reviews.models import Review, Genre, Category, Title, Comment, UserMain

from .filters import TitleFilter
from .permissions import (
    IsAdminOrUserOrRead, IsAdmin, IsAdminOrRead, IsAuthOrAdminOrModerOrRead, IsAdminNoRead)
from .serializers import (
    CategorySerializer, GenreSerializer, TitleSerializer, AuthSerializer, TokenSerializer,
    UserSerializer, ReviewSerializer, ComentSerializer, TitleSerializerGet
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def send_confcode_to_user(request):
    ''' Отправка кода подтверждения на почту '''
    serializer = AuthSerializer(data=request.data)
    if UserMain.objects.filter(username=request.data.get('username'),
                               email=request.data.get('email')).exists():
        return Response({'granted': 'granted'}, status=status.HTTP_200_OK)
    if serializer.is_valid():
        serializer.save()
        email = serializer.validated_data['email']
        user = get_object_or_404(UserMain, email=email)
        confirmation_code = default_token_generator.make_token(user)
        send_mail('Confirm code', f'your confirmation code {confirmation_code}',
                  'yamdb@yamd.ru', [email,])
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_token_to_user(request):
    ''' Отправление пользователю токена '''
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(UserMain, username=serializer.validated_data['username'])
    if default_token_generator.check_token(user, serializer.validated_data['confirmation_code']):
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token)
        }, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthOrAdminOrModerOrRead, ]
    http_method_names = ['patch', 'get', 'head', 'post', 'delete']
    
    def get_queryset(self):
        print(self.kwargs['title_pk'])
        title = get_object_or_404(
            Title.objects.filter(id=self.kwargs['title_pk'])
        )        
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title.objects.filter(id=self.kwargs['title_pk'])
        )    
        serializer.save(
            author=self.request.user, title=title
        )


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = ComentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAuthOrAdminOrModerOrRead, ]
    http_method_names = ['patch', 'get', 'head', 'post', 'delete']

    def get_queryset(self):
        review = get_object_or_404(
            Review.objects.filter(id=self.kwargs['review_pk']))
        return Comment.objects.filter(review=review)
    
    def perform_create(self, serializer):
        review = get_object_or_404(
            Review.objects.filter(id=self.kwargs['review_pk']))
        serializer.save(
            author=self.request.user, review=review)


class DestroyCreateViewSet(viewsets.GenericViewSet,
                           mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.ListModelMixin):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', )
    permission_classes = [IsAdmin,]
    lookup_field = 'slug'


class CategoryViewSet(DestroyCreateViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(DestroyCreateViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer



class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrRead,]
    filterset_class= TitleFilter
    
    pagination_class = LimitOffsetPagination
    http_method_names = ['patch', 'get', 'head', 'post', 'delete']

    def get_queryset(self):
        if self.action in ('list', 'retrieve'):
            return Title.objects.annotate(rating=Avg('review__score'))
        return Title.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializerGet
        return TitleSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = UserMain.objects.all()
    lookup_field = 'username'
    permission_classes = [IsAdminNoRead,]
    filter_backends = [filters.SearchFilter]
    search_fields=['username', ]
    http_method_names = ['patch', 'get', 'head', 'post', 'delete']
    
    @action(url_path='me', methods=['patch', 'get'],
            detail=False, permission_classes=[IsAuthenticated,])
    def get_info(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        if request.method == 'PATCH':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=UserMain.USER)
        return Response(serializer.data)
