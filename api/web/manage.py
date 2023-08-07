import sqlite3

from rest_framework.response import Response
from django.forms import model_to_dict
import json
from rest_framework.views import APIView
from api import models
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
import datetime
from api.views.news import ListNewsModelSerializer
from api.serializer.pages import MaxBaseFilterBackend, MinBaseFilterBackend, NewsListLimitOffsetPagination
from api.serializer.auth import GeneralAuthentication,UserAuthentication
from .web_form.NewsModelForm import AuctionCreateForm, AuctionItemCreateForm
import uuid
# from api import task
from rest_framework import serializers


from django.db.models import F
class AuctionDeleteView(APIView):
    def conn_sqlite(self):
        conn =sqlite3.connect('D:/python_django_virtual/djangoprogram/Scripts/lostandfound/db.sqlite3')
        cur = conn.cursor()
        return conn,cur
    def post(self, request, *args, **kwargs):
        new_id = json.loads(request.body.decode('utf8')).get('newsId')
        print(new_id)
        if not new_id:
            return Response({'status': False, 'message': "请传入有效id"})
        models.News.objects.filter(id=new_id).delete()

        return Response({'status': True, 'message': '删除成功'})

class CreateNewsTopicModelSerializer(serializers.Serializer):  # 序列化
    key = serializers.CharField()
    cos_path = serializers.CharField()
    news_id =serializers.CharField()
class NewsEditView(APIView):
    imageList = CreateNewsTopicModelSerializer(many=True)
    def post(self, request, *args, **kwargs):
        #image_list= CreateNewsModelSerializer()
        new_id = json.loads(request.body.decode('utf8')).get('newsId')
        context = json.loads(request.body.decode('utf8'))
        image_list =context['imageList']
        length = context['length']
        #print(self.kwargs)
        news_object = models.News.objects.filter(id=new_id)
        images_object = models.NewsDetail.objects.filter(news_id=new_id)
        images_object.delete()
        print(image_list[0]['key'])

        #print(context)
        for i in range(length):
            if not list(image_list[i]['key']) is None:
                models.NewsDetail.objects.create(key=image_list[i]['key'],cos_path=image_list[i]['cos_path'],news_id= new_id)
        if not context:
            return Response({'status': False, 'message': "请传入有效id"})
        print(context['content'])
        news_object.update(content=context['content'],topic_id = context['topic_id'],kinds = context['kinds'],address = context['address'],cover = context['cover'])

        return JsonResponse({'status': True, 'message': '修改成功'})
class CommentDeleteView(APIView):
    def post(self, request, *args, **kwargs):
        comment_id = json.loads(request.body.decode('utf8')).get('commentId')
        new_id = json.loads(request.body.decode('utf8')).get('newsId')
        print(comment_id)
        print(new_id)
        if not comment_id:
            return Response({'status': False, 'message': "请传入有效id"})
        models.CommentRecord.objects.filter(id=comment_id).delete()
        count = models.CommentRecord.objects.filter(news_id= new_id).count()
        print(count)
        models.News.objects.filter(id = new_id).update(comment_count = count)
        return Response({'status': True, 'message': '删除成功'})

# class CreateNewsModelSerializer(serializers.ModelSerializer):
#     imageList = CreateNewsTopicModelSerializer(many=True)
#     token = serializers.CharField()
#     topic_id = serializers.CharField()
#     new_id = serializers.CharField()
#     Response(imageList)
#     print(imageList)
#     class Meta:
#         model = models.News
#         # fields = "__all__"
#         exclude = [ 'user','viewer_count', 'comment_count','favor_count']
#     def create(self, validated_data):
#         image_list = validated_data.pop('imageList')##切割newDetail字典数据
#         new_id = validated_data.pop('newId')
#         print(new_id)
#         print(image_list)
#         print(1)
#         #models.News.objects.filter(id=new_id).delete()
#         # 获取用户信息
#         token = validated_data.pop('token')##切割token数据
#         user_object = models.UserInfo.objects.filter(token=token).first()
#         print(token)
#         print(user_object)
#         validated_data['user'] = user_object
#         news_object = models.News.objects.create(**validated_data)##创建news表中数据
#         data_list = models.NewsDetail.objects.filter(news_id=new_id).bulk_create(
#             [models.NewsDetail(**info, news=news_object) for info in image_list]
#         )
#         news_object.imageList = data_list
#         news_object.token = token
#         if news_object.topic:
#             news_object.topic.count += 1
#             news_object.save()
#
#         return news_object
#
# class NewsEditViews(CreateAPIView, ListAPIView):
#     serializer_class = ListNewsModelSerializer
#     queryset = models.News.objects.prefetch_related('user', 'topic').order_by("-id")
#     pagination_class = NewsListLimitOffsetPagination
#     filter_backends = [MinBaseFilterBackend, MaxBaseFilterBackend]
# #加到最小值，最大值
#     def perform_create(self, serializer):
#         # 调用save 其先调用creat()
#         new_object = serializer.save()
#         return new_object
#     def get_serializer_class(self):
#         if self.request.method == 'POST':
#             return CreateNewsModelSerializer