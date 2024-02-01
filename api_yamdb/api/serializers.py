from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Genre, Title

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fileds = '__all__'
        models = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        models = Genre


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(required=False, many=True)
    category = serializers.StringRelatedField()

    class Meta:
        fields = '__all__'
        models = Title
