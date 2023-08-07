from django.forms import model_to_dict
from rest_framework import serializers
from rest_framework.filters import BaseFilterBackend
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from api.serializer.pages import MaxBaseFilterBackend, MinBaseFilterBackend, NewsListLimitOffsetPagination,AuctionPagination
from api.serializer.auth import GeneralAuthentication,UserAuthentication
from django.db.models import Max
from api import models
import collections
from django.db.models import F
from api.views.news import  ListNewsModelSerializer,CreateNewsTopicModelSerializer
class NewsListView(CreateAPIView, ListAPIView):
    serializer_class = ListNewsModelSerializer
    queryset = models.News.objects.order_by("-id")
    pagination_class = AuctionPagination
    filter_backends = [MinBaseFilterBackend, MaxBaseFilterBackend]