from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models.expressions import Exists, OuterRef, Value
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet

from rest_framework import status

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
)

from users.models import Subscribe

from api.serializers.user_serializers import (
    UserCreateSerializer,
    UserSerializer,
    UserPasswordSerializer,
    SubscribeSerializer
)

User = get_user_model()


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
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request, pk=None):
        user = self.request.user
        serializer = UserPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        serializer_class=SubscribeSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        queryset = Subscribe.objects.filter(subscriber_id=request.user.id)
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
        author = get_object_or_404(User, id=id)
        if self.request.method.upper() == 'DELETE':
            instance = get_object_or_404(
                Subscribe,
                subscriber=request.user,
                author=author
            )
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        subscribe_is_exist = Subscribe.objects.filter(
            subscriber_id=request.user.id,
            author_id=author.id
        ).exists()
        if subscribe_is_exist or request.user == author:
            return Response(
                {'detail': 'Подписка есть или пытайтесь подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        new_subscribe = Subscribe.objects.create(
            subscriber=request.user,
            author=author
        )
        serializer = SubscribeSerializer(
            new_subscribe,
            context={'request': request}
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
