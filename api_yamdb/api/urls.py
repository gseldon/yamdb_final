from django.urls import include, path
from rest_framework import routers

from .views import (
    CategoryViewSet, CommentViewSet, GenreViewSet,
    ReviewViewSet, TitleViewSet, UserViewSet, get_token,
    send_code
)

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('titles', TitleViewSet)
router.register('genres', GenreViewSet)
router.register('categories', CategoryViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews',
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)
authpatterns = [
    path('signup/', send_code, name='send_code'),
    path('token/', get_token, name='get_token'),
]
urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include(authpatterns)),
]
