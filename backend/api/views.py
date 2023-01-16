from django.shortcuts import get_object_or_404

from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    RecipeReadCaptionSerializer,
)
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientsList,
    UserFavourite,
    ShoppingCart,
)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def add_to_list_object(self, model, user, pk):
        obj = model.objects.filter(
            user=user,
            recipe__id=pk
        )
        if obj.exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(
            Recipe,
            id=pk
        )
        model.objects.create(
            user=user,
            recipe=recipe
        )
        serializer = RecipeReadCaptionSerializer(recipe)
        return Response(
            serializer.data,
            status=HTTP_201_CREATED
        )

    def delete_from_list_object(self, model, user, pk):
        obj = model.objects.filter(
            user=user,
            recipe__id=pk
        )
        if not obj.exists():
            return Response(
                {'errors': 'Вы пытаетесь удалить удаленный рецепт!'},
                status=HTTP_400_BAD_REQUEST
            )
        obj.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=[
            'post',
            'delete'
        ],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to_list_object(
                UserFavourite,
                request.user,
                pk
            )
        else:
            return self.delete_from_list_object(
                UserFavourite,
                request.user,
                pk
            )

    @action(
        detail=True,
        methods=[
            'post',
            'delete'
        ],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to_list_object(
                ShoppingCart,
                request.user,
                pk
            )
        else:
            return self.delete_from_list_object(
                ShoppingCart,
                request.user,
                pk
            )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        today = datetime.today()
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredients_list = IngredientsList.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(quantity=Sum('quantity'))
        shopping_list = (
            f'Список покупок на дату {today:%d.%m.%Y}\n'
        )
        shopping_list += '\n'.join(
            [
                f'* {ingredient["ingredient__name"]} '
                f' - {ingredient["quantity"]}'
                f' {ingredient["ingredient__measurement_unit"]};'
                for ingredient in ingredients_list
            ]
        )
        shopping_list += (
            f'\n\n для пользователя {user.username}.',
            '\n\n Cгенерировано в Foodgram!'
        )
        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
