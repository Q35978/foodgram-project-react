from django.contrib.auth import get_user_model
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
    id = serializers.IntegerField()
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
                'Количество ингредиента введено не корректно!'
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
        ingredients_list = data['ingredients']
        dict_for_error = {}
        if not ingredients_list:
            dict_for_error['ingredients'] = ('Список ингреиентов не'
                                             ' может быть пустым!')
        tags = data['tags']
        if not tags:
            dict_for_error['tags'] = 'Нужен хотя бы один тэг для рецепта!'
        for tag_name in tags:
            if not Tag.objects.filter(name=tag_name).exists():
                dict_for_error['tags'] = (
                    dict_for_error['tags']
                    + f'Тэга {tag_name} не существует! '
                )
        added_ingredients_list = set()
        for item in ingredients_list:
            id_item = item['id']
            if id_item in added_ingredients_list:
                ingredient = get_object_or_404(
                    Ingredient,
                    id=item['id']
                )
                if not dict_for_error['ingredient']:
                    dict_for_error['ingredient'] = (
                        dict_for_error['ingredient']
                        + f'Ингридиент {ingredient} уже добавлен!'
                    )
                added_ingredients_list.append(id_item)
        if dict_for_error:
            raise serializers.ValidationError(dict_for_error)
        return data

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть не 0'
            )
        return cooking_time

    def create_ingredients(self, ingredients, recipe):
        list_ingredients = []
        for ingredient in ingredients:
            new_ingredient_row = IngredientsList(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient.get('amount'),
            )
            list_ingredients.append(new_ingredient_row)
        IngredientsList.objects.bulk_create(list_ingredients)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_list(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags')
            )
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients_list.clear()
            self.create_ingredients_list(ingredients, instance)
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
