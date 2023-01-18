from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    TagsViewSet,
    IngredientsViewSet,
    RecipesViewSet,
    AddOrDeleteFromFavorite,
    AddOrDeleteFromShoppingCart,
    UsersViewSet,
    AuthToken,
    AddOrDeleteSubscribe,
    change_password
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
    path(
        'users/<int:user_id>/subscribe/',
        AddOrDeleteSubscribe.as_view(),
        name='subscribe'
    ),
    path(
        'recipes/<int:recipe_id>/favorite/',
        AddOrDeleteFromFavorite.as_view(),
        name='favorite_recipe'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        AddOrDeleteFromShoppingCart.as_view(),
        name='shopping_cart'
    ),
]
