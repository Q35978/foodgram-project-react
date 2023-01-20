from io import BytesIO

from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import Exists, OuterRef, Value
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from rest_framework import generics, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)


from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAdminOrReadOnly

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    UserFavourite,
    ShoppingCart
)

from users.models import Subscribe

from .serializers import (
    TagSerializer,
    UserCreateSerializer,
    UserListSerializer,
    TokenSerializer,
    UserPasswordSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeEditSerializer,
    SubscribeRecipeSerializer,
    SubscribeSerializer
)

from foodgram.settings import SHOPPING_CART_FILENAME


User = get_user_model()


class PermissionAndPaginationMixin:
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class TagsViewSet(
        PermissionAndPaginationMixin,
        viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(
        PermissionAndPaginationMixin,
        viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter


class AddOrDeleteSubscribe(generics.RetrieveDestroyAPIView,
                           generics.ListCreateAPIView):
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        return self.request.user.subscriber.select_related(
            'subscribing'
        ).prefetch_related(
            'subscribing__recipe'
        ).annotate(
            recipes_count=Count('ubscribing__recipe'),
            is_subscribed=Value(True),
        )

    def get_object(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    def create(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user.subscriber.filter(author=instance).exists():
            return Response(
                {'errors': 'Вы уже подписаны!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.user.id == instance.id:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subs = request.user.subscriber.create(author=instance)
        serializer = self.get_serializer(subs)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.subscriber.filter(author=instance).delete()


class GetListObjectUseRecipeMixin:
    serializer_class = SubscribeRecipeSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.check_object_permissions(self.request, recipe)
        return recipe


class AddOrDeleteFromFavorite(
        GetListObjectUseRecipeMixin,
        generics.RetrieveDestroyAPIView,
        generics.ListCreateAPIView):
    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        request.user.user_favorites.recipe.add(instance)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def perform_destroy(self, instance):
        self.request.user.user_favorites.recipe.remove(instance)


class AddOrDeleteFromShoppingCart(
        GetListObjectUseRecipeMixin,
        generics.RetrieveDestroyAPIView,
        generics.ListCreateAPIView):
    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        request.user.shopping_cart.recipe.add(instance)
        return Response(
            serializer.data,
            tatus=status.HTTP_201_CREATED
        )

    def perform_destroy(self, instance):
        self.request.user.shopping_cart.recipe.remove(instance)


class AuthToken(ObtainAuthToken):
    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)

    @cache_page(60 * 15)
    @csrf_protect
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': token.key},
            status=status.HTTP_201_CREATED
        )


class UsersViewSet(UserViewSet):
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return (
            User.objects.annotate(
                is_subscribed=Exists(
                    self.request.user.subscriber.filter(author=OuterRef('id'))
                )
            ).prefetch_related(
                'subscriber',
                'subscribing'
            ) if self.request.user.is_authenticated else User.objects.annotate(
                is_subscribed=Value(False))
        )

    def get_serializer_class(self):
        if self.request.method.upper() == 'POST':
            return UserCreateSerializer
        return UserListSerializer

    def perform_create(self, serializer):
        password = make_password(self.request.data['password'])
        serializer.save(password=password)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = Subscribe.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


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
            'ingredients',
            'recipe',
            'shopping_cart',
            'user_favorite'
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
        tmp_storage = BytesIO()
        page = canvas.Canvas(tmp_storage)
        x_coordinate = 60
        y_coordinate = 700
        shopping_cart = (
            request.user.shopping_cart.recipe.
            values(
                'ingredients_list__name',
                'ingredients_list__measurement_unit'
            ).annotate(amount=Sum('recipe__amount')).order_by())
        page.setFont('Vera', 12)
        if not shopping_cart:
            page.setFont('Vera', 24)
            page.drawString(
                x_coordinate,
                y_coordinate,
                'Cписок пуст!')
            page.save()
            tmp_storage.seek(0)
            return FileResponse(
                tmp_storage,
                as_attachment=True,
                filename=SHOPPING_CART_FILENAME)

        indent = 20
        page.drawString(
            x_coordinate,
            y_coordinate,
            'Cписок:'
        )
        for recipe in shopping_cart:
            y_with_indent = y_coordinate - indent
            page.drawString(
                x_coordinate,
                y_with_indent,
                f'* {recipe["ingredients_list__name"]} - '
                f'{recipe["quantity"]}, '
                f'{recipe["ingredients_list__measurement_unit"]}.')
            y_coordinate -= 15
            if y_coordinate <= 60:
                page.showPage()
                y_coordinate = 700
        page.save()
        tmp_storage.seek(0)
        return FileResponse(
            tmp_storage,
            as_attachment=True,
            filename=SHOPPING_CART_FILENAME
        )


@api_view(['post'])
def change_password(request):
    serializer = UserPasswordSerializer(
        data=request.data,
        context={'request': request}
    )
    if not serializer.is_valid():
        return Response(
            {'error': 'Введите верные данные!'},
            status=status.HTTP_400_BAD_REQUEST
        )
    serializer.save()
    return Response(
        {'message': 'Пароль изменен!'},
        status=status.HTTP_201_CREATED
    )
