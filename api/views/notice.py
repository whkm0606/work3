import itertools
import collections
import json
from urllib import request

from django.forms import model_to_dict
from rest_framework import serializers
from django.http import JsonResponse
from rest_framework.filters import BaseFilterBackend
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from api.serializer.pages import MaxBaseFilterBackend, MinBaseFilterBackend, NewsListLimitOffsetPagination
from api.serializer.auth import GeneralAuthentication,UserAuthentication
from django.db.models import Max
from api import models
import collections
from django.db.models import F
class CreateNoticeModelSerializer(serializers.ModelSerializer):
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    class Meta:
        model = models.Notice
        # fields = "__all__"
        exclude = [ ]

    def create(self, validated_data):
        content = validated_data.pop('content')##切割newDetail字典数据
        print(content)
        # 获取用户信息
        notice_object = models.Notice.objects.create(content = content )##创建notice表中数据


        return notice_object


class ListNoticeModelSerializer(serializers.ModelSerializer):
    # topic = serializers.SerializerMethodField()
    # user = serializers.SerializerMethodField()
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = models.Notice
        # filter = ['id','content','create_date']
        exclude = []

class NoticeView(CreateAPIView, ListAPIView):

    """
    获取动态列表
    """
    serializer_class = ListNoticeModelSerializer
    queryset = models.Notice.objects.order_by('-id')
    pagination_class = NewsListLimitOffsetPagination
    filter_backends = [MinBaseFilterBackend, MaxBaseFilterBackend]
#加到最小值，最大值

    def perform_create(self, serializer):
        # 调用save 其先调用creat()
        notice_object = serializer.save()
        return notice_object

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateNoticeModelSerializer
        if self.request.method == 'GET':
            return ListNoticeModelSerializer

class NoticeDeleteView(APIView):
    def post(self, request, *args, **kwargs):
        notice_id = json.loads(request.body.decode('utf8')).get('NoticeId')
        print(notice_id)
        if not notice_id:
            return Response({'status': False, 'message': "请传入有效id"})
        models.Notice.objects.filter(id=notice_id).delete()

        return Response({'status': True, 'message': '删除成功'})