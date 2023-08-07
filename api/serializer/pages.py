from rest_framework.filters import BaseFilterBackend
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework import status
from rest_framework.response import Response
from collections import OrderedDict


class MinBaseFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        min_id = request.query_params.get('min_id')
        if min_id:
            return queryset.filter(id__lt=min_id).order_by('-id')
        return queryset


class MaxBaseFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        max_id = request.query_params.get('max_id')
        if max_id:
            # 大于第一次获取的id数据(即新值)
            return queryset.filter(id__gt=max_id).order_by('id')
        return queryset
class NewsListLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 6
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 50

    # 从哪个位置取(重写为0)
    def get_offset(self, request):
        return 0

    def get_paginated_response(self, data):
        return Response(data, status=status.HTTP_200_OK)


class AuctionPagination(PageNumberPagination):
    # 默认显示多少个数据
    page_size = 4
    # 最大显示多少个数据
    max_page_size = 4
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('results', data)
        ]))
