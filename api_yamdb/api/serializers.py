from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from django.contrib.auth.tokens import default_token_generator

from reviews.models import Category, Genre, Title, UserMain, Review, Comment
from django.shortcuts import get_object_or_404



class TokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    confirmation_code = serializers.CharField(required=True)


class AuthSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254)
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    
    class Meta:
        model = UserMain
        fields = ['email', 'username', ]
    
    def create(self, validated_data):
        return UserMain.objects.create(**validated_data)

    
    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'You can`t be "me"'
            )
        elif UserMain.objects.filter(username=value).exists():
            raise serializers.ValidationError('exists')
        return value
    
    def validate_email(self, value):
        if UserMain.objects.filter(email=value).exists():
            raise serializers.ValidationError('exists')
        return value



class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    role = serializers.CharField(required=False)
    def validate_role(self, value):
        if value not in ['user', 'admin', 'moderator'] and not None:
            raise serializers.ValidationError('huita')
        return value

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'You can`t be "me"'
            )
        elif UserMain.objects.filter(username=value).exists():
            raise serializers.ValidationError('exists')
        return value

    def validate_email(self, value):
        if UserMain.objects.filter(email=value).exists():
            raise serializers.ValidationError('exists')
        return value

    class Meta:
        model = UserMain
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio', 
                  'role')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


#class TitleSerializerGet(serializers.Serializer):
#    genre = serializers.SlugRelatedField(queryset=Genre.objects.all(),
#                                         many=True,
#                                         slug_field='slug')
#    category = serializers.SlugRelatedField(queryset=Category.objects.all(),
#                                            slug_field='slug')
#    raiting = serializers.IntegerField()
#    description = serializers.CharField()
#    name = serializers.CharField()
#    class Meta:
#        fields = '__all__'


class TitleSerializerGet(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)
    
    
    class Meta:
        fields = '__all__'
        model = Title


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(queryset=Genre.objects.all(),
                                         many=True,
                                         slug_field='slug')
    category = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                            slug_field='slug')

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    title = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Review

    def validate(self, data):
        if self.context['request'].method == 'POST':
            title_id = self.context['view'].kwargs['title_pk']
            title = get_object_or_404(Title, id=title_id)
            author = self.context['request'].user
            if Review.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже оставляли отзыв к этому произведению')
        return data

class ComentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(read_only=True,
                                          slug_field='text')
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')
    class Meta:
        fields = '__all__'
        model = Comment
