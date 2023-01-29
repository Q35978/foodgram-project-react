from django.urls import include, path
from rest_framework.routers import DefaultRouter
from djoser.views import TokenCreateView, TokenDestroyView

from api.views.user_views import (
    UsersViewSet,
    # set_password
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
        'auth/token/login/',
        TokenCreateView.as_view(),
        name='login'
    ),
    path(
        'auth/token/logout/',
        TokenDestroyView.as_view(),
        name='logout'
    ),
]
