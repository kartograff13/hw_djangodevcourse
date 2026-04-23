from rest_framework import pagination


class StandardResultsSetPagination(pagination.PageNumberPagination):
    """Стандартная пагинация для API с постраничной навигацией"""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
