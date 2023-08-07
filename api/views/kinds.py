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
from api.views.news import  ListNewsModelSerializer,CreateNewsTopicModelSerializer
class KindsNewsView(CreateAPIView, ListAPIView):
    serializer_class = ListNewsModelSerializer
    queryset = models.News.objects.prefetch_related('user', 'topic').order_by("-id")
    pagination_class = NewsListLimitOffsetPagination
    filter_backends = [MinBaseFilterBackend, MaxBaseFilterBackend]
    def get(self,request,*args,**kwargs):
        topic_id = request.META.get('HTTP_AUTHORIZATION', None)
        #user_object= request.META.get('HTTP_AUTHORIZATION', None)
        #user_object = models.UserInfo.objects.filter(token=token).first()
        # 1. 获取这中topic_id的所有发布的新闻
        node_queryset = models.News.objects.filter(topic_id=topic_id).order_by('-id')
        # 2. 序列化
        ser = ListNewsModelSerializer(instance=node_queryset,many=True)
        #print(user_object)
        print(topic_id)
        print(node_queryset)
        return Response(ser.data,status=status.HTTP_200_OK)