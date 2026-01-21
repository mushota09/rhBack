"""
Pagination utilities for the application.
"""
from rest_framework.pagination import PageNumberPagination
class GlobalPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'

    def paginate_queryset(self, queryset, request, view=None):
        no_pagination = (
            request.query_params.get('no_pagination', 'false').lower() == 'true'
        )
        if no_pagination:
            return None
        return super().paginate_queryset(queryset, request, view)
