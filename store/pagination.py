from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


class MyDefaultPaginationClass(PageNumberPagination):
    page_size = 10