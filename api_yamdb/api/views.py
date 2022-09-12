from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt import tokens
from reviews.filters import TitleFilter
from reviews.models import Categories, Genres, Review, Title
from users.models import User

from .permissions import (IsAdmin, IsAdminOrReadOnly, IsAuthorOrAdmin,
                          IsAuthorOrAdminOrModeratorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer, Confirmation,
                          GenreSerializer, Registration, ReviewSerializer,
                          TitleSerializer, TitleViewSerializer, UserSerializer)


class CreateListDestroyViewSet(
    CreateModelMixin, ListModelMixin,
    DestroyModelMixin, GenericViewSet
):
    pass


@api_view(['POST'])
def send_code(request):
    serializer = Registration(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    username = serializer.data.get('username')
    user, created = User.objects.get_or_create(
        email=email,
        username=username
    )
    confirmation_code = PasswordResetTokenGenerator().make_token(user)
    send_mail(
        'Код подтверждения для Yamdb',
        f'Ваш код подтверждения: {confirmation_code}',
        settings.ADMIN_MAIL,
        [email]
    )
    answer = {'email': email, 'username': username}
    return Response(
        answer,
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def get_token(request):
    serializer = Confirmation(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.data.get('username')
    confirmation_code = serializer.data.get('confirmation_code')
    user = get_object_or_404(User, username=username)
    if not PasswordResetTokenGenerator().check_token(user, confirmation_code):
        return Response(
            {'confirmation_code': 'Invalid confirmation code'},
            status=status.HTTP_400_BAD_REQUEST
        )
    token = tokens.AccessToken.for_user(user)
    return Response({'token': f'{token}'}, status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin, IsAuthenticated]
    filter_backends = [SearchFilter]
    lookup_field = 'username'
    search_fields = ['username']

    @action(
        methods=['patch', 'get'],
        permission_classes=[IsAuthenticated, IsAuthorOrAdmin],
        detail=False,
        url_path='me',
        url_name='me'
    )
    def me(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(user)
        if self.request.method == 'PATCH':
            if not (user.is_admin or user.is_moderator) and not user.is_staff:
                return Response(serializer.data)
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('review__score')
    ).order_by('pk')
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filterset_class = TitleFilter
    filter_backends = (DjangoFilterBackend, SearchFilter)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleViewSerializer
        return TitleSerializer

    def perform_create(self, serializer):
        category = Categories.objects.get(
            slug=self.request.data.get('category')
        )
        genre = Genres.objects.filter(
            slug__in=self.request.data.getlist('genre')
        )
        description = self.request.data.get('description')
        return serializer.save(
            category=category, genre=genre, description=description
        )

    def perform_update(self, serializer):
        category = get_object_or_404(
            Categories, slug=self.request.data.get('category')
        )
        return serializer.save(category=category)


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly, ]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ('name', )
    search_fields = ('name', 'slug')
    lookup_field = 'slug'


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, )
    search_fields = ('name',)

    def destroy(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        slug = self.kwargs.get('pk')
        instance = Categories.objects.filter(slug=slug)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrAdminOrModeratorOrReadOnly, ]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id).all()

    def create(self, request, *args, **kwargs):
        review_have_this_author = Review.objects.filter(
            title=self.kwargs.get('title_id'), author=self.request.user
        ).exists()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if bool(review_have_this_author):
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(
            author=self.request.user,
            title=title,
        )


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrAdminOrModeratorOrReadOnly, ]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        try:
            review = get_object_or_404(
                Review,
                id=self.kwargs.get('review_id'),
                title_id=self.kwargs.get('title_id')
            )
        except TypeError:
            TypeError('Нет ревью на это произведение')
        return review.comments.all()

    def perform_create(self, serializer):
        try:
            review = get_object_or_404(
                Review,
                id=self.kwargs.get('review_id'),
                title_id=self.kwargs.get('title_id')
            )
        except TypeError:
            TypeError('Нет отзыва у этого произведения')
        serializer.save(author=self.request.user, review=review)
