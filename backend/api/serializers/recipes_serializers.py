from django.contrib.auth import get_user_model

from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientsList,
    ShoppingCart,
    UserFavourite,
)

from users.models import Subscribe

from api.serializers.user_serializers import UserSerializer


User = get_user_model()


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
        source='ingredient',
        slug_field='name',
        read_only=True
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientsList
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit',
        )


class IngredientsInListEditSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsList
        fields = (
            'id',
            'amount'
        )

    def validate_amount(self, data):
        if not int(data) > 0:
            raise serializers.ValidationError(
                {'error': 'Количество ингредиента введено не корректно!'}
            )
        return data


class RecipeUserSerializer(serializers.ModelSerializer):
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
        if not user.is_authenticated:
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
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.user_favorite.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=user).exists()


class RecipeEditSerializer(serializers.ModelSerializer):
    author = UserSerializer(
        read_only=True
    )
    image = Base64ImageField(
        max_length=None,
        use_url=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientsInListEditSerializer(
        source='recipe',
        many=True
    )

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('Нужен хотя бы один'
                                              ' тэг для рецепта!')
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(
                    'Указанного тега не существует')
        return tags

    def validate_ingredients(self, ingredients):
        ingredients_list = [
            item['id'] for item in ingredients
        ]
        if not ingredients_list:
            raise serializers.ValidationError('Список ингреиентов не'
                                              ' может быть пустым!')
        all_count_ingredients = len(ingredients_list)
        distinct_count_ingredients = len(set(ingredients_list))
        if not all_count_ingredients == distinct_count_ingredients:
            raise serializers.ValidationError('Ингредиенты должны'
                                              ' быть уникальными')
        return ingredients

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть не 0'
            )
        return cooking_time

    def create_ingredients(self, ingredients, recipe):
        IngredientsList.objects.bulk_create(
            IngredientsList(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        user = self.context.get('request').user
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientsList.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data


class RecipeReducedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserFavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFavourite
        fields = (
            'user',
            'recipe',
        )

    def validate(self, data):
        user = data['user']
        if user.user_favorite.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.'
            )
        return data

    def to_representation(self, instance):
        return RecipeReducedSerializer(
            instance.recipe,
            context={
                'request': self.context.get('request')
            }
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe',
        )

    def validate(self, data):
        user = data['user']
        if user.shopping_cart.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину'
            )
        return data

    def to_representation(self, instance):
        return RecipeReducedSerializer(
            instance.recipe,
            context={
                'request':
                    self.context.get('request')
            }
        ).data
