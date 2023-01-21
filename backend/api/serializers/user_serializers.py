from django.contrib.auth import get_user_model, authenticate
import django.contrib.auth.password_validation as validators
from django.contrib.auth.hashers import make_password

from rest_framework import serializers

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


class UserListSerializer(serializers.ModelSerializer):
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
            request=self.context.get('request'),
            email=email,
            password=password
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
        user = authenticate(
            email=self.context.get('request').email,
            password=current_password
        )
        if not user:
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
        password = make_password(
            validated_data.get('new_password'))
        user.password = password
        user.save()
        return validated_data


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(
        source='author.email'
    )
    author_username = serializers.CharField(
        source='author.username'
    )
    author_first_name = serializers.CharField(
        source='author.first_name'
    )
    author_last_name = serializers.CharField(
        source='author.last_name'
    )
    recipes = serializers.SerializerMethodField(
        read_only=True
    )
    is_subscribed = serializers.BooleanField(
        read_only=True
    )
    recipes_count = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = Subscribe
        fields = (
            'id',
            'author_email',
            'author_username',
            'author_first_name',
            'author_last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        author_recipes = obj.author.recipe.all()
        return SubscribeRecipeSerializer(
            author_recipes,
            many=True
        ).data

    def get_recipes_count(self, obj):
        return obj.author.recipe.count()
