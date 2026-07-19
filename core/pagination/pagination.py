"""Page-number pagination that conforms to the project's response envelope."""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from utils.response import success_response


class StandardResultsSetPagination(PageNumberPagination):
    """Default pagination: 20 per page, capped at 100, ``?page_size=`` override."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data: list) -> Response:
        assert self.page is not None
        return success_response(
            data={
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
