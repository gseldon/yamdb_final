from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.models import Categories, Comments, Genres, Review, Title
from users.models import User


class Registration(serializers.Serializer):
    email = serializers.EmailField(
        required=True
    )
    username = serializers.CharField(
        required=True
    )

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError('Недопустимое имя.')
        return username

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')
        if User.objects.filter(email=email, username=username).exists():
            return attrs
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Имя уже существует.')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Почта уже существует.')
        return attrs

    class Meta:
        fields = ('username', 'email')
        model = User


class Confirmation(serializers.Serializer):
    username = serializers.CharField(
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=200,
        required=True
    )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username',
            'bio', 'email', 'role',
        )
        extra_kwargs = {
            'username': {
                'required': True
            },
            'email': {
                'required': True,
                'validators': [
                    UniqueValidator(
                        queryset=User.objects.all()
                    )
                ]
            }
        }


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Review
        fields = (
            'id', 'text', 'author', 'score', 'pub_date', 'title'
        )
        read_only_fields = ('id', 'author', 'title')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Categories


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genres


class TitleViewSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, required=False, read_only=True)
    category = CategorySerializer(required=False, read_only=True)
    rating = serializers.IntegerField()

    class Meta:
        fields = (
            'id', 'name', 'year',
            'description', 'category',
            'genre', 'rating',
        )
        model = Title
        read_only_fields = ('id', 'rating')


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', many=False, queryset=Categories.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        required=False,
        queryset=Genres.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = Title


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Comments
        fields = 'id', 'text', 'author', 'pub_date'
        read_only_fields = ('id', 'author')
