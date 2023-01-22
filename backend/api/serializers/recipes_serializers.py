from django.contrib.auth import get_user_model

from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientsList,
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

    def validate(self, data):
        ingredients_list = [
            item['ingredient'] for item in data['ingredients']
        ]
        error_text = {}
        if not ingredients_list:
            error_text['error'] = (error_text['error']
                                   + ('Список ингреиентов не'
                                      ' может быть пустым!'))
        tags = data['tags']
        if not tags:
            error_text['error'] = (error_text['error']
                                   + ('Нужен хотя бы один'
                                      ' тэг для рецепта!'))
        for tag_name in tags:
            if not Tag.objects.filter(name=tag_name).exists():
                error_text['error'] = (error_text['error']
                                       + (f'Тэга {tag_name} не существует!'))
        all_count_ingredients = len(ingredients_list)
        distinct_count_ingredients = len(set(ingredients_list))
        if not all_count_ingredients == distinct_count_ingredients:
            error_text['error'] = (error_text['error']
                                   + ('Ингредиенты должны быть уникальными'))
        if error_text['error']:
            raise serializers.ValidationError(error_text['error'])
        return data

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
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags')
            )
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
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
