from django.contrib.auth import get_user_model, authenticate
import django.contrib.auth.password_validation as validators
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientsList,
)

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
    is_subscribed = serializers.BooleanField(
        read_only=True
    )

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
        if user.is_anonymous:
            return False
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
        if not email or not password:
            msg = 'Email и пароль обязательные поля'
            raise serializers.ValidationError(
                msg,
                code='authorization'
            )

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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredients',
        read_only=True
    )
    name = serializers.SlugRelatedField(
        source='ingredients',
        slug_field='name',
        read_only=True
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredients',
        slug_field='measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientsList
        fields = (
            'id',
            'name',
            'quantity',
            'measurement_unit',
        )


class IngredientsInListEditSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    quantity = serializers.IntegerField()

    class Meta:
        model = IngredientsList
        fields = (
            'id',
            'name',
            'quantity'
        )


class RecipeUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        read_only=True
    )

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
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(subscriber=user, author=obj).exists()


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(
        many=True,
        read_only=True)
    author = RecipeUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        required=True,
        source='recipe'
    )
    is_favorited = serializers.BooleanField(
        read_only=True
    )
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeEditSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        max_length=None,
        use_url=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients_list = IngredientsInListEditSerializer(
        many=True
    )

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate(self, data):
        ingredients_list = data['ingredients_list']
        if not ingredients_list:
            raise serializers.ValidationError(
                {'ingredients': 'Список ингреиентов не может быть пустым!'}
            )
        added_ingredients_list = []
        for item in ingredients_list:
            if not int(item['quantity']) > 0:
                raise serializers.ValidationError(
                    {
                        'quantity':
                        'Количество ингредиента введено не корректно!'
                    }
                )
            ingredient = get_object_or_404(
                Ingredient,
                id=item['id']
            )
            if ingredient in added_ingredients_list:
                raise serializers.ValidationError(
                    {'ingredients': 'Ингридиент уже добавлен!'}
                )
            added_ingredients_list.append(ingredient)
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError(
                'Нужен хотя бы один тэг для рецепта!'
            )
        for tag_name in tags:
            if not Tag.objects.filter(name=tag_name).exists():
                raise serializers.ValidationError(
                    f'Тэга {tag_name} не существует!'
                )
        return data

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть не 0'
            )
        return cooking_time

    def create_ingredients_list(self, ingredients_list, recipe):
        for ingredient in ingredients_list:
            IngredientsList.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                quantity=ingredient.get('quantity'),
            )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_list = validated_data.pop('ingredients_list')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_list(ingredients_list, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags')
            )
        if 'ingredients_list' in validated_data:
            ingredients_list = validated_data.pop('ingredients_list')
            instance.ingredients_list.clear()
            self.create_ingredients_list(ingredients_list, instance)
        return super().update(
            instance,
            validated_data
        )

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data


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
