from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.user_views import (
    UsersViewSet,
    AuthToken,
    change_password
)
from api.views.recipes_views import (
    TagsViewSet,
    IngredientsViewSet,
    RecipesViewSet,
)


app_name = 'api'

router = DefaultRouter()
router.register(
    'tags',
    TagsViewSet
)
router.register(
    'ingredients',
    IngredientsViewSet
)
router.register(
    'recipes',
    RecipesViewSet
)
router.register(
    'users',
    UsersViewSet
)

urlpatterns = [
    path(
        '',
        include(router.urls)
    ),
    path(
        '',
        include('djoser.urls')
    ),
    path(
        'auth/',
        include('djoser.urls.authtoken')
    ),
    path(
        'auth/token/login/',
        AuthToken.as_view(),
        name='login'
    ),
    path(
        'users/set_password/',
        change_password,
        name='set_password'
    ),
]
