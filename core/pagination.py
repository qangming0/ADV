#!/usr/bin/python
# -*- coding: utf8 -*-


import json
from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    # page_size_query_param = 'perpage'
    page_size = 25
    page_size_query_param = 'page_size'
    # max_page_size = 1000
    def __init__(self):
        pass

    def paginate_queryset(self, queryset, request, view=None):
        dctUrlParams = request.query_params
        if 'flt' in dctUrlParams:
            try:
                dctFilterAttrs = json.loads(dctUrlParams.get('flt') or '')
                if 'perpage' in dctFilterAttrs:
                    self.page_size = int(dctFilterAttrs.get('perpage'))
            except Exception as ex:
                dctFilterAttrs = None

        return super(CustomPagination, self).paginate_queryset(queryset=queryset, request=request, view=view)

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'page_size': self.page_size,
            'num_pages': self.page.paginator.num_pages,
            'results': data
        })