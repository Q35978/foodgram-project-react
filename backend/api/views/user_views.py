from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models.expressions import Exists, OuterRef, Value
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)

from users.models import Subscribe

from api.serializers.user_serializers import (
    UserCreateSerializer,
    UserSerializer,
    TokenSerializer,
    UserPasswordSerializer,
    SubscribeSerializer
)

User = get_user_model()


class AuthToken(ObtainAuthToken):
    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': token.key},
            status=status.HTTP_201_CREATED
        )


class UsersViewSet(UserViewSet):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return User.objects.annotate(is_subscribed=Value(False))
        return User.objects.annotate(
            is_subscribed=Exists(
                self.request.user.subscriber.filter(author=OuterRef('id'))
            )
        ).prefetch_related('subscriber', 'subscribing')

    def get_serializer_class(self):
        if self.request.method.upper() == 'POST':
            return UserCreateSerializer
        return UserSerializer

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

    @action(
        detail=True,
        methods=[
            'POST',
            'DELETE'
        ],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)
        if request.method == 'DELETE':
            get_object_or_404(
                Subscribe,
                user=user,
                author=author,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = SubscribeSerializer(
            author,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        Subscribe.objects.create(
            user=user,
            author=author
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
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
