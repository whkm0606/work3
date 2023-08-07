import itertools
import collections
from django.forms import model_to_dict
from rest_framework import serializers
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

class ListUserModelSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()


    class Meta:
        model = models.UserInfo
        exclude = ['token', ]

    # def get_topic(self, obj):
    #
    #     if not obj.topic:
    #         return
    #     return model_to_dict(obj.topic, ['id', 'title'])
    #
    # def get_user(self, obj):
    #     return model_to_dict(obj.user, ['id', 'nickname', 'avatar','token'])

class UserView(CreateAPIView, ListAPIView):

    """
    获取动态列表
    """
    serializer_class = ListUserModelSerializer
    queryset = models.UserInfo.objects.prefetch_related('user', 'topic').order_by("id")
    pagination_class = NewsListLimitOffsetPagination
    filter_backends = [MinBaseFilterBackend, MaxBaseFilterBackend]
#加到最小值，最大值

    def perform_create(self, serializer):
        # 调用save 其先调用creat()
        new_object = serializer.save()
        return new_object

    def get_serializer_class(self):
            return ListUserModelSerializer