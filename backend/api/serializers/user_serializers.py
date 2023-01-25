from django.contrib.auth import get_user_model, authenticate
import django.contrib.auth.password_validation as validators
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Recipe
from users.models import Subscribe
from foodgram.settings import ERR_AUTH_MSG

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def validate_password(self, password):
        validators.validate_password(password)
        return password


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Subscribe.objects.filter(subscriber=user, author=obj).exists()


class TokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label='Email',
        write_only=True,
    )
    password = serializers.CharField(
        label='Пароль',
        write_only=True,
    )
    token = serializers.CharField(
        label='Токен',
        read_only=True,
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            email=email,
            password=password,
        )
        if not user:
            raise serializers.ValidationError(
                ERR_AUTH_MSG,
                code='authorization',
            )
        attrs['user'] = user
        return attrs


class UserPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        label='Текущий пароль'
    )
    new_password = serializers.CharField(
        label='Новый пароль'
    )

    def validate_current_password(self, current_password):
        user = self.context['request'].user
        if not authenticate(
                email=user.email,
                password=current_password,
        ):
            raise serializers.ValidationError(
                ERR_AUTH_MSG,
                code='authorization'
            )
        return current_password

    def validate_new_password(self, new_password):
        validators.validate_password(new_password)
        return new_password

    def create(self, validated_data):
        user = self.context['request'].user
        user.set_password(
            validated_data.get('new_password')
        )
        user.save()
        return validated_data


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='author.id'
    )
    email = serializers.ReadOnlyField(
        source='author.email'
    )
    username = serializers.ReadOnlyField(
        source='author.username'
    )
    first_name = serializers.ReadOnlyField(
        source='author.first_name'
    )
    last_name = serializers.ReadOnlyField(
        source='author.last_name'
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return Subscribe.objects.filter(
            subscriber=obj.subscriber,
            author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return SubscribeRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
