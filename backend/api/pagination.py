from rest_framework.pagination import PageNumberPagination

from foodgram.settings import CUSTOM_PAGE_SIZE


class CustomPagination(PageNumberPagination):
    page_size = CUSTOM_PAGE_SIZE
    page_size_query_param = "limit"
