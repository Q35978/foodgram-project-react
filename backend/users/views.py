from api.pagination import CustomPagination
from api.serializers import CustomUserSerializer
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
