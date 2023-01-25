from django.contrib.auth import get_user_model
from django.db.models.aggregates import Sum
from django.db.models.expressions import Exists, OuterRef, Value
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    SAFE_METHODS,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)

from api.filters import IngredientFilter, RecipeFilter

from api.permissions import IsAdminOrReadOnly

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientsList,
    UserFavourite,
    ShoppingCart,
)

from api.serializers.recipes_serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeEditSerializer,
    UserFavouriteSerializer,
    ShoppingCartSerializer,
)

from foodgram.settings import SHOPPING_CART_FILENAME


User = get_user_model()


class PermissionAndPaginationMixin:
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class TagsViewSet(
    PermissionAndPaginationMixin,
    viewsets.ModelViewSet
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(
    PermissionAndPaginationMixin,
    viewsets.ModelViewSet
):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeEditSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Recipe.objects.annotate(
                is_in_shopping_cart=Value(False),
                is_favorited=Value(False),
            ).select_related('author').prefetch_related(
                'tags',
                'author',
                'ingredients',
                'recipe',
                'shopping_cart',
                'user_favorite'
            )
        return Recipe.objects.annotate(
            is_favorited=Exists(
                UserFavourite.objects.filter(
                    user=self.request.user,
                    recipe=OuterRef('id')
                )
            ),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    user=self.request.user,
                    recipe=OuterRef('id')
                )
            )
        ).select_related('author').prefetch_related(
            'tags',
            'author',
            'ingredients',
            'recipe',
            'shopping_cart',
            'user_favorite'
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if self.request.method.upper() == 'DELETE':
            get_object_or_404(
                ShoppingCart,
                user=request.user,
                recipe=get_object_or_404(Recipe, id=pk)
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = ShoppingCartSerializer(
            data=data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @staticmethod
    def send_message(ingredients):
        shopping_cart = 'Список покупок:'
        for ingredient in ingredients:
            shopping_cart += (
                f"\n * {ingredient['ingredient__name']} "
                f"- {ingredient['amount']}"
                f", {ingredient['ingredient__measurement_unit']}")
        response = HttpResponse(
            shopping_cart,
            content_type='text/plain'
        )
        response['Content-Disposition'] = (f'attachment; filename'
                                           f'="{SHOPPING_CART_FILENAME}"')
        return response

    @action(
        detail=False,
        methods=['GET']
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientsList.objects.filter(
            recipe__shopping_cart__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return self.send_message(ingredients)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if self.request.method.upper() == 'DELETE':
            get_object_or_404(
                UserFavourite,
                user=request.user,
                recipe=get_object_or_404(Recipe, id=pk)
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        context = {"request": request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = UserFavouriteSerializer(
            data=data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
